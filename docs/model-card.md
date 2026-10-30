# CONTEXT Model & Capability Card

**Version:** 1.0 (Meta Global AI Developer Hackathon 2026)  
**Repository:** [https://github.com/thecodekaizen/context](https://github.com/thecodekaizen/context)  
**Primary Integration:** Meta Muse Spark 1.2 & Meta SAM 3.1

---

## 1. Overview & Architecture Role

CONTEXT is a deterministic-first video evidence workstation that investigates deceptive edits in **developer tutorials, software benchmark demos, and commercial product claims**. 

The system enforces a strict boundary between mathematical signal alignment and generative AI reasoning:
- **Signal-Level Grounding:** Mathematical alignment (4Hz visual cosine distance and normalized acoustic cross-correlation) isolates matching footage and omission intervals.
- **Generative AI Role:** Foundation models are **never** permitted to guess, invent, or assert an ungrounded omission. The Meta model is only invoked on verified, grounded intervals to explain potential semantic consequences.

---

## 2. Meta AI Model Integration

### A. Meta Muse Spark 1.2 (Bounded Semantic Interpretation)
* **Input Pack:** Receives two tightly bounded video excerpts: the original source context around the omission and the published edit boundary context (embedded audio preserved).
* **Output:** Generates structured semantic observations, potential effects on viewer interpretation, and epistemic uncertainty statements.
* **Strict Citation Guardrail:** Every observation must cite specific clip IDs and timestamps. The server validates that all citations point strictly within the provided excerpt windows; any ungrounded assertion is automatically rejected.
* **Epistemic Segregation:** Model reviews are stored separately (`interpretation-<id>.json`) and visually differentiated from measured physical findings.

### B. Meta SAM 3.1 (Spatial Crop & Peripheral Segmentation)
* **Capability:** Segments peripheral disclaimers, benchmark hardware configurations, non-standard compile flags, and UI disclaimer widgets cut out of frame when widescreen videos are cropped for mobile.
* **Evaluation Performance:** Passed the SAM 3.1 spatial crop gate with **> 99.9% pixel recall** and **~84% IoU** across multi-scale spatial reframing cases.

---

## 3. Epistemic Guardrails & Safety Boundaries

1. **Domain Boundary (Strict Whitelist):** Restricted exclusively to developer tutorials, benchmark demos, and product claims. Explicitly prohibits analysis of elections, political campaigns, wartime footage, or real public figures.
2. **Honest Failure Boundaries:** When an edit undergoes non-linear time warping (dynamic time remapping) or rapid jump-cuts below the 4Hz aligner resolution, CONTEXT safely abstains and outputs *"no material omission"*.
3. **Evidence Before Assertion:** An edit is never labeled as "fake" or "deceptive" solely because an original source cannot be found. If no correspondence is established, the output remains strictly inconclusive.
