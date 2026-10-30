# Dark Silicon workstation

The October 30 frontend overhaul keeps API bindings and deterministic grounding in the backend unchanged.

## Visual and interaction decisions

- Obsidian canvas, three elevated surfaces, crisp borders and inner highlights. Evidence blue means matched footage; amber identifies measured cuts; emerald and rose distinguish retained and removed geometry.
- System sans typography avoids a remote font dependency. Monospaced, tabular millisecond timecodes keep playback telemetry stable.
- Loaded investigations collapse intake and reference-library setup, putting evidence above configuration.
- One shared `ForensicPlayer` serves the comparator and dossier source comparison. It preserves each parent's existing synchronization handler and citation seeking.
- Keyboard transport: Space toggles playback, J steps backward at 1×, K pauses, L starts forward playback and repeats up to 4×, brackets navigate measured cuts, M toggles curtain comparison. Text fields and native control activation retain their keyboard behavior.
- Confidence samples are resampled from reported matched intervals at a 4 Hz display cadence (up to the supported ten-minute duration), not raw per-frame features or audio amplitude. SVG keeps the strip bounded at narrow widths.
- Crop calipers use API coordinates, source resolution and area fractions. The overlay visualizes measured crop geometry; it does not claim that a fresh SAM inference ran for the current case.
- Audit badges distinguish deterministic interval grounding and citation-range validation from semantic correctness. They do not claim zero hallucinations, cryptographic signing, SOC-2 compliance or ISO certification.
- Export uses available media SHA-256 hashes and mean matched visual interval confidence. Missing values are explicit. Browser print supports saving the audit summary as PDF.
- Evaluation values, case counts and pass states come from `/api/benchmark/results`; loading and error states do not fabricate successful metrics. Speed controls remain benign controls. The two served demo cases offer exact replay; other rows expose measured result traces without substituting an unrelated video.

## Verification

`web/tests/workstation.spec.ts` exercises real deterministic demo endpoints, transport, curtain position, acoustic omission navigation, crop opacity, export, narrow layouts, evaluation filtering and fetch failure. A clearly marked mocked review tests citation presentation and seeking without calling a model. Text tokens are checked against all four surfaces at the WCAG AA 4.5:1 threshold. This is not a full accessibility certification.

Run against a local API and Vite server:

```sh
cd web
CONTEXT_BASE_URL=http://127.0.0.1:5173 npm run test:e2e -- tests/workstation.spec.ts --workers=1
npm run build
```
