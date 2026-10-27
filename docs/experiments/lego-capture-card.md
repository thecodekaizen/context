# SHOWME LEGO capture card

Use this after choosing a small set with a short, visibly constrained assembly. The clips test whether one reviewed demonstration can support a separate correct attempt, a deliberate mistake, and a recovery. They are not just demo footage.

## Before recording

- Keep the task to one small assembly with about 4–6 distinct pieces and one visible ordering or orientation rule.
- Prefer hands and work surface only. Keep every piece and the connection area in frame; use a stable overhead or shallow-angle view with even light.
- Record landscape at the phone's normal 1080p setting. Keep the camera position, zoom, lighting, and table fixed for the baseline.
- Say what each piece is and why the constrained step matters during the expert recording. Narration helps, but the visual change should still be inspectable.
- Record short, continuous clips. Do not edit out the mistake, correction, or transitions between states.
- Do not upload anything yet. Keep the answer key separate from the clips and from model prompts.

## Four clips to capture

Use neutral filenames (`clip-a.mp4` through `clip-d.mp4`) so the condition is not leaked by the filename.

| Clip | What to record | Purpose |
|---|---|---|
| A | Demonstrate the complete task once, slowly, naming pieces and explaining the important rule. | Teach proposes the Skill Model from one example. |
| B | Reset all pieces, move them to different positions on the same table, then complete the task correctly. | Check transfer beyond replaying the expert's hand or object coordinates. |
| C | Reset again and make one deliberate, visible, recoverable mistake related to the rule. Stop with the mistaken state visible for several seconds. | Test whether Do notices the real divergence and cites visual evidence. |
| D | Start from the exact mistaken state left at the end of C; correct it and finish the task. | Test whether Do recognizes recovery rather than merely seeing a later completed object. |

If the phone changes angle between clips B/C/D, keep that as a separate robustness trial. First get a fixed-camera baseline; then we can test viewpoint change deliberately.

## Keep the answer key separate

Before looking at any model output, write down locally:

1. The intended completed configuration.
2. The visible rule that makes the chosen wrong state incorrect.
3. The first time the wrong state is visibly established in C.
4. The recovery action and first time the corrected state is visible in D.
5. Any ambiguity, occlusion, or valid alternate assembly order.

These notes are ground truth for evaluation. Keep them in a separate local file; never include them in the prompt, filenames, or upload sent to Muse. We will compare model timestamps and claims against the key only after the inference outputs are saved.

## What to send back

When ready, attach the four raw clips here and tell me which file is A, B, C, and D. Also provide the separate answer-key notes in chat after the clips are attached; I will keep them out of model inputs. We will inspect duration, framing, and whether the rule is actually visible before spending API credits.

No clip needs to be added to Git. SHOWME should keep recordings and raw inference artifacts outside the public repository unless you explicitly decide otherwise.
