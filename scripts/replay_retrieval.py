"""Replay a failed dossier's real search receipts through corrected selection.

The old dossier and raw receipts remain intact. Only source inspection and the
source-constrained verification request run again, without a supplied original.
"""

import asyncio
import json
import shutil
import sys
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from context_core.dossier import (
    SEARCH_MODEL,
    model_request,
    text_output,
    validate_assessment,
    verification_prompt,
    write,
)
from context_core.retrieval import inspect_source, search_receipts, select_sources


async def main(identifier):
    load_dotenv(ROOT / ".env")
    old = ROOT / "data" / identifier
    previous = json.loads((old / "dossier.json").read_text())
    target = ROOT / "data" / uuid4().hex
    target.mkdir()
    for file in old.iterdir():
        if file.is_file() and (
            file.suffix in {".mp4", ".jpg"}
            or file.name in {"observation-response.json", "search-response.json"}
        ):
            shutil.copyfile(file, target / file.name)
    data = json.loads(
        json.dumps(previous).replace(
            f"/api/dossiers/{identifier}/", f"/api/dossiers/{target.name}/"
        )
    )
    data.update(id=target.name, status="running", stage="retrieving", sources=[])
    data.pop("assessment", None)
    data["retrieval_replay"] = {
        "previous_dossier_id": identifier,
        "observation_and_search_receipts_reused": True,
        "original_video_supplied": False,
    }
    write(target, data)
    print("Replay dossier:", target.name, flush=True)
    candidates, searched = search_receipts(
        json.loads((target / "search-response.json").read_text())
    )
    selected = select_sources(candidates, data["analysis"]["search_queries"])
    (target / "search-candidates.json").write_text(json.dumps(candidates, indent=2))
    data["retrieval"].update(
        provider_search_performed=searched,
        candidate_count=len(candidates),
        selected_count=len(selected),
        selection_method="Inspectable documents, provider citations, institutional origin, query relevance",
    )
    sources = await asyncio.gather(*(inspect_source(source) for source in selected))
    for index, source in enumerate(sources):
        source["id"] = f"source-{index}"
    data.update(sources=sources, stage="verifying")
    write(target, data)
    accessible = [
        {key: source[key] for key in ("id", "url", "title", "text")}
        for source in sources
        if source["fetch_status"] == "fetched"
    ]
    print("Fetched:", json.dumps([s["url"] for s in accessible]), flush=True)
    if not accessible:
        raise ValueError(
            "No accessible source; preserve failed replay instead of inventing a verdict"
        )
    response = await model_request(
        verification_prompt(data["analysis"], accessible), model=SEARCH_MODEL
    )
    (target / "verification-response.json").write_text(json.dumps(response, indent=2))
    data.update(
        assessment=validate_assessment(
            text_output(response), data["analysis"], sources
        ),
        status="complete",
        stage="complete",
    )
    write(target, data)
    (ROOT / "data/gate-v2/retrieval-replay-job.json").write_text(
        json.dumps({"id": target.name}, indent=2)
    )
    print(json.dumps({"id": target.name, "assessment": data["assessment"]}), flush=True)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
