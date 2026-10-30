# CONTEXT: 3-Minute Demo Script & Storyboard

**Meta Global AI Developer Hackathon 2026**  
**Target Duration:** Exactly 3:00 minutes (180 seconds)  
**Track:** Solo / Indie Developer Track  
**Rule:** Authentic builder voice only (no synthetic/cloned speech). Every claim backed by repo data.

---

## 3-Minute Timeline Overview

| Timecode | Section | Visual on Screen | Spoken Narration (Builder Voice) | Grounded Repo Evidence |
|---|---|---|---|---|
| **0:00–0:25** | **The Hook & Reveal** | Play misleading 12-second clip where benchmark claims "100x speedup with zero errors". Then immediately snap to side-by-side reveal showing the 5 seconds cut out where cache memory spiked and crashed. | *"Watch this developer demo. The edited clip claims a 100x performance breakthrough. But when you align it with the original recording, you instantly see what was cut: seconds 5 to 10, where the benchmark memory spiked and threw an out-of-memory error."* | `eval/execution-v1/sources/sort.mp4` vs `sort-omission.mp4`; 5-second omitted interval. |
| **0:25–0:55** | **The Core Problem & Architectural Rule** | Graphic showing the trap of "hallucinating analyzers" vs CONTEXT's deterministic-first architecture diagram. | *"Misleading edits of developer tutorials, benchmark demos, and product claims cut out critical qualifications. But you cannot simply ask a foundation model to guess what was cut—models hallucinate omissions that never existed. CONTEXT enforces a strict non-negotiable rule: deterministic alignment first. If our acoustic and visual aligner finds no correspondence, the output is 'no material omission'. The Meta model is only permitted to reason over verified, grounded intervals."* | Architecture rule in README; evidence contract `{source_start, source_end, edit_position, confidence}`. |
| **0:55–1:50** | **Live Pipeline & Side-by-Side Review** | Live run in CONTEXT workstation: upload candidate clip, trace against source. Dual-player timeline scrubbers lock together. Clicking omission card seeks source player directly to the missing cut. | *"Here's a live run. The aligner chunks the media, downsamples 4Hz visual feature grids, and runs normalized acoustic cross-correlation. Within seconds, it locks the correspondence with sub-second accuracy. Notice our dual player: scrubbing the edited video synchronously drives the source. When we click the omission card, it reveals the excised footage. Meta Muse Spark 1.2 explains the exact semantic consequence, bounded strictly by our citation checker: any explanation citing timestamps outside the evidence is rejected."* | `SourceComparison.tsx`, synchronized playback, `grounded_omissions.py`, `meta.py` bounded citations. |
| **1:50–2:20** | **Spatial Crop & Reframe (SAM 3.1)** | Switch to vertical mobile reframe case (`crop_omission`). Green dashed bounding box highlights retained area; red shaded overlay highlights the peripheral chart and disclaimer cropped out. | *"Deceptive cuts aren't just temporal—they're spatial. When a widescreen tutorial is reframed or cropped for mobile, key disclaimers and benchmark sidebars vanish. Having passed our SAM 3.1 gate with over 99% pixel recall, CONTEXT runs multi-scale spatial alignment and uses SAM 3.1 to segment and shade the exact peripheral elements cut out of frame."* | `crop_detector.py`, SAM 3.1 gate (`10/10` passed, IoU `0.84`), SVG margin overlay. |
| **2:20–2:45** | **Evaluation & Quantitative Proof** | Display frozen benchmark table and charts: 30 scripted edits across 3 sources, 18 benign controls. | *"Every claim here is backed by reproducible numbers. Before writing a line of tuning code, we froze a labeled eval contract: 30 automated FFmpeg edits, including 18 benign controls—intro trims, 1.25x speed-ups, subtitles, re-encodes, and reorders. Our thresholds were fixed beforehand: at least 80% recall and under 10% false alarms. CONTEXT scored 100% interval recall, 0.0 seconds mean boundary error, and exactly zero false alarms on benign edits."* | `eval/execution-v1/full-results/RESULTS.md`; 30/30 passed; 0% false alarms. |
| **2:45–3:00** | **Meta Model Attribution & Honest Failure** | Summary screen showing model roles, repo link, and the honest failure case. | *"Here's what each Meta model did: Muse Spark 1.2 provided bounded semantic interpretation; SAM 3.1 powered spatial reframe segmentation. And here is our honest failure case: when an edit undergoes aggressive non-linear speed changes or extreme jump-cuts, the aligner safely abstains rather than making a false accusation. CONTEXT is reproducible with one Docker command. Code, benchmarks, and data are public in our repository."* | Model attribution table, `Dockerfile`, reproducible commands. |

