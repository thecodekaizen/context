#!/usr/bin/env python3
"""Run the preregistered raw-only Neighborhood Atlas Muse experiment."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "datasets/synthetic/experiments/neighborhood-atlas"
OUTPUT_ROOT = ROOT / ".thread-experiment-runs/neighborhood-atlas"
MODEL = "muse-spark-1.3"
MAX_OUTPUT_TOKENS = 4096
PROMPT = (
    "Review this dated archive of one creative project. Identify any meaningful evolution "
    "in the project's focus over time. If the evidence is insufficient, say so. Separate "
    "direct observations from your interpretation. Cite artifact IDs and dates for each "
    "part of your interpretation. Include evidence that complicates your interpretation. "
    "Do not infer the creator's personality or invent causes. Return concise JSON with keys "
    "`observations`, `candidate_finding`, `supporting_artifacts`, `complicating_artifacts`, "
    "and `limitations`. Use an empty `candidate_finding` when no evolution is established."
)
ALLOWED_TOP_KEYS = {"project", "artifacts"}
ALLOWED_PROJECT_KEYS = {"id", "title"}
ALLOWED_ARTIFACT_KEYS = {"id", "date", "modality", "title", "content"}


def load_raw_archive(filename: str) -> dict[str, object]:
    path = FIXTURES / filename
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"schema_version", "project", "artifacts"}:
        raise ValueError(f"{filename}: unexpected raw-fixture structure")
    if data["schema_version"] != 1:
        raise ValueError(f"{filename}: unsupported schema version")
    project = data["project"]
    artifacts = data["artifacts"]
    if not isinstance(project, dict) or set(project) != ALLOWED_PROJECT_KEYS:
        raise ValueError(f"{filename}: project must contain only id and title")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError(f"{filename}: artifacts must be a non-empty list")

    seen: set[str] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict) or set(artifact) != ALLOWED_ARTIFACT_KEYS:
            raise ValueError(f"{filename}: each artifact must contain only raw source fields")
        artifact_id = artifact["id"]
        if not isinstance(artifact_id, str) or artifact_id in seen:
            raise ValueError(f"{filename}: artifact IDs must be unique strings")
        seen.add(artifact_id)
        if not all(isinstance(artifact[k], str) and artifact[k] for k in ALLOWED_ARTIFACT_KEYS):
            raise ValueError(f"{filename}: all raw artifact fields must be non-empty strings")

    # The request contains only the explicitly allowed project and raw artifact fields;
    # schema metadata never enters model context.
    return {"project": project, "artifacts": artifacts}


def make_request(archive: dict[str, object]) -> dict[str, object]:
    archive_json = json.dumps(archive, ensure_ascii=False, indent=2)
    return {
        "model": MODEL,
        "reasoning": {"effort": "high"},
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "input": f"{PROMPT}\n\nDated archive (raw source artifacts):\n{archive_json}",
    }


def load_api_key() -> str | None:
    """Read the key from the environment or the local, git-ignored .env file."""
    key = os.environ.get("MODEL_API_KEY")
    if key:
        return key
    env_file = ROOT / ".env"
    if not env_file.exists():
        return None
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == "MODEL_API_KEY":
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]
            return value or None
    return None


def run_case(client: object, label: str, filename: str, run_dir: Path) -> None:
    archive = load_raw_archive(filename)
    request = make_request(archive)
    serialized_request = json.dumps(request, ensure_ascii=False, indent=2)
    input_hash = hashlib.sha256(serialized_request.encode("utf-8")).hexdigest()
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / f"{label}-request.json").write_text(serialized_request + "\n", encoding="utf-8")

    response = client.responses.create(**request)  # type: ignore[attr-defined]
    payload = response.model_dump(mode="json")
    (run_dir / f"{label}-response.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    usage = getattr(response, "usage", None)
    print(json.dumps({
        "case": label,
        "model": getattr(response, "model", MODEL),
        "input_sha256": input_hash,
        "output_text": getattr(response, "output_text", ""),
        "usage": usage.model_dump(mode="json") if usage is not None else None,
        "saved_to": str(run_dir),
    }, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("complete", "ablation", "all"), default="all")
    args = parser.parse_args()
    api_key = load_api_key()
    if not api_key:
        print("Set MODEL_API_KEY in the local .env file or shell before running this experiment.", file=sys.stderr)
        return 2

    try:
        from openai import OpenAI
    except ImportError:
        print("Install the optional Meta client in backend: pip install -e '.[meta]'", file=sys.stderr)
        return 2

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = OUTPUT_ROOT / timestamp
    client = OpenAI(api_key=api_key, base_url="https://api.meta.ai/v1")
    cases = []
    if args.case in ("complete", "all"):
        cases.append(("complete", "raw.json"))
    if args.case in ("ablation", "all"):
        cases.append(("ablation", "ablation-no-story-evidence.json"))

    try:
        for label, filename in cases:
            run_case(client, label, filename, run_dir)
    except Exception as exc:  # Do not print request headers or environment values.
        print(f"Experiment call failed ({type(exc).__name__}); inspect the local run record and API dashboard.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
