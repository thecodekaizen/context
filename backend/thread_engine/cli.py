"""Command-line entry point for the deterministic discovery baseline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .contracts import Memory


def load_dataset(path: Path) -> tuple[str, str, list[Memory]]:
    try:
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read dataset {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc

    if data.get("schema_version") != 1:
        raise ValueError("dataset must declare schema_version: 1")
    project = data.get("project")
    if not isinstance(project, dict) or not project.get("id") or not project.get("title"):
        raise ValueError("dataset must include project.id and project.title")
    raw_memories = data.get("memories")
    if not isinstance(raw_memories, list):
        raise ValueError("dataset 'memories' must be a list")

    memories = [Memory.from_dict(item) for item in raw_memories]
    source_ids = [memory.source_id for memory in memories]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("each memory must refer to a distinct source_id in this baseline")
    return str(project["id"]), str(project["title"]), memories


def _render_text(result: dict[str, Any]) -> str:
    lines = [
        f"{result['project_title']} · {result['start_date']} → {result['end_date']}",
        f"Theme extraction: {result['extraction_provider']}"
        + (f" ({result['extraction_model']})" if result.get("extraction_model") else ""),
        "",
        result["hypothesis"],
        "",
        "Supporting evidence:",
    ]
    for item in result["supporting_evidence"]:
        lines.append(f"  + {item['date']} · {item['title']} [{item['source_id']}] — {item['summary']}")
    lines.append("\nCounter-evidence:")
    if result["counter_evidence"]:
        for item in result["counter_evidence"]:
            lines.append(f"  ! {item['date']} · {item['title']} [{item['source_id']}] — {item['summary']}")
    else:
        lines.append("  None found in this fixture.")
    lines.append("\nUncertainty:")
    lines.extend(f"  ? {item}" for item in result["uncertainty"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover one evidence-backed evolution in a creative project.")
    parser.add_argument(
        "dataset",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "datasets" / "synthetic" / "creative-evolution.json",
        help="path to a schema_version 1 JSON dataset",
    )
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument("--provider", choices=("fixture", "meta"), default="fixture", help="theme extraction source")
    args = parser.parse_args()

    try:
        from .service import discover_dataset

        result = discover_dataset(dataset_path=args.dataset, provider_name=args.provider)
    except ValueError as exc:
        if str(exc).startswith("No sufficiently supported evolution finding"):
            print("No sufficiently supported evolution finding in this dataset.")
            return 0
        print(f"thread-discover: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"thread-discover: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(_render_text(result))
        if (usage := result.get("api_usage")) is not None:
            print(
                "\nAPI usage this run: "
                f"{usage['requests']} requests, {usage['cache_hits']} cache hits, "
                f"estimated ${usage['estimated_usd']:.6f}; "
                f"cumulative local estimate ${usage['cumulative_estimated_usd']:.6f}."
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
