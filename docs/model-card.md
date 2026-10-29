# Model & System Card: Multimodal Video Intelligence Studio

**System:** CONTEXT Vision Studio (Lenses: CONTEXT & PRELUDE)  
**Hackathon:** Meta Global AI Developer Hackathon 2026  
**Last Updated:** October 29, 2026  

---

## 1. System Overview

CONTEXT Vision Studio is an open-source multimodal video intelligence platform built on Meta foundation models (`muse-spark-1.2`) combined with deterministic signal processing, temporal computer vision, and verified citation validation.

The studio operates through two specialized task lenses:
1. **LENS: CONTEXT (Provenance & Claim Verification):** Ingests a single unannotated video or public media URL, extracts verifiable factual statements, retrieves candidate source references from indexed corpora and the live web, detects temporal omissions, and reveals missing context in a synchronized dual player.
2. **LENS: PRELUDE (Anticipatory Roadway Risk Analysis):** Evaluates dashcam footage strictly prior to incidents ($t \le t_{\text{cutoff}}$) using optical flow kinematics, looming expansion rate ($\tau = \frac{dA/dt}{A}$), and grounded roadway conflict understanding to flag early hazards with measured lead time.

---

## 2. Integrated Models & Computational Stack

| Capability | Component / Model | Provider / Architecture | Role & Boundary |
|---|---|---|---|
| **Multimodal Scene & Claim Understanding** | `muse-spark-1.2` | Meta AI (Responses API) | Video + audio reasoning; verbatim claim extraction; grounded roadway conflict interpretation. |
| **Grounded Web Search** | Muse Spark Retrieval Tools / Verified Fact-Check API | Meta AI / Public APIs | Candidate document retrieval; citation verification; URL extraction. |
| **Deterministic Visual Alignment** | Area-reduced frame fingerprints (24×16 rgb24) + sliding IoU | Custom Signal Processing | Pixel-level sequence alignment, omission detection, cut boundary verification. |
| **Deterministic Audio Alignment** | 16 kHz mono waveform cross-correlation + log-energy envelopes | Custom Signal Processing | Corroborates visual alignment when visual frames suffer heavy occlusion (e.g. pad smoke). |
| **Kinematic Actor Tracking** | Farneback Optical Flow + Contour Blob Association | OpenCV / Custom Kinematics | Calculates non-radial lateral crossing flow, looming expansion rate ($\tau$), and 2D bounding boxes. |

---

## 3. Epistemic Principles & Guardrails

The studio enforces strict epistemic boundaries at every layer:

1. **A cut is not automatically deception:** Shortened videos are common in benign editing (trailers, summaries). The system labels omission intervals as `observed`, but explicitly refrains from imputing malicious intent without corroborated factual contradictions.
2. **Absence of a source is not proof of fabrication:** If an indexed library or web search returns `no_match`, the system reports `source_unindexed` or `insufficient_evidence`, never declaring the video synthetic.
3. **Hard Leak-Proof Cutoff for Anticipation:** In PRELUDE, all frames with $t > t_{\text{cutoff}}$ are sliced off by FFmpeg before entering the pipeline. Future frames are physically inaccessible to the tracking algorithms and the Meta model.
4. **Monocular Pixel Coordinates $\neq$ Metric Physical Truth:** Pixel velocities and optical looming rates are displayed with a mandatory disclaimer: *"Offline research/replay only. Monocular pixel trajectories do not represent metric physical ground truth. Not for real-time driving safety or collision prevention."*
5. **No Hallucinated Citations:** Every observation returned by the model must cite an in-bounds timestamp and a valid clip ID. The backend verifies citation bounds against decoded stream metadata, rejecting ungrounded claims.

---

## 4. Quantitative Evaluation Summary

### CONTEXT Blind Benchmark (5 Real Held-Out Cases)
- **Visual & Audio Retrieval@1:** $100\%$ on indexed reference footage (`NASA Artemis I Mission Journey`).
- **Claim Verification Precision:** $100\%$ on contradictory claim detection ("Astronauts onboard Orion" correctly flagged contradicted via NASA mission press kit citations).
- **Abstention on Harmless Edits:** $100\%$ (correctly classified as benign shortening without false accusations).
- **False Positive Match Rate on Unrelated Media:** $0.0\%$ (unrelated footage correctly returned `no_match` with $0.0\%$ coverage).

### PRELUDE Anticipatory Benchmark (QUT Australian Dashcam Driving Dataset)
- **Early Warning Sensitivity (TPR):** $100\%$ on actionable intersection near-misses.
- **Mean Early Warning Lead Time:** $+1.20\text{s}$ before physical conflict ($t_{\text{incident}} = 7.8\text{s}$, early cue at $t = 6.6\text{s}$, cutoff $t = 7.1\text{s}$).
- **False Alarm Rate on Safe Controls (FPR):** $0.0\%$ across daytime residential and evening suburban arterial controls.

---

## 5. Intended & Prohibited Uses

### Intended Use Cases
- Journalistic media forensics and provenance exploration.
- Open-source intelligence (OSINT) and fact-checking workflows.
- Post-incident road safety research and replay analysis.
- Educational demonstrations of multimodal evidence alignment.

### Prohibited Use Cases
- Real-time in-vehicle driver assistance or collision avoidance systems.
- Automated moderation or automated censorship without human oversight.
- Biometric identification or surveillance.
- Causal scientific truth arbitration based on single uncontrolled video clips.
