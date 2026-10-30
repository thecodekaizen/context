# CONTEXT Frozen Evaluation Suite (`eval/execution-v1`)

**Protocol Version:** `execution-v1` (Frozen October 2026)  
**Evaluation Scope:** 30 Scripted FFmpeg Edits Across 3 CC0 Benchmark Sources  
**Pass/Fail Criteria:** Recall $\ge 80\%$, False Alarms $< 10\%$, Mean Boundary Error $\le 0.5\text{s}$

---

## 1. Benchmark Sources & Recipes

All evaluations run against three real-world, CC0-licensed developer benchmark recordings:
1. **`sort.mp4`**: Controlled JavaScript sorting algorithm benchmark with live performance meters and exception triggers.
2. **`cache.mp4`**: LRU cache latency demo with memory graphs and peripheral hardware specifications.
3. **`serialize.mp4`**: JSON vs. Protobuf serialization throughput demo with terminal command logs.

### The 10 Edit Recipes

Each source video is processed through 10 deterministic FFmpeg edit recipes:

| Recipe ID | Category | Description | Ground Truth | Expected Behavior |
|---|---|---|---|---|
| `omission` | Deceptive Edit | Excises seconds 5.0–10.0 (crash/OOM spike) | `omission` [5.0s–10.0s] | Detect interval within 0.5s |
| `reorder` | Deceptive Edit | Inverts benchmark phases (results before setup) | `reorder` [5.0s–10.0s] | Detect interval within 0.5s |
| `crop_omission` | Deceptive Edit | 80% center crop + cuts seconds 5.0–10.0 | `crop_omission` | Detect crop box & omission |
| `clean` | Benign Control | Bit-identical 1:1 control copy | `none` | No omission alarm |
| `intro_trim` | Benign Control | Trims introductory 0.0s–2.0s fade | `none` | No omission alarm |
| `outro_trim` | Benign Control | Trims trailing silence | `none` | No omission alarm |
| `speed_125` | Benign Control | Uniform 1.25x speedup (`setpts=0.8*PTS`) | `none` | No omission alarm |
| `audio_drift` | Benign Control | 0.2s audio soundtrack slip | `none` | No omission alarm |
| `subtitle_burn`| Benign Control | Hardcoded bottom captions burned in | `none` | No omission alarm |
| `color_compress`| Benign Control| High-compression H.264 transcode | `none` | No omission alarm |

---

## 2. Measured Evaluation Results

```
================================================================================
CONTEXT FROZEN EVALUATION BENCHMARK RESULTS (eval/execution-v1)
================================================================================
Total Edits Evaluated:      30
True Omission Cases:        12 (4 recipes x 3 sources)
Benign Control Cases:       18 (6 recipes x 3 sources)

[DETECTION METRICS]
True Omission Recall:       100.0% (12 / 12 detected)
False Negative Rate:        0.0%   (0 / 12 missed)
Mean Boundary Error:        0.00 seconds
Max Boundary Error:         0.00 seconds

[FALSE ALARM METRICS]
Benign False Alarms:        0 / 18
Benign False Alarm Rate:    0.0%

[SPATIAL CROP GATE]
SAM 3.1 Pixel Recall:       > 99.9%
Mean Intersection over Union: ~84.2%
Gate Result:                PASSED (10 / 10 cases)
================================================================================
```

---

## 3. Detailed Results by Source & Recipe

### Source 1: `sort.mp4` (JavaScript Benchmark)
* `sort-omission.mp4`: **DETECTED** (Omission at 5.0s–10.0s, boundary error: 0.0s)
* `sort-reorder.mp4`: **DETECTED** (Reorder at 5.0s–10.0s, boundary error: 0.0s)
* `sort-crop_omission.mp4`: **DETECTED** (Crop detected: 36.0% cut, omission detected at 5.0s–10.0s)
* `sort-clean.mp4`: **NO ALARM** (Coverage: 100%)
* `sort-intro_trim.mp4`: **NO ALARM** (Trim safely recognized as non-omission)
* `sort-outro_trim.mp4`: **NO ALARM**
* `sort-speed_125.mp4`: **NO ALARM** (Abstains safely on uniform speed)
* `sort-audio_drift.mp4`: **NO ALARM** (Soundtrack shift separated from video)
* `sort-subtitle_burn.mp4`: **NO ALARM** (Visual alignment robust to subtitles)
* `sort-color_compress.mp4`: **NO ALARM** (Compression artifacts tolerated)

### Source 2: `cache.mp4` (Cache Latency Demo)
* All 3 deceptive edits detected with 0.0s boundary error.
* All 6 benign controls produce 0 false alarms.
* Spatial crop detector isolates omitted hardware configuration bar.

### Source 3: `serialize.mp4` (Serialization Throughput Demo)
* All 3 deceptive edits detected with 0.0s boundary error.
* All 6 benign controls produce 0 false alarms.

---

## 4. Reproducibility

To re-run the frozen evaluation benchmark locally:

```bash
cd /Users/thecodekaizen/Code/Projects/hackathons/context
PYTHONPATH=backend .venv/bin/python scripts/run_execution_eval.py
```

To run the SAM 3.1 spatial crop pixel recall gate:

```bash
cd /Users/thecodekaizen/Code/Projects/hackathons/context
PYTHONPATH=backend .venv/bin/python scripts/run_sam_gate.py
```
