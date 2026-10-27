# SHOWME Lego Teach Smoke Test — Preregistration

**Registered:** 2026-10-27, before the Muse inference call  
**Purpose:** Test the Teach stage only: can Muse Spark turn one complete, user-recorded physical assembly demonstration into a concise, evidence-linked candidate process?

## Scope and claim

The input is one continuous overhead recording of the user building a small Lego Star Wars TIE Advanced set from loose pieces. The video is approximately 15 minutes long. This is a Teach smoke test, not a test of learner mistake detection, recovery, live guidance, or generalization to other tasks.

The claim under test is limited to: **from this recording, the model can describe several visible phases of the build in chronological order and attach evidence intervals that point to those phases.** One demonstration cannot show that any observed order is required.

## Input and isolation

- Use the complete, silent, locally downscaled copy of the user-provided recording as the sole model media input.
- No expected process, step labels, error labels, or evaluation notes are sent to Muse.
- The instruction booklet is visible in the recording. Its presence is part of the test input; therefore success does not establish that the model learned solely from hand-object interactions.
- Keep the original recording, compressed copy, sampled frames, API response, and run artifacts local and out of Git.
- Request one inference only. Automatic retries are disabled. The adapter requests remote file expiry and attempts deletion after the call.

## Human-authored expected landmarks

Before model output is inspected, local frame samples from the video show these broad visual phases. The windows are deliberately broad because sparse checkpoints cannot establish exact action boundaries:

| Approximate window | Expected visible landmark |
|---|---|
| 0:00–2:30 | Loose pieces are selected and a small light-gray central subassembly begins to form. |
| 2:30–7:30 | The light-gray central subassembly is handled and extended with additional pieces. |
| 7:30–12:30 | Dark/black elongated or panel-like subassemblies are built alongside the gray core. |
| 12:30–15:23 | Separate dark pieces are brought together with the central assembly; the final visible state is a more integrated model. |

These are appearance-based landmarks, not a canonical Lego instruction sequence. Do not score exact part names unless visually supported. Do not treat the booklet's numbered order as proof of physical necessity.

## Decisive evidence

The local 24-frame sample manifest is the fixed human-review set for this smoke test. Its source digest is `621b60288411f9a8f44c7da2906710ffa90035e7e258e79783d845a9b435416d`; samples are spaced approximately 38.442 seconds apart across the 922.6-second clip. The complete video, not just these stills, is supplied to Muse.

A model claim counts as supported only if its evidence interval overlaps a relevant landmark window and a reviewer can confirm the described visible state in the source video around that time. An unsupported claim, wrong order, or interval that points to unrelated activity does not count as a hit.

## Pass / fail criteria

**Pass this Teach smoke test only if all are true:**

1. The response passes the existing process schema and reference validator.
2. The candidate describes at least three distinct landmarks from the table, in the correct broad chronological order.
3. Each counted landmark has a timestamped evidence interval that overlaps its registered window and visibly supports the description.
4. The output describes observed order as observed order; it does not assert that the observed sequence is required, safe, or the only valid method.
5. Ambiguous part identity or occluded actions are represented as uncertainty rather than invented detail.

Otherwise the result is **fail** or **inconclusive**, with the unmet criteria recorded. A valid JSON response alone is not a pass. A fluent summary without grounded timing is not a pass.

## Controls and limits

- The prompt uses the existing neutral learning instruction: learn only from the demonstration; do not assume the task or an expected mistake; cite visible evidence; do not infer prerequisites from one trace.
- Evaluation landmarks and this file are kept out of the model request.
- This is a single video and a single inference. There is no independent camera-angle or learner-run control in this test.
- Since the instruction booklet is visible, the test cannot distinguish visual instruction reading from learning the procedure by observing the hands alone.
- Passing only validates a narrow Teach capability on this clip. Do mode still requires a separate learner attempt, including a deliberate divergence and recovery, before we can claim it catches mistakes or helps complete the build.
