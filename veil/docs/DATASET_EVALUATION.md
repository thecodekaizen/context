# External dataset evaluation

## First external fixture: synthetic Ukrainian plates

Source: https://zenodo.org/records/13342103 (Shpir, Shvai and Nakib, 2024).
License: CC BY 4.0, confirmed in the Zenodo metadata.

Archive MD5: `1c4a9db36e5f0a662ca7a5a0fcb513dc`.
10,000 generated 193×72 plate images; supplied train/validation/test splits. Download approximately 236 MB, kept in ignored private storage.

Protocol: choose six evenly spaced filenames from the sorted test split before inference, resize to three fixed widths on simple vehicle-like canvases, anonymize input filenames, freeze hashes. Four maximum real Spark requests: two source batches and two fresh exported-image review batches. No retries. The model receives pixels and timestamps, never filenames containing plate text or the evaluation boxes.

Report per-sample plate pixel coverage and unnecessary masked image area. A fully covered plate alone is insufficient: unnecessary masking must be reported. Still-image tests do not establish tracking performance, natural-scene recall or anonymity.

Commands from the product directory:

```
PYTHONPATH=src .venv/bin/python scripts/evaluate_plate_dataset.py prepare --archive artifacts/private/datasets/ukrainian-plates/source.zip --root artifacts/plate-dataset-001
PYTHONPATH=src .venv/bin/python scripts/evaluate_plate_dataset.py run --root artifacts/plate-dataset-001 --env-file /path/to/private/.env
```

## Screened alternatives

- PP4AV: directly relevant face/plate annotations, but real driving imagery and CC BY-NC-ND terms. Not sent to cloud under our synthetic/consented-media rule. https://github.com/Fsoft-AIC/PP4AV/blob/main/DATASET.md
- Microsoft FaceSynthetics: generated faces with pixel labels; research-use agreement explicitly excludes product/service improvement. Not adopted for product development. https://github.com/microsoft/FaceSynthetics/blob/main/LICENSE.txt
- Rickkosse synthetic Dutch plates: card says actual cropped plate imagery and BDD100K backgrounds; synthetic label does not establish consent for cloud transfers. Not adopted. https://huggingface.co/datasets/Rickkosse/kenteken-synthetic-dataset

## Next dataset gates

Add consent-cleared face video and labeled plate sequences; retain source terms, hashes and frozen selection. Measure boundary frames, occlusion, temporal coverage and collateral masking. Keep still-image scores separate from video scores. Avoid claiming a dataset was tested until results exist.
