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

## Human observation and limits

The user reports that the learner clip contains multiple mistakes and incorrect arrangements. This establishes a human-observed false negative for the current runs, but the exact mistake timestamps and labels have not been independently recorded. Therefore this result is qualitative; it is not a precision/recall score.

The clip begins with the central body and wing assemblies already built. It tests reworking and attaching subassemblies, not learning the whole procedure from loose pieces. The camera is close to the build, the hands frequently cover the small connections, and the relevant transitions are quick.

## Conclusion

**Fail for the current setup.** The model did not detect the reported mistakes and could not validate the final arrangement against the official instructions. The broad candidate Skill Model from IMG_7660 is not detailed enough to check piece-level relationships. Adding the instructions improved the target description but did not overcome the visibility limits. The claim that the model recognized a recovery is not supported.

Do not present this run as proof that SHOWME catches physical mistakes or guides recovery.

## Engineering consequence

The Do experience needs a verified target model and a way to ask for a clearer view when the decisive connection is hidden. It must leave the state unresolved when it cannot see enough evidence, and it must not call an action a recovery unless a confirmed mismatch is followed by a clearly visible, target-consistent state. A future controlled capture should hold the completed assembly still from above and show both wing faces and attachment points unobstructed; this clip remains useful as a hard, realistic failure case.
