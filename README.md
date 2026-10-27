<div align="center">

# SHOWME

### Demonstrations into understanding.

**Show it once. Learn it. Simulate it. Teach it.**

</div>

---

Tutorials can show someone what happened. SHOWME aims to understand the process well enough to watch another person try it, notice when their physical state diverges, and help them recover.

    Expert demonstration
             ↓
    Objects, actions, states, dependencies
             ↓
    Process model
             ↓
    Observe another attempt
             ↓
    Grounded guidance and recovery
             ↓
    Procedural “what if?” simulation (after P0)

## First proof

The first milestone is a constrained, prerecorded physical task: learn from one expert clip, observe a correct learner attempt and deliberate mistake, ground the relevant object visually, then recognize recovery. The experiment comes before product UI. It does not claim general physical intelligence or physics simulation.

See the proof-of-magic experiment in docs/SHOWME_PROOF_OF_MAGIC.md for the protocol, evidence rules, first milestone, and kill criteria.

## Meta models

The intended roles are substantive and distinct: Muse Spark interprets the demonstration and learner attempt; SAM 3.1 segments and tracks relevant objects for visual grounding; Muse Voice Transcribe may provide a separate narration transcript. Capabilities and costs must be checked against the current API and proved in the experiment before they become demo claims.

## Existing repository

This repository began as THREAD. Its Python CLI, FastAPI setup, Meta API adapter patterns, evaluation habits, and Next.js toolchain may be useful infrastructure. THREAD-specific product logic, datasets, experiments, and UI are legacy; they are not SHOWME specifications. See AGENTS.md for current working agreements. Inspect legacy material before reuse; preserve useful infrastructure.

## Hackathon

Meta Global AI Developer Hackathon 2026 · Indie Developer / Push the Frontier. The public submission needs to clearly identify work created during the Oct 27–Nov 4 building period, use Meta models in the working path, and include a three-minute demo. This is a local prototype first; no accounts, production infrastructure, robot control, or general-purpose task support in P0.

## Safety and data

Use a safe, repeatable task and clips the team has permission to record and share. Keep faces and private details out of footage. Never commit API keys, private recordings, raw model payloads, or evaluation labels. The system gives guidance only; it does not control tools or machinery.
