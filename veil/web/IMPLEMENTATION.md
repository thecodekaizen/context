# VEIL Reference Frontend Implementation Checklist

Reference frontend for VEIL: an API-first multimodal video privacy engine (Detect. Redact. Verify).

## Planned

- [x] Phase A: Design and data contracts
  - [x] Write `veil/web/DESIGN.md`: visual tokens, palette, typography, responsive behavior, state matrix.
  - [x] Create TypeScript types matching `veil.core.models` and recorded artifacts.
  - [x] Build typed recorded example manifest with real timestamps, geometry, and explicit not-run labels.
- [x] Phase B: Recorded evidence workspace
  - [x] Video desk with 4 MP4 stages: `input.mp4`, `redacted.mp4`, `repaired.mp4`, `protected.mp4`.
  - [x] Paired synchronized comparison (source vs export) with single-toggle mode for mobile.
  - [x] Timeline scrub bar with visual categories (Face, Plate, Printed Phone, Spoken Speech).
  - [x] Hero verification surface: highlight remaining phone number at 00:07.500 in export, inspect exposed frame, show rejected single-digit repair, and show corrected whole-field repair.
  - [x] Scoped final review display: "No exposure reported in 3 sampled frames (00:02.000, 00:07.500, 00:16.000). Other frames may contain missed exposures."
  - [x] Receipt modal and MP4 download actions.
- [x] Phase C: Live local API integration
  - [x] API client for loopback server (`http://127.0.0.1:8018`).
  - [x] File upload with size/format validation (100 MiB, 60s, 1080p, audio required).
  - [x] Submit reviewed timeline and render redacted export.
  - [x] Clear separation between "Recorded example · saved real inference" and "Current job".
  - [x] Honest disabled states when automatic detection/verification routes are not yet exposed.
  - [x] Graceful fallback when local API server is offline.
- [x] Phase D: Polish, accessibility and verification
  - [x] Keyboard navigation, visible focus indicators, accessible ARIA attributes.
  - [x] Contrast compliance and `prefers-reduced-motion` support.
  - [x] Unit tests for data adapters, mode separation, and receipt validation.
  - [x] Responsive design verified at 1440×900, 1280×800, and 390×844.
  - [x] Screenshots captured and committed under `veil/web/docs/screenshots/`.
  - [x] Frontend README with run and build instructions.

## Implemented

- Complete React + TypeScript + Vite frontend in `veil/web/`
- Film inspection desk visual system matching `#090C10` / `#12171E` / `#69DDF3` specifications
- Real synthetic media in `public/artifacts/`: `input.mp4`, `redacted.mp4`, `repaired.mp4`, `protected.mp4`, inspection frames, and latest live-pipeline-003 corrected shots (`final-7600.jpg`, `final-2000.jpg`, `final-16000.jpg`, `final-export.mp4`)
- Verification hero highlighting the omitted printed phone number at `00:07.500` with the failed 1-digit repair progression
- Scoped 3-sample disclaimer with no false zero-leak guarantees
- Machine-readable receipt modal with SHA-256 hashes and cost accounting
- Python SDK drawer with copyable code snippet
- Unit test suite protecting honest status labels, null confidence, and upload limits
- Comprehensive READMEs with embedded corrected scene shots across root `README.md`, `veil/README.md`, and `veil/web/README.md`

## Verified

- `cd veil/web && npm test`
  - Output: 6 passed, 0 failed (211ms)
- `cd veil/web && npm run typecheck && npm run build`
  - Output: 0 TypeScript errors, bundle generated in 398ms
- Screenshots verified in `veil/web/docs/screenshots/`:
  - `desktop-1440x900.png` (1440×900 standard desktop)
  - `laptop-1280x800.png` (1280×800 laptop viewport)
  - `mobile-390x844.png` (390×844 mobile viewport)

## Blocked / Limitations

- Automatic detection and verifier endpoints (`/v1/jobs/{id}/detect`, `/v1/jobs/{id}/verify`) are not yet implemented in Python API; the live mode only renders client-supplied reviewed timelines.
- Recorded example uses saved real Meta model inference from smoke test 001.
