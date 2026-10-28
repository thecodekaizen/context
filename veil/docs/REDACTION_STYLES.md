# Redaction styles

VEIL now supports an explicit **face-only blur** option. Existing clients and historical timelines retain opaque covers by default. License plates and printed phone numbers must use opaque covers; the validated model rejects blur on those categories.

## Select the option

During `POST /v1/jobs/{id}/detect`, include:

```json
{"allow_cloud_transfer":true,"media_is_synthetic_or_consented":true,"face_action":"blur"}
```

Alternatively, a reviewed Timeline can set `action: "blur"` on a face track before `/redact`. The SDK's `protect(..., face_action="blur")` and `cloud_action(id, "detect", face_action="blur")` pass the same explicit option. Audit and repair requests must not carry a non-default style. A repair of a face residual escalates to opaque covering; cosmetic preference must not override an observed miss.

## Rendering behavior

The renderer uses the existing padded per-frame boxes. It does not claim polygon/contour masks. Conservative padding is unchanged. Face blur uses Gaussian sigma scaled to the protected region, with a minimum value of 18; this is a rendering parameter, not a validated anonymity threshold.

For overlap, the renderer first removes mandatory opaque regions, then applies face blur, then restores the solid covers. This prevents original text pixels from spreading into adjacent blurred pixels, and prevents blur from softening a required cover. Tests check operation-order independence, overlap and independence from the original covered text's pixels.

## Evidence and limits

`artifacts/face-blur-001/export.mp4` is a newly rendered variant using real saved `live-pipeline-003` geometry, with fresh verification of the new file. Two real Meta requests cost an estimated $0.004672. Spark reported no exposure in three model samples; independent local OCR completed on a denser schedule with no phone-like text found. The known spoken-number interval was silent, all 180 frames decoded, and visible plate/phone fixture regions remained covered throughout.

This is one composited synthetic clip. Neither Gaussian blur nor a passing sampled audit guarantees face anonymity. Identity may remain inferable from hair, clothing, context, voice or other footage. Opaque covers erase the covered source pixels in the rendered stream; they do not guarantee that every sensitive region was detected or that contextual information cannot be inferred. Never describe either style as leak-proof. The earlier opaque variant's audit was not reused for this output.

For the visual demo, label the new variant **Optional face blur** and preserve the original opaque variant as the conservative default. Both files and their separate receipts should remain available.
