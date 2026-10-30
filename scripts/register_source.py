"""Register an admitted technical recording as a searchable candidate."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from context_core.source_catalog import register


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument(
        "--license",
        required=True,
        help="Document the license or permission; do not infer it from the hostname",
    )
    parser.add_argument("--tag", action="append", default=[])
    args = parser.parse_args()
    record = register(
        args.media,
        title=args.title,
        origin_url=args.source_url,
        license=args.license,
        tags=args.tag,
    )
    print(json.dumps(record.model_dump(), indent=2))


if __name__ == "__main__":
    main()
