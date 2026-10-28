# VEIL Natural Editing: Dataset Screening and Case Selection

**Date**: 28 October 2026  
**Author**: Antigravity (Visual Experiments & Dataset Screening Owner)  
**Status**: Formal Screening Shortlist (Audited & Corrected per Peer Review)  
**Repository**: `veil/` (multimodal video privacy engine)  
**Baseline Checkpoint**: Commit `71f205a` / `81ebb59`  

---

## 1. Executive Summary & Screening Policy

Under the hackathon working agreement and `ANTIGRAVITY_NATURAL_EXPERIMENTS.md`, VEIL's natural-editing acceptance gate requires at least **four of six fixed cases** to be visually acceptable without per-frame manual repair, with zero leaked original identifiers, no unexpected blackout frames, and blinded preference evidence.

Before implementing new benchmark runs or executing cloud model calls, this document delivers a concrete screening of **six proposed candidate slots** targeting the six priority capabilities:
1. **Camera movement** (dynamic camera panning across office surfaces)
2. **Moving / perspective vehicle plate** (road vehicle with changing planar angle)
3. **Difficult lighting** (surveillance optics under outdoor ambient glare/shadow)
4. **Brief occlusion & reappearance** (roadside planar text temporarily occluded)
5. **Static plate with extreme angle & texture** (European license plate font and physical distortion)
6. **Angled screen with display refresh** (handheld phone with fake credentials and autofocus dynamics)

### Core Compliance & Verification Principles
- **No relabeling of synthetic animation as natural video**: Still-image plate datasets (e.g., Ukrainian plates, CCPD) are classified as synthetic animation or geometric test fixtures, not continuous temporal camera validation.
- **Strict third-party cloud transfer clearance**: Under VEIL's privacy policy, real strangers' faces or vehicle license plates captured without consent on public roads **must never be transferred to Meta cloud APIs**.
- **Pexels License vs. Model Consent**: A royalty-free stock license (e.g., Pexels) permits commercial use and distribution, but stock platforms do not guarantee that every bystander has an executed release suitable for cloud AI training or inference. In our project, Pexels footage is cleared for cloud processing **only when used as an unpopulated background onto which synthetic targets are composited**.
- **Candid reporting of access barriers**: Missing footage, restricted FTP servers, or author-permission gates are recorded as explicit gaps (`PENDING`, `RESTRICTED`, or `MISSING / DECLINED`), not assumed ready.

---

## 2. Six Proposed Clip Candidates

### Candidate 1: Pexels Kampus 8347238 Hybrid (Office Screen / Desk Camera Pan)
- **Priority Capability**: Camera movement + angled planar surface.
- **Official Dataset / Source**: Pexels Stock Video ID `8347238` ("Computers on the Office Table" by Kampus Production).
  - Source Page: https://www.pexels.com/video/computers-on-the-office-table-8347238/
  - Raw Source Download URL: `https://videos.pexels.com/video-files/8347238/8347238-uhd_2160_3840_25fps.mp4`
  - Provenance Ledger: `veil/artifacts/public-footage-001/source-provenance.json`
- **Access Status**: `VERIFIED` (Direct public HTTPS download confirmed).
- **Probed Media Attributes & Hashes**:
  - Raw Downloaded Asset: 20,154,891 bytes (~19.2 MB), 2160×3840 (portrait 4K), 25 fps.
  - Raw Source SHA-256: `47c2ecc4a76533f84d95ed0f88703df7e282d3c23ab730b38511bf1424258264`.
  - Normalized Challenge Clip (`veil/artifacts/public-footage-001/challenge.mp4`):
    - Width: **360 px**, Height: **640 px** (Portrait orientation).
    - Framerate: **12.0 fps**, Decoded Frames: **96 frames**.
    - Container Duration: **8.000 s**, File Size: **592,161 bytes**.
    - SHA-256: `a4bd2f9c643a74222569dc06b85e1c65fe881d825b73af051bc0e27a7f1ccf71`.
