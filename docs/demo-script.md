# Three-Minute Demo Storyboard: CONTEXT Vision Studio

**Meta Global AI Developer Hackathon 2026**  
**Track:** Multimodal Video Intelligence Studio  
**Target Video Duration:** 3:00 minutes (180 seconds)  

---

## Storyboard Overview: Prove the Engine, Not Just the Tabs

| Timecode | Screen / Lens | Action | Spoken Narration | Grounded Evidence Shown |
|---|---|---|---|---|
| **0:00–0:25** | Studio Home | Drop `artemis-captioned-omission.mp4` into the single-video intake. | *"A video can show authentic NASA launch footage, but the caption claims astronauts were on board. How do you verify the footage, uncover what was omitted, and challenge the claim using only the single video?"* | Single unannotated video intake; pipeline acknowledges ingestion in $<1\text{s}$. |
| **0:25–1:05** | **LENS: CONTEXT** (Dossier) | Click **Investigate**. Show live analysis stages. View extracted claims and discovered sources. | *"CONTEXT extracts visual events and spoken claims using Meta Muse Spark. It autonomously searches indexed corpora and verified records. Here, it matches the official NASA Artemis I Mission Journey with 86% coverage, and flags the caption claim as CONTRADICTED, citing the official uncrewed mission kit."* | Discovered source citations; contradiction badge; timeline with omission cuts. |
| **1:05–1:40** | **Dual-Player Comparator** | Click **"Reveal Missing Context in Synchronized Dual Player"**. | *"One click opens our synchronized dual player. Deterministic frame fingerprints and 16 kHz audio cross-correlation lock the published edit to the original broadcast. We scrub directly into the 6-second cut NASA omitted, with zero hallucination."* | Dual video player synchronized at millisecond accuracy; visual & audio alignment tracks. |
| **1:40–2:15** | **Abstention & Honest Edit** | Load `honest_qualification.mp4` sample. | *"Epistemic honesty matters. When a video is shortened fairly without false claims, CONTEXT flags the cut as observed, but abstains from accusing the editor of deception. Absence of evidence is never treated as fabrication."* | Honest provenance classification; zero false accusations. |
| **2:15–2:45** | **LENS: PRELUDE** (Anticipate) | Switch to **Anticipate Roadway Hazards**. Load `near_crash_011` dashcam scenario. Adjust cutoff slider to $t \le 7.1\text{s}$. | *"The same time-series engine powers PRELUDE for anticipatory road safety research. We enforce a hard leak-proof cutoff before the incident. Farneback flow isolates lateral crossing vectors and looming expansion rate $\tau$. Muse Spark identifies the oncoming hatchback failing to yield, flagging an early cue 1.2 seconds before the physical conflict."* | Hard pre-incident horizon ($t \le 7.1\text{s}$); bounding boxes with velocity arrows; $+1.20\text{s}$ lead time; zero false alarms on safe controls. |
| **2:45–3:00** | System Summary | Show evaluation metrics table and architecture overview. | *"CONTEXT Vision Studio: One unified video-first engine, two proven multimodal lenses, and strict epistemic boundaries. Grounded multimodal intelligence you can inspect frame by frame."* | 82/82 passing tests, quantitative benchmark summaries, open-source repo. |

---

## Preparation Checklist Before Recording

1. Ensure the local server is running:
   ```bash
   uvicorn context_core.api:app --app-dir backend --env-file .env --host 127.0.0.1 --port 8000
   ```
2. Open `http://127.0.0.1:8000/` in Chrome at 1920×1080 resolution.
3. Pre-load sample scenarios:
   - CONTEXT: `artemis-captioned-omission` (ready via "Open Saved Investigation").
   - PRELUDE: `near_crash_011` (ready via top sample chips).
4. Verify audio recording input and system sound routing.
5. Keep mouse movements smooth and deliberate; pause 1 second on key finding cards.
