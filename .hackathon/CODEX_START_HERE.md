# CODEX EXECUTION DIRECTIVE — CONTEXT VIDEO EVIDENCE WORKSTATION

**Target:** Meta Global AI Developer Hackathon 2026  
**Deadline:** November 4, 2026, 9:00 PM ET  
**Reference Document:** See [CODEX_HANDOFF.md](../CODEX_HANDOFF.md) in the project root for full architectural details.

---

## 1. Operating Mode: Hackathon Principal Engineer

You are operating in the live public repository for **CONTEXT** (`https://github.com/thecodekaizen/context`).
- All foundation engineering, alignment algorithms, SAM 3.1 spatial crop detection, and demo video rendering are **COMPLETE AND PASSING**.
- **132/132 pytest tests pass.**
- **Frozen 30-edit benchmark suite passes with 100% recall, 0.0s boundary error, and 0.0% false alarms.**
- **Demo video rendered:** `demo-video/renders/context-demo-3min.mp4` (180.00s Full HD).

---

## 2. Invariant Architecture Principles

1. **Deterministic Alignment First:**
   - 4Hz visual cosine matching + normalized audio cross-correlation.
   - If no correspondence is found, output is strictly `"no material omission"`.
   - Never allow foundation models to guess or hallucinate ungrounded omissions.
2. **Domain Whitelist:**
   - Developer tutorials, software benchmark demos, and commercial product claims ONLY.
   - No politics, elections, news, war, or real public figures.
3. **Rule 9 (Authentic Builder Voice):**
   - The master demo video currently uses silent audio placeholders.
   - The human builder records authentic narration on Tuesday, Nov 3 matching `docs/demo-script.md`.
4. **Git Protocol:**
   - In sandbox mode, use `git commit --no-gpg-sign`.
   - Git push requires `BypassSandbox: true`.

---

## 3. Quick Verification Commands

```bash
# 1. Run all tests
.venv/bin/pytest -q

# 2. Check code quality
.venv/bin/ruff check backend scripts && .venv/bin/ruff format --check backend scripts

# 3. Check frontend build
cd web && npx tsc --noEmit && npx vite build && cd ..

# 4. Run frozen evaluation suite
PYTHONPATH=backend .venv/bin/python scripts/run_execution_eval.py

# 5. Check master demo video
ffprobe demo-video/renders/context-demo-3min.mp4
```

For full context, test manifests, and architecture maps, read `CODEX_HANDOFF.md` and `docs/ANTIGRAVITY-HANDOFF.md`.
