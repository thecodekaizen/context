"""Record a local operator's content review for exact media bytes.

This is an operator trust boundary, not automatic classification or signing.
Do not approve footage based only on its title, filename, caption or uploader.
"""

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from context_core import domain_policy
from context_core.domain_policy import DomainReview, ExclusionChecks, evaluate_domain
from context_core.media import digest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path)
    parser.add_argument(
        "--category",
        required=True,
        choices=[*sorted(domain_policy.ALLOWED_CATEGORIES), "other", "unknown"],
    )
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--rationale", required=True)
    parser.add_argument(
        "--excluded", action="append", choices=domain_policy.EXCLUSIONS, default=[]
    )
    parser.add_argument(
        "--reviewed-entire-file",
        action="store_true",
        help="Confirm the named operator reviewed the complete footage, including its soundtrack and peripheral text",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Explicitly replace an existing review of these exact bytes",
    )
    args = parser.parse_args(argv)
    if not args.reviewed_entire_file:
        parser.error(
            "Record an actual full-file operator review with --reviewed-entire-file; a category declaration alone is insufficient"
        )
    if not args.reviewer.strip() or not args.rationale.strip():
        parser.error("Reviewer and rationale must be non-empty")
    sha256 = digest(args.media)
    review = DomainReview(
        sha256=sha256,
        category=args.category,
        exclusions=ExclusionChecks(
            **{name: name in args.excluded for name in domain_policy.EXCLUSIONS}
        ),
        basis="operator_review",
        reviewer=args.reviewer,
        rationale=args.rationale,
        reviewed_at=datetime.now(UTC),
    )
    target = domain_policy.REVIEW_ROOT / f"{sha256}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not args.replace:
        parser.error(
            "A review exists; inspect it and use --replace only for an intentional revision"
        )
    if args.replace:
        # Preserve the prior receipt before explicitly replacing a decision.
        history = target.parent / "history"
        history.mkdir(exist_ok=True)
        if target.exists():
            old_hash = digest(target)
            (history / f"{sha256}-{old_hash}.json").write_bytes(target.read_bytes())
        temporary = target.with_suffix(".tmp")
        temporary.write_text(review.model_dump_json(indent=2))
        temporary.replace(target)
    else:
        with target.open("x") as output:
            output.write(review.model_dump_json(indent=2))
    print(evaluate_domain(sha256, review).model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
