# SUBMISSION checklist (human-only steps)

**Internal deadline: Wed Nov 4 2026, 22:30 IST (noon ET).**
Official hard stop: Wed Nov 4, 9 PM ET = Thu Nov 5, 07:30 IST. Do not rely on the buffer.

## Only you can do these
- [ ] Re-read the official rules (eligibility, track, video length, what counts as "built during the hackathon", public repo requirement, any required licence).
- [ ] Claim the Meta API credits with a low-limit card. Set the spend cap before first use. Do not paste keys into the repo; `.env` stays local.
- [ ] Re-render `demo-video/renders/context-demo-3min.mp4` (the committed render predates the script edits), then fill the README video size / release link (currently TBD).
- [ ] Record the narrated clip from `docs/demo-script.md` (266 words, about 3 min). Follow its recording notes: cut is four seconds; say "evidence"; label the Muse panel "saved response".
- [ ] Decide what stays in the public tree (see "Before making public" below), then make the repo public.
- [ ] Post the demo on X (link repo and video; keep the corner-badge disclosure: scripted cuts, saved Muse response).
- [ ] Fill in and submit the form: repo URL, video URL, track (Solo / Indie), description. Reuse the README wording; no "proof" / "verdict".
- [ ] Open the submitted page in a logged-out window and confirm the repo and video load.

## Before making public (decisions for you)
Untracked on Oct 31 (still on disk, in .gitignore): .hackathon/, Codex/Antigravity handoffs, handoff-followup, docs/review/. Still tracked on purpose: CLAUDE.md files, .claude/ (not settings.local.json), docs/AUDIT.md, docs/HANDOFF.md. History still contains the untracked files.

## Verified (Oct 31)
- Clean clone of origin main (7ff90aa): cold `docker build --no-cache` 111 s; container ready in 0.6 s; `POST /api/demo/hero` returns 200 in under 0.1 s without any API key.
- gitleaks over 54 commits: no leaks. No `.env` tracked. Largest tracked file: 11.3 MB demo render.
