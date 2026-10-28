# Evaluation — October 29, 2026

Two suites: generated moving-pattern fixtures and a 24-second excerpt of a
licensed animated production, *Big Buck Bunny*. This is a small regression set,
not an accuracy estimate for arbitrary social media footage or human speech.

## Production excerpt

Source window: seconds 40–64 of Blender Foundation's original, locally reset to
0–24. Each test edit is generated independently using FFmpeg. The inference
receives media only, never recipes. The evaluator compares its output to recipes.

| Case | Aligned duration | Findings | Mean accepted timestamp error |
| --- | ---: | --- | ---: |
| Copy/re-encode | 90.6% | None | 0.000 s |
| Omit seconds 8–14 | 87.5% | Omission | 0.000 s |
| Reorder three intervals | 90.6% | Reordering | 0.000 s |
| Repeat first interval | 91.3% | Omission, repetition | 0.000 s |
| Trim at fractional seconds | 90.3% | Two boundary omissions | 0.125 s |
| Heavy compression + downscale | 81.2% | None | 0.000 s |
| Small text-sized opaque overlay | 91.7% | None | 0.000 s |
| Brightness shift | 41.7% | Insufficient evidence | Diagnostic only |
| 10% crop | 39.6% | Insufficient evidence | Diagnostic only |
| 1.25× playback | 0% | Unsupported timing rejected | N/A |
| Unrelated excerpt | 0% | No supported match | N/A |

For the six supported copy/edit/compression cases, all accepted sampled matches
fall within 0.5 seconds of recipe ground truth. Coverage excludes ambiguity and
unsupported timing; it is not an accuracy percentage. The matching score is not
a calibrated probability. The overlay case is a stress test, not a guarantee of
overlay robustness. Machine-readable results: [evaluation.json](evaluation.json).

## Defects found and corrected

The initial engine inferred omissions from any uncovered source range. On this
production clip, ambiguous near-static frames caused false omissions even in a
copy. Version 2 requires an observed cut or an aligned boundary, subtracts source
material used elsewhere, and withholds claims where unresolved footage could
account for the gap. Possible coverage never becomes a confirmed match.

The initial engine also allowed speed changes to fragment into apparent 1×
matches. Sustained non-unit correspondence rates now invalidate those mapping
windows. Both defects have generated-fixture and optional production regression
tests. Speed-change support remains intentionally unresolved, not implemented.

## Reproduce

```sh
PYTHONPATH=backend .venv/bin/python scripts/evaluate.py --download
.venv/bin/pytest -q
```

The download is approximately 65 MB, stored under ignored `data/evaluation`.
Without it, production-footage tests skip; generated tests still run offline.
`docs/evaluation.json` records the source hash and exact window. No API key or
Meta request is required for this alignment evaluation.

## Attribution

*Big Buck Bunny* (2008), (c) copyright 2008, Blender Foundation /
www.bigbuckbunny.org. Licensed under Creative Commons Attribution 3.0.
Excerpt trimmed, transcoded and edited solely for these evaluations.

- License and attribution: https://peach.blender.org/about/
- Official download page: https://peach.blender.org/download/
- Archive: https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_320x180.mp4.zip
