# Compare learner evidence with the actual reference — v5

Status: implemented and locally tested; no new perception run and no capability pass.

## Gap addressed

The v4 learner comparison received the learner clip and extracted process prose, but not the instruction PDF whose page/step citations it purported to check. A mistaken geometric claim in Teach could therefore become the target used to diagnose a learner. The existing v4 artifacts remain untouched.

Observe now accepts an optional reference PDF, using the existing narrow provider adapter. The HTTP endpoint `/api/skills/observe` accepts `reference_pdf`; no file is fetched or uploaded automatically. Existing callers without it remain supported. The CLI exposes `observe-video PROCESS VIDEO --reference-pdf PDF --output NEW_DIRECTORY`.

The v5 prompt distinguishes direct PDF evidence from extracted claims. With a PDF, it asks the model to disclose source/model conflicts rather than diagnose the learner against unsupported prose. Without it, the prompt states that no source images are available and requires disclosure of that limitation. Comparisons should use visible connector/facing relationships; apparent size across different diagram scales or views is insufficient. Possible reference mismatches must have a divergence at the same evidence timestamp. The validator's two-second guard has not been relaxed.

Run metadata records `comparison_source` (`attached_reference` or `extracted_process_only`) and the explicitly supplied reference's SHA-256. The API preserves this metadata. The CLI saves its exact prompt and an explicitly named `observation-unvalidated.json` before validating; rejected model output therefore remains inspectable without becoming accepted guidance.

## Verification

Local controlled-provider tests cover default no-upload behavior, explicit PDF forwarding/hash, missing source disclosure, source/model conflict instructions, invalid-PDF rejection before provider use, and HTTP provenance retention. These tests establish software behavior, not visual accuracy. A `%PDF-` header check is a coarse format check, not a security or semantic PDF validator.

## Next permitted experiment

A new run requires approval covering the learner clip, candidate process, actual instruction PDF, and API credit use. Use an independently reviewed process candidate first; do not treat the currently questionable v4 candidate as ground truth. Preserve neutral media names, exact prompt, process hash, PDF hash, raw response, validation outcome and latency. Do not include an expected error or human answer key. Compare correct and divergent attached states before making an orientation claim; reference access alone does not establish reliable geometry understanding.

No Meta call was made for this change. Existing footage and experiment outcomes are unchanged.

## Integration follow-up — October 28

The API now retains a canonical SHA-256 of the semantic process claims (private `_` metadata excluded), so a report can be associated with the exact process used. A local regression checks that changing claims changes the hash while changing private run metadata does not. Backend checks: 66 passed.

One subsequently approved source-aware comparison ran against the saved baseline and IMG_7670. It returned no supported divergence, with occlusion uncertainty. See `results/showme-source-comparison-v5-2026-10-28.md`; this is not a perception pass.
