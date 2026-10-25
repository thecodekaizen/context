# Repository working agreements

## Product boundary

THREAD is a multimodal personal creative intelligence system. It turns personal history into time-aware memories, discovers evidence-backed patterns, contradictions, evolution, and cross-domain connections, investigates candidates skeptically, interviews the user to develop human-confirmed insights, and only then creates artifacts.

## Day-0 constraints

- Do not implement product features before the Day-1 plan and scope are reviewed.
- The discovery engine must run from the CLI before frontend work begins.
- Keep P0 narrow; use the kill list in `docs/PLAN.md` to protect the demo.
- Every surfaced claim must link to inspectable evidence and indicate uncertainty. Never present model-generated interpretation as a fact or user-confirmed insight.
- Treat personal data as sensitive: use only consented/imported data, minimize retention, and make provenance visible.
- Keep model providers behind an adapter. Do not couple core logic to Meta Model API response shapes.
- Update docs when a decision changes; mark assumptions as assumptions.

## Visual source of truth

Use `design/DESIGN_SYSTEM.md` and the mockups in `design/mockups/` as the UI reference. Avoid generic SaaS dashboards and chat-first interaction. The experience should feel like a living research journal and intelligence map.
