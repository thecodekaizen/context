"""Run a single admitted clip against the registered catalog, without source labels."""

import argparse
import asyncio
import json
import os
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from context_core.domain_policy import require_files
from context_core.dossier import investigate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--caption", default="")
    parser.add_argument(
        "--with-meta",
        action="store_true",
        help="Use configured Meta credentials for grounded excerpts only",
    )
    args = parser.parse_args()
    require_files({"submitted": args.video})
    if args.with_meta:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env")
    else:
        os.environ.pop("MODEL_API_KEY", None)
    identifier = (
        f"technical-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:6]}"
    )
    directory = ROOT / "data" / identifier
    directory.mkdir()
    shutil.copyfile(args.video, directory / "video.mp4")
    report = asyncio.run(investigate(directory, args.caption))
    summary = {
        "id": identifier,
        "status": report["status"],
        "pipeline": report["pipeline"],
        "input_sha256": report["domain_admission"]["submitted"]["sha256"],
        "source_name": report.get("matched_source", {}).get("source_name"),
        "source_id": report.get("matched_source", {}).get("source_id"),
        "source_selection": report.get("source_video_retrieval", {}).get("status"),
        "omission_evidence": report.get("omission_evidence"),
        "meta_requested": args.with_meta,
        "reviews": [
            {
                "status": r["status"],
                "model": r.get("model"),
                "classification": r.get("interpretation", {}).get("classification"),
                "error": r.get("error"),
                "elapsed_seconds": r.get("elapsed_seconds"),
                "usage": r.get("usage"),
            }
            for r in report.get("comparison", {}).get("reviews", [])
        ],
        "failure_log": report["failure_log"],
        "dossier": str(directory / "dossier.json"),
        "scope": "Single-clip lookup within a registered reviewed catalog/local collection, not internet-wide source discovery or independent semantic accuracy evaluation.",
    }
    (directory / "run-summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 1 if report["status"] == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
