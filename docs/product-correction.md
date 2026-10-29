# Product recovery: one-input investigation

## Gap
The existing app asks for an original or an indexed source. Its central data
model is an alignment report, not an investigation. It cannot extract standalone
video claims, retrieve external evidence or distinguish event facts from provenance.

## Reuse
FFmpeg probing/decoding, hashes, compatible playback, timestamps, evidence storage,
Meta transport, citation validation, dual players and conservative alignment.
No repository restart. Comparator remains available as a specialized drill-down.

## Implementation order
1. Single video upload or explicitly supported direct-media URL; optional caption.
2. Meta video/audio observations, factual claims and search queries with timestamps.
3. Real search-grounded retrieval; preserve provider search receipts and sources.
4. Fetch accessible source text, retain hashes/excerpts, reject invented citations.
5. A dossier: overview, origin, claims, manipulation, source graph and timeline.
6. Independent real-footage proof with opaque upload name and no supplied original.
7. Expand cases and compare evidence-grounded reasoning with a no-retrieval baseline.

## Honesty boundaries
Observations are model claims with checked timestamp bounds. Search hits are not
verified originals. HTTP-fetched pages are not automatically true. A source can
support a fact about an event without proving the uploaded video's identity.
No unsupported synthetic-video score, deceptive-edit verdict, or missing-original
accusation. A source/video mismatch and an inconclusive result must remain visible.

## Competitive context
InVID-WeVerify already offers keyframe extraction, reverse-search and forensic
assistance: https://www.invid-project.eu/tools-and-services/invid-verification-plugin/
EVID-Bench already evaluates search-grounded video misinformation reasoning:
https://arxiv.org/abs/2606.04098 and https://github.com/yutao1024/EVID-Bench

We claim no invention of video verification. Our hypothesis is that a single-input,
source-linked dossier can reduce investigation effort and expose unsupported model
claims more effectively than disconnected tools. Measure source relevance,
claim-verdict correctness, evidence entailment, timestamp validity, false accusations
on harmless edits and time-to-inspect. No improvement is established yet.
