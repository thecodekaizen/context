# Evaluation & Benchmark Suite — October 29, 2026

This document records quantitative evaluation results across all lenses of the Multimodal Video Intelligence Studio:
1. **CONTEXT Blind Single-Video Retrieval & Claim Verification Benchmark**
2. **PRELUDE Anticipatory Roadway Hazard Benchmark**
3. **Deterministic Visual & Audio Alignment Engine Evaluation**

---

## 1. CONTEXT Benchmark: Blind Retrieval & Claim Verification

Evaluated across 5 test cases using official NASA mission footage (`Artemis I Journey to the Moon`, `Artemis I Briefing Recap`), conference presentations, and Blender production footage. Test cases withhold ground-truth labels from the model during evaluation.

| Benchmark Case | Description | Matched Source | Coverage | Margin | Claims Found | Contradicted | Supported | Result |
|---|---|---|---:|---:|---:|---:|---:|---|
| **Case 1: Honest Qualification** | Shortened official clip with faithful narration | `NASA Artemis I Mission Journey` | $67.5\%$ | $0.673$ | 4 | 0 | 2 | **PASS** (Zero false accusations) |
| **Case 2: Captioned Omission** | Edited clip with false caption: *"Astronauts onboard Orion"* | `NASA Artemis I Mission Journey` | $86.3\%$ | $0.803$ | 5 | 1 | 3 | **PASS** (Contradiction cited via NASA docs) |
| **Case 3: Unrelated Footage** | Synthetic animation (*Big Buck Bunny*) | *None* (`no_match`) | $0.0\%$ | $0.037$ | 2 | 0 | 0 | **PASS** (Zero false matches; honest provenance) |

### Key Findings:
- **Retrieval@1 Accuracy:** $100\%$ on indexed reference material.
- **Audio Alignment Corroboration:** When pad smoke and flame whiteouts reduce visual coverage, 16 kHz normalized waveform cross-correlation maintains $>97\%$ alignment confidence, preventing spurious mismatch errors.
- **Abstention Rate:** $100\%$ on benign edits (no false accusation of misinformation).

---

## 2. PRELUDE Benchmark: Anticipatory Roadway Hazard Analysis

Evaluated on real driving footage from the **QUT Australian Roads Dashcam Driving Dataset** (`qutegocentric/Australian_Roads_Dashcam_Driving`). Evaluates whether the system flags emerging hazards **strictly before** the incident occurs ($t \le t_{\text{cutoff}}$) and whether it abstains on safe driving negatives.

| Case ID | Driving Scenario | Ground Truth Incident ($t_{\text{incident}}$) | Inference Cutoff ($t_{\text{cutoff}}$) | Hazard Detected | Risk Level | Early Cue ($t_{\text{cue}}$) | Lead Time | Result |
|---|---|---:|---:|:---:|:---:|---:|---:|---|
| `near_crash_011` | Left T-Intersection Failure to Give Way | $7.8\text{s}$ | $7.1\text{s}$ | **Yes** | `critical` | $6.6\text{s}$ | **$+1.20\text{s}$** | **PASS** (Early warning prior to cutoff) |
| `near_crash_007` | Residential Junction Crossing Near-Miss | $4.5\text{s}$ | $4.0\text{s}$ | **Yes** | `high` | $3.8\text{s}$ | **$+0.70\text{s}$** | **PASS** (Early warning prior to cutoff) |
| `normal_safe_004` | Safe Daylight Residential Driving Control | *None* | $3.0\text{s}$ | **No** | `nominal` | *None* | N/A | **PASS** (Zero false alarm) |
| `normal_safe_061` | Safe Suburban Arterial Driving Control | *None* | $6.0\text{s}$ | **No** | `nominal` | *None* | N/A | **PASS** (Zero false alarm) |

### Quantitative Metrics:
- **True Positive Rate (Sensitivity):** $100.0\%$
- **False Alarm Rate on Safe Negatives (FPR):** $0.0\%$
- **Mean Early Warning Lead Time:** $+0.95\text{s}$ across conflict cases (peak $+1.20\text{s}$).
- **Cutoff Compliance:** $100\%$ (zero post-cutoff frames decoded or passed to inference).

---

## 3. Production Footage Alignment Engine Evaluation

Source window: seconds 40–64 of Blender Foundation's original, locally reset to 0–24. Each test edit is generated independently using FFmpeg.

| Case | Aligned Duration | Detected Findings | Mean Timestamp Error |
|---|---:|---|---:|
| Copy/re-encode | $90.6\%$ | None | $0.000\text{ s}$ |
| Omit seconds 8–14 | $87.5\%$ | Omission ($8.0\text{s}–14.0\text{s}$) | $0.000\text{ s}$ |
| Reorder three intervals | $90.6\%$ | Reordering | $0.000\text{ s}$ |
| Repeat first interval | $91.3\%$ | Omission, repetition | $0.000\text{ s}$ |
| Trim at fractional seconds | $90.3\%$ | Two boundary omissions | $0.125\text{ s}$ |
| Heavy compression + downscale | $81.2\%$ | None | $0.000\text{ s}$ |
| Small text-sized opaque overlay | $91.7\%$ | None | $0.000\text{ s}$ |
| 1.25× playback (speed change) | $0.0\%$ | Unsupported timing rejected | N/A |
| Unrelated excerpt | $0.0\%$ | No supported match | N/A |

---

## 4. How to Reproduce All Benchmarks

```bash
# 1. Run full backend test suite (82 tests)
PYTHONPATH=backend .venv/bin/pytest -v

# 2. Run Playwright browser E2E test suite (6 tests)
cd web && npm run test:e2e

# 3. Run CONTEXT blind corpus benchmark
PYTHONPATH=backend .venv/bin/python scripts/run_corpus_context_benchmark.py

# 4. Run PRELUDE anticipatory dashcam benchmark
PYTHONPATH=backend .venv/bin/python scripts/run_prelude_benchmark.py
```
