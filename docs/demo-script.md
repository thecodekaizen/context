# CONTEXT demo script — evidence-aligned draft

Updated October 31, 2026. Aligned with the Pre-Publication QA workflow and the
exact Python cache qualification hero clip (4-second omission: 00:06.000–00:10.000).

Three minutes is our editorial target, not a verified portal requirement. Record
in the builder's own voice on Monday, leaving Tuesday for retakes and final render.
Timing is a storyboard budget; narration duration has not been measured.

## Pre-Publication QA demonstrable story

- **The Problem:** An editor cuts a 18-second benchmark demo down to 14 seconds to hit
  a runtime target. In doing so, the editor trimmed seconds 6–10, unaware that the
  side conditions panel displayed "WARM CACHE ONLY" and "COLD-START SETUP IS EXCLUDED"
  during those four seconds.
- **The Audit:** The engineering lead or reviewer drops both versions into CONTEXT.
- **The Discovery:** CONTEXT pinpoints the 4-second cut, locks the dual player, and
  Meta Muse Spark 1.2 reads the excised qualification text. The team catches the
  unintended omission before publishing.
- **The Boundaries:** Real-world noise differs from scripted edits; 0/18 benign controls
  gives a 95% upper bound of about 16.7% on a scripted set (rule of three). The Muse
  response is a saved recording. SAM 3.1 is experimental (chart bars only).

| Time | Screen action | Draft builder narration |
|---|---|---|
| 0:00–0:25 | Edited highlight, then recovered source interval | “Before publishing a benchmark demo or technical highlight, how does an engineering team verify what the video edit cut out? An editor tightening a recording might trim four seconds to hit a runtime target without realizing those seconds carried an essential caveat. CONTEXT finds the excised interval and lets your team inspect the evidence before you publish.” |
| 0:25–0:55 | Pre-publication intake and deterministic trace | “Here is the workflow. The reviewer submits the cut highlight alongside the raw recording. CONTEXT matches the soundtracks by acoustic cross-correlation—no model guessing—and flags the exact four-second omission from seconds six to ten. Visual matching alone was not enough on this clip.” |
| 0:55–1:50 | Synchronized dual-player, 'WARM CACHE' reveal, Muse review | “Notice our synchronized dual player: scrubbing the edit drives the raw source in lockstep. When we click the omission card, the source exposes the excised footage. And here is the discovery: during those four missing seconds, the source displayed 'WARM CACHE ONLY' and 'COLD-START SETUP IS EXCLUDED'—which do not appear in the edited sample frames. A saved response from Meta Muse Spark 1.2 reads the qualification text and explains its potential interpretive impact, while honestly reporting inconclusive on whether meaning changed throughout the clip. The team catches the unintended omission before publishing.” |
| 1:50–2:20 | Cache crop calipers, then separately labeled SAM experiment | “Spatial changes are audited separately. When a widescreen recording is reframed, OpenCV geometry measures the exact retained box—here, 25% of the frame was cropped out, removing the entire right-side conditions panel. Separately, we evaluated Meta SAM 3.1: it passed a replay on ten frozen chart-bar crops, but returned zero masks on the live conditions panel. So the live margin overlay is strictly geometric evidence, not an AI claim.” |
| 2:20–2:45 | Evaluation matrix with scripted-case scope visible | “Every metric is evaluated on a frozen contract: thirty scripted FFmpeg scenarios across three benchmark sources. It recovered all fifteen labeled omission intervals across twelve positive cases with zero boundary error, and produced zero false alarms across eighteen benign controls—a 95% upper bound under 17% on a scripted set, by the rule of three.” |
| 2:45–3:00 | Limits and model attribution | “Here is where the evidence stops: scripted cuts of authored clips, a saved Muse response, and SAM as an experiment. Deterministic evidence first, bounded model review second, and honest limits throughout.” |

## Recording acceptance

- Re-run the selected case and show actual output; label saved replay as replay.
- Keep controlled-fixture and synthetic-soundtrack disclosures visible.
- The cut is four seconds (00:06.000–00:10.000); do not say five seconds.
- Do not replace “inconclusive” with a scripted changed-meaning verdict.
- Do not call geometric margin shading a SAM mask.
- Do not claim zero hallucinations, universal recall, proven intent, or verified semantic judgment.