---

## Narration Recording Script (Builder Voice)

### Chapter 1: Hook & Reveal (0:00 – 0:25)
> "Watch this developer demo. The edited clip claims a 100x performance breakthrough. But when you align it with the original recording, you instantly see what was cut: seconds 5 to 10, where the benchmark memory spiked and threw an out-of-memory error."

### Chapter 2: The One-Line Problem (0:25 – 0:55)
> "Misleading edits of developer tutorials, benchmark demos, and product claims cut out critical qualifications. But you cannot simply ask a foundation model to guess what was cut—models hallucinate omissions that never existed. CONTEXT enforces a strict non-negotiable rule: deterministic alignment first. If our acoustic and visual aligner finds no correspondence, the output is 'no material omission'. The Meta model is only permitted to reason over verified, grounded intervals."

### Chapter 3: Live Dual-Player Run (0:55 – 1:50)
> "Here's a live run. The aligner chunks the media, downsamples 4Hz visual feature grids, and runs normalized acoustic cross-correlation. Within seconds, it locks the correspondence with sub-second accuracy. Notice our dual player: scrubbing the edited video synchronously drives the source. When we click the omission card, it reveals the excised footage. Meta Muse Spark 1.2 explains the exact semantic consequence, bounded strictly by our citation checker: any explanation citing timestamps outside the evidence is rejected."

### Chapter 4: SAM 3.1 Spatial Crop Detector (1:50 – 2:20)
> "Deceptive cuts aren't just temporal—they're spatial. When a widescreen tutorial is reframed or cropped for mobile, key disclaimers and benchmark sidebars vanish. Having passed our SAM 3.1 gate with over 99% pixel recall, CONTEXT runs multi-scale spatial alignment and uses SAM 3.1 to segment and shade the exact peripheral elements cut out of frame."

### Chapter 5: 30-Edit Eval Benchmark (2:20 – 2:45)
> "Every claim here is backed by reproducible numbers. Before writing a line of tuning code, we froze a labeled eval contract: 30 automated FFmpeg edits, including 18 benign controls—intro trims, 1.25x speed-ups, subtitles, re-encodes, and reorders. Our thresholds were fixed beforehand: at least 80% recall and under 10% false alarms. CONTEXT scored 100% interval recall, 0.0 seconds mean boundary error, and exactly zero false alarms on benign edits."

### Chapter 6: Model Attribution, Failure Case & Wrap (2:45 – 3:00)
> "Here's what each Meta model did: Muse Spark 1.2 provided bounded semantic interpretation; SAM 3.1 powered spatial reframe segmentation. And here is our honest failure case: when an edit undergoes aggressive non-linear speed changes or extreme jump-cuts, the aligner safely abstains rather than making a false accusation. CONTEXT is reproducible with one Docker command. Code, benchmarks, and data are public in our repository."

---

## Screen Recording Instructions

1. Start uvicorn:
   ```bash
   uvicorn context_core.api:app --app-dir backend --env-file .env --host 127.0.0.1 --port 8000
   ```
2. Set display to 1920×1080 (16:9 widescreen).
3. Record high-bitrate MP4 (60 fps or 30 fps).
4. Synchronize video with your voiceover track according to the timecodes above.
