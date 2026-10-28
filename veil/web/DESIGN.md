# VEIL Reference Interface Design System (DESIGN.md)

**Product:** VEIL — Detect. Redact. Verify.  
**Role:** Reference inspection desk for an embeddable video privacy engine.

---

## 1. Visual Theme & Philosophy

VEIL is designed as a **precision film inspection desk** rather than a generic SaaS marketing dashboard. The video footage occupies the primary visual focus, supported by deliberate, restrained telemetry and clear evidence.

### Color Tokens

| Token | Hex Value | Semantic Usage |
|---|---|---|
| `--color-bg-base` | `#090C10` | Canvas / viewport background |
| `--color-panel-bg` | `#12171E` | Sidebar, timeline container, card surface |
| `--color-control-bg` | `#1B2430` | Button, input, raised scrubber background |
| `--color-control-hover` | `#232E3D` | Interactive control hover state |
| `--color-border-subtle` | `#2A3543` | Dividers, panel borders, hairline outlines |
| `--color-border-focus` | `#69DDF3` | Focus rings, active selections |
| `--color-text-main` | `#F3F6FA` | Primary headings, active values, timestamps |
| `--color-text-secondary` | `#A8B5C5` | Labels, supporting copy, metadata |
| `--color-text-muted` | `#6B7B8E` | Inactive tracks, empty states, captions |
| `--color-accent-protect` | `#69DDF3` | Protected region, track selection, active stage |
| `--color-accent-amber` | `#FFBE66` | Potential exposure, unreviewed finding |
| `--color-accent-red` | `#FF786F` | Confirmed residual exposure requiring repair (Hero) |
| `--color-accent-mint` | `#84E0B4` | Completed operation, verified clean sample, audit pass |

> **Rule:** Color is never used alone to convey state. Every color is paired with a distinct textual label and status icon.

---

## 2. Typography

- **Primary Sans:** System UI sans stack (`system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`) with tabular numerals enabled (`font-variant-numeric: tabular-nums`).
- **Monospace:** System monospace (`ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace`) reserved for:
  - Exact timestamps (`00:07.500`)
  - Finding and Job IDs (`smoke-001`, `face-track-01`)
  - Code snippets and SDK samples

### Scale & Hierarchy

- **Title / Hero:** 20px / 1.3, bold (600)
- **Section Heading:** 14px / 1.4, semibold (600), uppercase tracking +0.05em
- **Body / Main Text:** 14px / 1.5, regular (400)
- **Metadata / Labels:** 12px / 1.4, medium (500)
- **Monospace Stamp:** 11px / 1.4, regular (400)

---

## 3. Spacing, Geometry & Transitions

- **Spacing Rhythm:** `4px`, `8px`, `12px`, `16px`, `24px`, `32px`
- **Border Radius:** `8px` for buttons, inputs, chips; `12px` for major desk panels.
- **Borders:** `1px solid var(--color-border-subtle)`
- **Shadows:** Minimal, restrained elevation (`0 2px 8px rgba(0, 0, 0, 0.4)`)
- **Transitions:**
  - Micro-interactions (hover, focus, chip toggle): `140ms`–`200ms` cubic-bezier(0.2, 0, 0, 1)
  - Layout / drawer / panel state shifts: `250ms`–`350ms` ease-out
- **Reduced Motion:** When `prefers-reduced-motion: reduce` is active, animations and transitions are disabled (`transition: none !important; animation: none !important`).

---

## 4. Layout Architecture (1440×900 Target Desktop)

```text
+------------------------------------------------------------------------------------+
| [VEIL Wordmark]  Detect. Redact. Verify.          [Mode: Recorded Example / Job]   |
| Stage Nav: Import -> Detect -> Redact -> Verify -> Repair -> Export   [Status: OK] |
+----------------------------------------------------+-------------------------------+
|                                                    | SELECTED FINDING / HERO PANEL |
|                                                    | ----------------------------- |
|                 VIDEO INSPECTION DESK              | Category · Time · Evidence    |
|             (Large player or Paired Split)         | Status & Actions              |
|                                                    |                               |
|                                                    | Hero: Confirmed Residual      |
|                                                    | "A phone number is still      |
|                                                    |  visible in export"           |
+----------------------------------------------------+-------------------------------+
| TIMELINE / TRACK SCRUBBER (Face | Plate | Printed Phone | Speech)                  |
| Play/Pause · Seek Bar · 00:07.500 / 00:18.000 · Toggle Overlays · Split/Single     |
+------------------------------------------------------------------------------------+
| Audit Scope Summary & Limitations                  [Download MP4] [View Receipt]   |
+------------------------------------------------------------------------------------+
```

### Responsive Breakpoints

- **Desktop (>= 1280px):** Two-column inspection desk with video player occupying 68% width, sidebar panel occupying 32% width.
- **Tablet / Narrow Desktop (960px - 1279px):** Two-column compact or stacked, video player maintains 16:9 ratio.
- **Mobile (< 960px, tested down to 390×844):** Single-column stacked layout. Video player on top, compact playback controls, timeline bar, followed by the selected finding and verification cards below. Source/Export toggle replaces side-by-side split. No horizontal page scroll.

---

## 5. State Matrix

| Stage | Mode: Recorded Example | Mode: Live Local Job |
|---|---|---|
| **Import** | Displays synthetic clip specs (18s, 1080p, 10 fps). Button: "Load Recorded Example". | Dropzone for local MP4 (<=100MB, <=60s). Button: "Upload Video". |
| **Detect** | Shows saved Meta SAM, Voice, and Spark findings with exact timestamps and boxes. | Shows "Detection not yet exposed on loopback API; submit reviewed timeline." |
| **Redact** | Loads `redacted.mp4` (face/plate covered, audio muted, printed phone omitted). | Sends POST `/v1/jobs/{id}/redact` with timeline; renders export. |
| **Verify (Hero)** | **Hero finding:** Omitted printed phone flagged at `00:07.500`. Shows `export-check.jpg`. "Inspect exposed frame" seeks export. | Shows "Privacy verifier endpoint pending; media decode check only." |
| **Repair** | Step 1: Rejected 1-digit repair (`repaired.mp4`). Step 2: Corrected whole-field repair (`protected.mp4`). | Disabled until repair endpoint is implemented. |
| **Export** | Shows final 3-sample pass (`protected-2000.jpg`, `7500`, `16000`). Downloads `protected.mp4` & `receipt.json`. | Downloads rendered `export.mp4` and job receipt. |

---

## 6. Tone & Claims Boundary

1. Never display "100% Private", "Zero Leaks", "Guaranteed", or "Certified".
2. Always pair the final pass with its explicit scope disclaimer:
   > *"No exposure reported in 3 sampled frames (00:02.000, 00:07.500, 00:16.000). Other frames may contain missed exposures."*
3. Persistent badge on archived demo: `Recorded example · saved real inference`.
