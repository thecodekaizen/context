---
description: Read-only audit of the repo against the gates; writes docs/AUDIT.md and a KEEP/FIX/PIVOT recommendation
model: opus
---
Do a read-only audit. Do NOT modify code. Be blunt.
1. Read CLAUDE.md and docs/HANDOFF.md. Run `git log --oneline -15` and `git status --short`.
2. Run `bash scripts/t.sh` and `npm run build` once each. Record pass/fail only.
3. Locate the frozen eval results file; report recall, boundary error, benign false-alarm counts as stored.
4. Find the demo path: how many commands from a clean clone to the hero clip result? Is `.env.example` present?
5. Check what Muse Spark and SAM actually do on the hero clip (read code, do not call APIs unless I say so).
6. Check docs/demo-script.md and demo-video/story.json numbers against the results file.
Write docs/AUDIT.md (max 60 lines): a table of gates G1..G6 with PASS/FAIL and one evidence line each:
G1 tests+build green; G2 eval reproducible from committed files; G3 clean-clone demo path <= 3 commands;
G4 Meta model contributes on hero clip (state exactly what); G5 domain policy enforced; G6 script numbers match data.
Then recommend: KEEP (all pass), FIX (fails fixable in <= 4 hours; list tasks with hour estimates), or
PIVOT (only if G1/G2/G3 cannot be fixed by Sun Nov 1 noon IST). Reply in 5 lines.