- **Crop Interval**: `0.0s` to `6.0s` (72 frames @ 12 fps) or full `8.0s` (96 frames).
- **License & Rights Clearance**:
  - License: Pexels License (https://www.pexels.com/license/). Free commercial and non-commercial use, modification permitted, no legal attribution required.
  - Creator Credit: Kampus Production.
  - Cloud Handling Justification: The raw footage depicts an empty office desk with computer monitors; **no identifiable living persons or private personal data appear**. The privacy targets in `challenge.mp4` are purely synthetic overlays (fictional portrait and fake numbers). Thus, third-party cloud transfer to Meta APIs is cleared for this hybrid asset.
- **Permissions**:
  - Local Evaluation: `PERMITTED`
  - Public Demonstration: `PERMITTED`
  - Third-Party Cloud Transfer: `PERMITTED` (as a hybrid with synthetic targets).
- **Available Annotations**: None in raw source. (Known bounding boxes exist for synthetic overlays in `veil/artifacts/public-footage-001/challenge-provenance.json`).
- **Manual Annotation Requirement**:
  - 4-corner screen quad across 96 frames: ~12–15 minutes (or 1 keyframe quad + LK forward tracking verification).
- **Contact Sheet Reference**: Verified in `veil/artifacts/public-footage-001/background-contact-sheet.jpg` and `challenge-contact-sheet.jpg`.
- **Classification**: **Public Demo & Live Benchmark Candidate**.

---

### Candidate 2: Pexels Road Perspective Vehicle (Proposed Slot — Direct URL Unverified)
- **Priority Capability**: Moving / perspective vehicle plate under natural outdoor daylight.
- **Official Dataset / Source**: Pexels Stock Video Search (Vehicle Driving / Traffic Perspective).
  - Search Page: https://www.pexels.com/search/videos/car%20driving/
  - Target Scene: Front/rear vehicle tracking shot showing planar license plate angle shift.
- **Access Status**: `PROPOSED SLOT (Direct URL Unverified)`.
  - *Correction*: CDN video URLs cannot be constructed algorithmically from video IDs without hitting 404. Direct stream URL must be resolved interactively from Pexels publisher page before download.
- **Source Byte Size & Hash**: `null / unknown until downloaded`.
- **Proposed Crop**: `0.0s` to `5.0s` (approx. 120–150 frames depending on source fps).
- **License, Terms & Attribution**:
  - License: Pexels License (https://www.pexels.com/license/). Free commercial use.
- **Permissions**:
  - Local Evaluation: `PERMITTED`
  - Public Demonstration: `PERMITTED`
  - Third-Party Cloud Transfer: `RESTRICTED UNLESS SYNTHETIC`. Real vehicle plates visible on public stock footage must be masked or replaced locally before transmitting frames to cloud inference APIs.
- **Available Annotations**: None.
- **Manual Annotation Requirement**:
  - Manual vehicle plate 4-corner quadrilateral annotation across 120 frames: ~15–20 minutes.
- **Classification**: **Public Demo Candidate** (requiring local synthetic target overlay).

---

### Candidate 3: EPFL PEViD-UHD Sequence (Surveillance Camera & Difficult Lighting)
- **Priority Capability**: Difficult lighting / wide-angle surveillance optics / ambient glare.
- **Official Dataset / Source**: EPFL MMSPG Privacy Evaluation Video Dataset UHD (PEViD-UHD).
  - Publisher Page: https://www.epfl.ch/labs/mmspg/downloads/pevid-uhd/
  - FTP Host: `tremplin.epfl.ch`
  - FTP Directory: `/PEViD/PEViD-UHD/`
  - Original Video Spec: 3840×2160 @ **30.0 fps** (Native 4K; requires local downscaling to comply with VEIL's $\le 1080p$ engine limit).
- **Access Status**: `PENDING / MANUAL FTP ACCESS REQUIRED`.
  - The EPFL server uses FTP protocol on host `tremplin.epfl.ch`. Exact individual video filenames inside the `/PEViD/PEViD-UHD/` directory remain unverified until an interactive FTP session is established.
- **Source Byte Size & Hash**: `unknown until FTP listing`.
- **Proposed Start / End Crop**: `2.0s` to `7.0s` (150 frames @ 30 fps).
- **License, Terms & Attribution**:
  - License: EPFL MMSPG Research License (https://www.epfl.ch/labs/mmspg/downloads/pevid-uhd/).
  - Terms: Academic, non-commercial research and evaluation only. Commercial redistribution prohibited.
- **Permissions**:
  - Local Evaluation: `PERMITTED` (Research diagnostic)
  - Public Demonstration: `RESTRICTED` (Non-commercial academic license excludes commercial hackathon product demo/redistribution).
  - Third-Party Cloud Transfer: `RESTRICTED` (Participant consent was executed strictly for academic privacy benchmarking at EPFL; transferring raw bystander footage to Meta cloud models violates project policy).
- **Available Annotations**: Person silhouette XML segmentation masks. **Zero screen or license plate quadrilaterals**.
- **Manual Annotation Requirement**:
  - 100% manual annotation required: ~25 minutes for 150 frames (surveillance target quadrilateral).
- **Classification**: **Private Research Diagnostic ONLY** (Strictly excluded from public demo and cloud transfer).

---

### Candidate 4: DAVAR Lab LSVTD (Camera Motion & Brief Occlusion — Proposed Slot)
- **Priority Capability**: Camera movement + brief occlusion / reappearance of planar text surface.
- **Official Dataset / Source**: Large-scale Scene Video Text Database (LSVTD), DAVAR Lab (Alibaba / TC11).
  - Publisher Page: https://davar-lab.github.io/dataset/lsvtd.html
  - Dataset Description: 129 video clips with multi-language bounding polygons and tracking IDs.
- **Access Status**: `PENDING AUTHOR / PORTAL ACCESS`.
  - Publisher page indicates downloads are hosted on Baidu NetDisk / TC11 portal, with contact via the official DAVAR portal. Direct HTTPS per-clip downloads are not accessible without portal credentials. Exact clip IDs remain unverified.
- **Source Byte Size & Hash**: `unknown until portal access`.
- **Proposed Start / End Crop**: `0.0s` to `4.0s` (approx. 120 frames).
- **License, Terms & Attribution**:
  - License: CC BY-NC-SA 4.0 (Creative Commons Attribution-NonCommercial-ShareAlike 4.0).
  - Credit: DAVAR Lab, 2020.
- **Permissions**:
  - Local Evaluation: `PERMITTED`
  - Public Demonstration: `RESTRICTED` (Non-commercial share-alike restricts commercial demo distribution).
  - Third-Party Cloud Transfer: `RESTRICTED` (Public street footage in China/Europe contains unconsented passersby and vehicles).
- **Available Annotations**: XML 4-corner text bounding polygons with consistent cross-frame tracking IDs.
- **Manual Annotation Requirement**:
  - Format parser from LSVTD XML to VEIL quad JSON (~10 minutes scripting).
- **Classification**: **Private Research Diagnostic ONLY**.

---

### Candidate 5: Ukrainian Synthetic Plates Archive (Plate Texture, Font & Extreme Tilt)
- **Priority Capability**: Static plate with realistic European font geometry, physical distortion, and varying tilt angles.
- **Official Dataset / Source**: Zenodo Record 13342103 ("Synthetic Ukrainian license plate dataset", Shpir, Shvai & Nakib, 2024).
  - DOI / URL: https://doi.org/10.5281/zenodo.13342103
  - Local Archive Path: `/Users/thecodekaizen/Documents/ChatGPT/Hackathons/veil/artifacts/private/datasets/ukrainian-plates/source.zip`
  - Archive MD5: `1c4a9db36e5f0a662ca7a5a0fcb513dc`
  - Archive Size: 247,025,841 bytes (~235.6 MB).
  - Test Split Evaluated: 6 test samples (`veil/artifacts/plate-dataset-001/`).
- **Access Status**: `VERIFIED` (Already downloaded and validated locally on disk).
- **Source Byte Size & Hash**:
  - Sample Crop: ~20 KB per still crop (193×72 px).
- **License, Terms & Attribution**:
  - License: Creative Commons Attribution 4.0 International (CC BY 4.0).
  - Credit: Mariia Shpir, Nadiya Shvai, Amir Nakib, 2024.
- **Permissions**:
  - Local Evaluation: `PERMITTED`
  - Public Demonstration: `PERMITTED` (with attribution)
  - Third-Party Cloud Transfer: `PERMITTED` (Purely synthetic generated plates; no real citizen identifiers).
- **Critical Gap & Honest Limitation**:
  - **STILL IMAGES ONLY**. The entire archive consists of static 193×72 plate crops. It is NOT continuous temporal camera video. Any video created from these is synthetic camera panning/animation, which tests font rendering and perspective distortion, but cannot measure shutter motion blur, autofocus hunting, or organic handheld shake.
- **Manual Annotation Requirement**:
  - 4-corner quad identification: ~2 minutes per still image.
- **Classification**: **Geometric & Texture Distortion Benchmark ONLY** (Explicitly labeled as still-image animation, NOT natural temporal footage).

---

### Candidate 6: User-Recorded Smartphone Screen
- **Priority Capability**: Angled phone screen, physical display refresh, finger/hand occlusion, real camera autofocus hunt.
- **Access Status**: **MISSING / DECLINED**.
  - The project maintainer explicitly declined to record a new self-recorded phone screen video today.
  - Per `ANTIGRAVITY_NATURAL_EXPERIMENTS.md` and user directives, this slot is recorded as **MISSING / DECLINED**.
  - No synthetic placeholders, fictitious permissions, or assumed licenses are assigned.
- **Permissions**: `null / unknown`.
- **Classification**: **MISSING EVIDENCE**.

---

## 3. Audited Screening Matrix & Capability Coverage

| # | Proposed Candidate | Capability Target | Access Status | License & Terms | Cloud Transfer | Video Type | Readiness | Gate Status |
|---|-------------------|-------------------|---------------|-----------------|----------------|------------|-----------|-------------|
| 1 | **Pexels Kampus 8347238** | Camera movement & angled screen | `VERIFIED` | Pexels License (Commercial) | `PERMITTED` (Synthetic overlay) | Real stock background (360×640 @ 12 fps) | Downloaded & Probed | **READY FOR INGESTION** |
| 2 | **Pexels Driving (Slot)** | Moving vehicle perspective | `PROPOSED SLOT` | Pexels License (Commercial) | `RESTRICTED UNLESS SYNTHETIC` | Real stock video | URL unverified | **NEEDS RESOLUTION & ANNOTATION** |
| 3 | **EPFL PEViD-UHD** | Difficult lighting / surveillance | `PENDING` | EPFL MMSPG (Non-commercial) | `RESTRICTED` | Real surveillance (30 fps 4K/HD) | FTP gate / No quads | **RESTRICTED RESEARCH ONLY** |
| 4 | **DAVAR Lab LSVTD (Slot)** | Brief occlusion & reappearance | `PENDING` | CC BY-NC-SA 4.0 | `RESTRICTED` | Real street video | Portal gate / Unverified | **RESTRICTED RESEARCH ONLY** |
| 5 | **Zenodo Ukrainian Plates** | Plate font & extreme tilt | `VERIFIED` | CC BY 4.0 | `PERMITTED` | **Still crops only** (Synthetic) | Local on disk (235 MB) | **SYNTHETIC BENCHMARK ONLY** |
| 6 | **Author Phone Screen** | Refresh, autofocus & hand occlusion | **MISSING / DECLINED** | `unknown` | `unknown` | Real phone camera | User declined capture | **MISSING EVIDENCE** |

---

## 4. Gap Analysis & Today's Decision Impact

1. **Inspected Source Limitations**:
   - Among the publicly accessible datasets screened (BDD100K, PP4AV, PEViD-UHD, LSVTD, CCPD):
     - BDD100K lacks plate-corner annotations and contains unconsented vehicles on public roads.
     - PP4AV is restricted under CC BY-NC-ND and contains real vehicles unconsented for cloud AI transfer.
     - PEViD-UHD has person silhouettes only, with no plate or screen quadrilaterals.
     - LSVTD requires third-party portal access and is restricted to non-commercial use.
     - CCPD and the Ukrainian archive consist exclusively of static image crops.
   - Cleared real-world plate footage satisfying commercial public demonstration, continuous temporal motion, and consented cloud transfer terms was **not found in the inspected repositories**.
2. **Current Verified Readiness**:
   - Ready real-camera hybrid asset: **1 of 6** (Pexels Kampus hybrid).
   - Ready synthetic still-crop benchmark: **1 of 6** (Ukrainian plates).
   - Research-restricted or access-gated slots: **2 of 6** (EPFL, LSVTD).
   - Stock candidate requiring direct URL resolution & quad labeling: **1 of 6** (Pexels Driving).
   - Declined user recording: **1 of 6** (Phone screen).
3. **Under the Six-Case Acceptance Gate (requiring $\ge 4/6$ fixed cases visually acceptable)**:
   - VEIL Natural Editing **cannot satisfy the 4/6 acceptance gate today**.
   - Attempting to pass the gate by relabeling still crops as continuous video, fabricating CDN download URLs, or guessing user recording files would violate engineering integrity agreements.

**Conclusion for Track A**:  
The dataset evidence supports **INSUFFICIENT EVIDENCE / NO-GO for general natural editing on arbitrary footage**, while the core redaction/verification baseline remains fully functional and ready for demonstration on its controlled synthetic and hybrid test sets.
