# SHOWME learner clip review: IMG_7663

**Date:** 2026-10-27  
**Result:** Core mistake-detection hypothesis not demonstrated  
**Set:** LEGO 30727 TIE Advanced mini-build  
**Reference:** [Official LEGO building instructions](https://www.lego.com/cdn/product-assets/product.bi.core.pdf/6609577.pdf)

## Question

Can SHOWME compare the learner's assembly with a learned process, detect a wrong physical arrangement, and recognize a verified correction?

## Runs

### Baseline video observation

Muse Spark 1.3 compared the 111-second learner clip to the candidate process inferred from IMG_7660. That process described broad groups such as a central body and black panel subassemblies; it did not encode piece-level geometry or the official target arrangement.

- Result: 5 events, 0 divergences, `no_divergence_observed`.
- Two intermediate events were marked unclear; the final combined model was marked consistent.
- Usage: 30,680 input tokens and 1,090 output tokens.

### Instruction-grounded video review

The same learner clip was compared with the two official instruction pages, with attention to the two wings and their attachment to opposite sides of the body.

- Result: 0 confirmed mismatches.
- The model described the clip as too blurred, dark, and hand-occluded to verify wing-face and connector orientation.
- It nevertheless described the reassembly as a recovery despite having confirmed no preceding mismatch. This is unsupported recovery language and must not count as a recovery result.
- Usage: 34,588 input tokens and 1,784 output tokens.

### Original-resolution still comparison

Three frames around 89, 92, and 97 seconds were compared with the step 17–18 diagram.

- Result: all three frames unclear; 0 confirmed mismatches.
- The model could see both wings in some frames but could not verify the smooth/studded faces or hinge-to-body connections because of motion blur and hand occlusion.
- Usage: 11,293 input tokens and 456 output tokens.

### Manual-backed step ledger replay

After adding explicit per-manual-step checks, the same 111-second learner clip and saved process were replayed once. Muse Spark 1.3 returned 18 reference checks, five observed events, one divergence, and `recovered` in 49.2 seconds. Usage was 33,305 input tokens and 2,289 output tokens.

- Steps 1–15: `not_shown`; the clip begins with those subassemblies already built. The output did not claim they were missing and supplied the next step or view needed for each.
- Step 16: the model reported that the white round tile was briefly placed on the cockpit area at 42 seconds, although the manual shows it on the wing panel.
- At 60 seconds, the model reported the tile on the wing panel; at 88 seconds, both wings were attached. It treated these later states as consistent and marked recovery.
- I inspected the extracted frames at 42, 60, and 88 seconds against manual page 2. The sequence supports a possible temporary placement error followed by correction. This is a useful single-run signal, not an independently preregistered or repeated evaluation.
- SAM 3.1 returned zero detections for both the cockpit core and wing panel on the cited 42-second frame. Visual grounding failed; the frame is tightly cropped and the hand covers the assembly.

## Human observation and limits

The user reports that the learner clip contains multiple mistakes and incorrect arrangements. This establishes a human-observed false negative for the current runs, but the exact mistake timestamps and labels have not been independently recorded. Therefore this result is qualitative; it is not a precision/recall score.

The clip begins with the central body and wing assemblies already built. It tests reworking and attaching subassemblies, not learning the whole procedure from loose pieces. The camera is close to the build, the hands frequently cover the small connections, and the relevant transitions are quick.

## Conclusion

**Partial signal; core hypothesis not yet passed.** Earlier runs missed the reported mistakes. The manual-backed step ledger produced one plausible, visually supported catch and a later correction in this clip. However, it is one run without independently recorded ground truth, most early steps were not visible, and recovery was inferred from two later frames rather than observed continuously. SAM grounding failed on the cited moment. This does not establish reliable mistake detection, complete-task guidance, or live intervention.

Do not present this run as proof that SHOWME catches physical mistakes or guides recovery.

## Engineering consequence

The Do experience now presents a check for every cited manual step, links visible checks to timestamps, and gives next actions for steps that are absent or unclear. Keep the mismatch visibly labeled as possible until a human reviews it. A future controlled capture should show the pieces before assembly, hold each decisive joint unobstructed, and record the intended mistake and correction as separate labeled evaluation conditions; this clip remains a realistic hard case.
