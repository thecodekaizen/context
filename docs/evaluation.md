# Evaluation status — post-audit correction

Previous 100% CONTEXT claim precision and PRELUDE sensitivity claims are withdrawn. See docs/audit/04_DATASETS_AND_TEST_RESULTS.md for immutable audit evidence and docs/sprint for new execution results.

Audit raw counts: 82 backend tests passed; six browser tests passed, including a mocked PRELUDE response. Four expected local-corpus sources matched; one weak no-match negative was not truly source-disjoint. The chronology case had no measured edit findings and all claims inconclusive. The primary API completed a real video/search/document/dossier workflow. These establish bounded functionality, not general accuracy.

PRELUDE audit: four attempts, one missed positive, two quiet negatives, one provider 503. The service error must not disappear from the denominator. A later-cutoff sample UI run produced a retrospective cue, not a prospective early warning. Incident times conflict and require independent review.

Post-audit runners write unique run directories, report attempted/completed/unavailable cases and separate measured retrieval from semantic interpretation. The synthetic color-bar negative replaces the full-movie-overlapping-source negative in the development corpus runner. No EVID benchmark performance is claimed. New source-disjoint evaluation must freeze media hashes/labels before inference and report authored versus independent annotations.

Commands:

```sh
PYTHONPATH=backend .venv/bin/pytest -q
npm --prefix web run build
PYTHONPATH=backend .venv/bin/python scripts/run_sprint_evaluation.py --manifest eval/sprint_regression_manifest.json
PYTHONPATH=backend .venv/bin/python scripts/run_prelude_benchmark.py
```

Real model runners use paid configured credentials. Preserve all predictions and failures. Do not equate tests, literal quote matches, bounded citations or a local corpus retrieval hit with model accuracy.
