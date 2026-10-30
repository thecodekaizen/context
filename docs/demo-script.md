# CONTEXT demo script: Pre-Publication QA

Voiceover for a human narrator. Narration is 264 words (limit 310); word counts are in each heading.
Every number comes from `eval/hero-v1/results.json` or `eval/execution-v1/full-results/results.json`.

**Always on screen (corner badge):** "Controlled, authored case · Saved Muse response · Eval = scripted cuts". SAM 3.1 is not featured.

## 0:00–0:20 | The reveal (33 words)
**On screen:** Two timelines: "Edited highlight 14 s", "Raw recording 18 s". A question mark over the gap.

> The edited highlight runs fourteen seconds. The raw recording runs eighteen. What is missing? A team about to publish a benchmark demo needs that answer first, so it checks what the edit removed.

## 0:20–0:50 | Find the cut (43 words)
**On screen:** Both files go in. An orange block appears from 6.0 to 10.0 s.

> CONTEXT lines the two recordings up and finds a gap: four seconds, from six to ten. It found the cut by matching the audio. Matching the picture alone wasn't enough on this clip. The boundary error against the known cut is zero seconds.

## 0:50–1:30 | See what was removed (42 words)
**On screen:** Dual player locked. Click the finding; source plays 6–10 s with the full conditions panel: "WARM CACHE ONLY", "COLD-START SETUP IS EXCLUDED", "Cold setup: 0.83 ms". Then the edit's sampled frames, showing only a shorter conditions panel.

> Both players move together. Click the finding, and the raw recording plays the missing four seconds. On screen there: warm cache only, cold-start setup excluded, cold setup zero point eight three milliseconds. The edit's sampled frames show only a shorter conditions panel.

## 1:30–2:00 | Muse reads it, the human decides (59 words)
**On screen:** Muse panel labeled "Saved response, not re-run": observation, possible effect, classification **inconclusive**. Then a reviewer-decision row.

> Meta's Muse Spark 1.2 reads the frames in that matched interval. Alignment and crop measurement are deterministic. Muse tied the removed seconds to the warm-cache-only limit. If that qualification is missing, it says the zero point zero zero nine microsecond figure could read as a general, end-to-end speedup. It reports inconclusive. Saved response, not run live. The human decides.

## 2:00–2:25 | The crop (33 words)
**On screen:** Calipers: 1280×720 source, 960×720 retained, right margin shaded. "25% of frame removed · OpenCV geometry".

> The edit also cropped the frame, from twelve eighty by seven twenty to nine sixty by seven twenty. That's a quarter of the picture, removed from the right side, measured with OpenCV geometry.

## 2:25–2:50 | How far to trust it (39 words)
**On screen:** Table: 30 scripted cuts, 12 with omissions, 15/15 intervals recovered, 0.0 s boundary error, 0/18 benign controls flagged. Banner: "Scripted cuts of authored recordings. Not field footage." Footnotes: "Hero clip: visual matching alone returned insufficient_evidence; the cut was found by audio." "SAM 3.1: experimental, not featured."

> On a frozen set of thirty scripted edits, it found all fifteen removed intervals, with zero seconds of boundary error. It raised no alarm on eighteen harmless edits. These are scripted cuts of recordings we authored, not field footage.

## 2:50–3:00 | Close (15 words)
**On screen:** Text card: "The team decides before publishing."

> CONTEXT doesn't judge the cut. It shows the evidence, so the team decides before publishing.

---

## Recording notes
- The cut is four seconds (6.0–10.0 s). Never say five.
- Say "evidence". Do not say "proof", "verdict", or "forensic".
- Label the Muse panel "saved response" at all times. Do not replace "inconclusive".
- Do not call the crop overlay a SAM mask. SAM does not appear in the video.
- Make no claim about natural footage, intent, or the model's accuracy.
