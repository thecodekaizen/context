# CONTEXT model and capability card

Updated October 30, 2026. Current integration claims supersede earlier broad SAM
and cosine-alignment descriptions. See [hero-validation.md](hero-validation.md)
for recorded runs, failures and exact scope.

## Deterministic evidence

The visual matcher samples spatial color features at 4 Hz and uses mean absolute
feature distance (`spatial-color-sequence-v2`); it is not a cosine matcher.
Acoustic normalized correlation is an independent lane. Crop geometry uses
OpenCV template matching. No-match is an abstention, not evidence of fidelity.

## Muse Spark 1.2

Only verified internal omission intervals may trigger review. The pack contains
at most two clips, each capped at 30 s and 8 MiB, and three timed JPEGs per clip
fitted to 1280×720, capped at 1 MiB each. JPEGs derive from the same bounded
windows and preserve readable UI text. Hashes, clip-local and media times are
recorded. Changed frame bytes and invalid timestamps are rejected before dispatch.

Outputs separate observations, possible effect, classification and uncertainty.
Responses are checked for referenced clip IDs and time bounds only; this is not
a check of the truth of observations or causal effect. Sparse images cannot establish absence throughout
an entire video. A non-inconclusive classification needs references to both media.
Model statements remain separate from measured evidence.

In the authored cache case, the original video-only pack returned `harmless_edit`
and missed the visible qualification. The revised pack read it and described its
possible effect but returned `inconclusive`. Both runs are retained. The retained
Muse response is a saved recording (`eval/hero-v1/muse/response.json`), not
re-run. This is one exploratory comparison, not independent semantic accuracy
validation.

## SAM 3.1 (experimental)

The operational crop overlay is geometric; SAM masks are not integrated into it.
A separate frozen chart-bar segmentation experiment passes 10/10 on replay of
saved API events. It does not establish disclaimer recognition or temporal tracking.

A fresh live test on the authored cache conditions panel returned zero masks and
failed the predeclared recall/IoU thresholds. The failure and replay are retained.
Do not attribute the live margin overlay to SAM or claim proven disclaimer tracking.

## Limits

Only reviewed developer tutorials, software benchmarks and product demos are
admitted. Byte-bound local reviews are operator trust records, not signed identity
or automatic content classification. Source discovery is limited to a registered
catalog/local collection. Evaluation results are scripted cuts of authored recordings
and do not establish performance on natural footage. Repetitive or static scenes
have not been evaluated and no result is claimed for them.
