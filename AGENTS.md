# Repository working agreements

## Product boundary

THREAD is a multimodal creative-project intelligence system. It turns dated project artifacts into temporal memories, discovers evidence-backed changes in themes and direction, investigates candidates skeptically, lets the creator confirm or correct findings, and only then creates artifacts.

## Hackathon constraints

- The repository, planning docs, and mockups are pre-event groundwork; clearly distinguish them from product features built during Oct 27–Nov 4.
- The official demo is three minutes and must highlight work created during the event.
- The public submission must use at least one Meta model in the working product path.
- Keep the project about evolution in creative work, not personality analysis or generic RAG.
- Do not implement product features before the kickoff and Day-1 scope are reviewed.
- The discovery engine must run from the CLI before frontend work begins.
- Keep P0 narrow; use the kill list in `docs/PLAN.md` to protect the demo.
- Every surfaced claim must link to inspectable evidence and indicate uncertainty. Never present model-generated interpretation as a fact or user-confirmed insight.
- Treat personal data as sensitive: use only consented/imported data, minimize retention, and make provenance visible.
- Keep model providers behind an adapter. Do not couple core logic to Meta Model API response shapes.
- Update docs when a decision changes; mark assumptions as assumptions.

## Visual source of truth

Use `design/DESIGN_SYSTEM.md` and the mockups in `design/mockups/` as the UI reference. Avoid generic SaaS dashboards and chat-first interaction. The experience should feel like a living research journal and intelligence map.
