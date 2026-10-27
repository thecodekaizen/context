# LEGO proof-of-magic recording guide

Use this guide when the set arrives. The exact procedure and deliberate mistake are **not selected yet**: inspect the pieces first, then choose one small, safe sequence with a visible, recoverable error. Do not force the washer/bracket example if the LEGO set does not naturally support it.

## What we need to learn

Can SHOWME learn a candidate process from one demonstration, accept a separate correct attempt, identify a visible divergence, and recognize recovery? The four clips below form one matched experiment. Stock footage can smoke-test the pipeline, but it cannot substitute for this controlled set.

## Before recording

1. Pick a task with 3–5 distinct pieces and 3–5 meaningful actions. Prefer a visible ordering or orientation constraint and one easy-to-see mistake that can be corrected safely.
2. Write the expected successful sequence and the planned mistake in a separate private answer key **before** running inference. Keep that file out of the repository and out of all model inputs.
3. Put the camera in a fixed overhead or oblique position. Keep the entire work area, pieces, and hands visible; use steady light and a plain surface.
4. Record uninterrupted clips, roughly 15–45 seconds each. Avoid cuts, zooms, face capture, private information, and moving the camera. Keep the same framing for all four baseline clips.
5. Reset the pieces between attempts. Move their starting positions slightly for the correct attempt so the system cannot pass by matching screen coordinates.

Do not change camera angle for the baseline. Viewpoint robustness is a later experiment after the fixed-view test works.

## The four clips

| Clip | What to record | Keep from the model |
|---|---|---|
| A — Demonstration | Perform the chosen task once, cleanly and at a natural pace. Optional: narrate what you are doing. | This is the only clip used to learn the initial candidate Skill Model. |
| B — Correct attempt | Reset and perform the same task correctly. Slightly reposition the loose pieces; keep the camera fixed. | Do not tell the model this is the correct control. |
| C — Divergence | Reset and perform the task with exactly one deliberate, visible, recoverable mistake. Continue briefly so the resulting state can be seen. | Do not name or describe the mistake in the filename, prompt, or recording. |
| D — Recovery | Start from the same incorrect partial state reached in C, correct it, and finish the task. | Do not tell the model this is the recovery clip. |

The error must be observable in the final arrangement or a clear action/state transition. Avoid hidden placements, tiny details, or multiple simultaneous mistakes. If the camera cannot show the decisive evidence, change the setup or task before recording the evaluation set.

## Capture and inference workflow

- Use **Teach → Record** (or upload) for A, save a local copy, inspect the preview, then explicitly choose **Learn this skill** when ready.
- The current recorder captures video only. Do not rely on spoken narration: the present P0 video preparation strips audio. If a spoken instruction matters, note it separately for a later voice-evidence experiment.
- After reviewing the candidate Skill Model from A, use **Do → Record** (or upload) to inspect B, C, and D as separate attempts. **Observe attempt** makes a model request; wait until the clips are ready before selecting it.
- The experiment CLI can also prepare and run individual local clips. Preserve the model output and evidence timestamps for review.
- Do not send the human answer key or condition-revealing labels with any request. Review each result against the private key only after the model response is saved.

Keep original recordings local and private by default. Do not commit raw clips, personal footage, API keys, or the answer key to the public repository. If a small rights-cleared fixture is ever proposed for publication, verify its license and obtain explicit user approval first.

## Private answer-key checklist

For each attempt, record outside the repo:

- neutral clip identifier;
- expected visible objects and final arrangement;
- meaningful action/state intervals (`start_seconds`, `end_seconds`);
- for C, the actual divergence and the first interval where it is visibly established;
- for D, when recovery becomes visible and what valid state is restored;
- any occlusion or ambiguity that should lower the score.

This ground truth is for evaluation only. The model sees raw video and, for B/C/D, the candidate Skill Model learned from A—not these labels.

## Pass criteria

- B: accepts the visibly correct attempt without inventing a problem.
- C: names the actual divergence and cites inspectable visual/time evidence.
- D: recognizes the correction and valid recovered state.
- Claims unsupported by a visible frame or interval count as ungrounded. Report misses and false alarms; do not repair outputs manually before scoring.

One successful run is a useful prototype result, not broad proof. Repeat the set before making a reliability claim.
