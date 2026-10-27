# SHOWME

### Build a process model from a demonstration.

Use the same model to inspect a learner’s attempt and test a different step order.

## The problem

Videos and manuals show a procedure, but they cannot inspect the learner’s workspace. SHOWME is a prototype for turning one task video into a reviewable process model, then comparing selected frames or a separate recording with that model.

## The product

SHOWME builds one evidence-linked **Process Model** from a bounded physical procedure. The same model supports three connected surfaces:

1. **Teach** — Record or upload a demonstration. SHOWME proposes objects, actions, states, transitions, and possible dependencies for human review.
2. **Do** — Check a selected camera frame or analyze a separate learner recording against the reviewed model. Inspect reported differences in the video.
3. **Simulate** — Change an action order and play through the resulting modeled states. The current simulator does not model physical forces or geometry.

The shared process model connects Teach, Do, and Simulate. The hackathon targets one safe, visually clear task. The prototype does not provide continuous tracking, proven recovery guidance, arbitrary task learning, or general-purpose physics.

## Current app screenshots

These screenshots were captured from the production build on October 27, 2026 at 1440 px width, before the current copy and navigation update. They include the blocked-attempt preview. Simulate uses an explicitly illustrative stacked-mount fixture. The Do screenshot shows the camera-off starting view; SAM grounding appears only after an explicit model call on a selected frame. The images show prototype flows, not proof that physical mistakes are reliably detected.

| Teach | Do |
|---|---|
| ![Teach: capture a demonstration](design/screenshots/01-teach.jpg) | ![Do: camera preview and learner clip workflow](design/screenshots/02-do.jpg) |

| Simulate | What-if result |
|---|---|
| ![Simulate: reorder the procedure](design/screenshots/03-simulate.jpg) | ![What-if simulation stops at a confirmed missing prerequisite](design/screenshots/04-simulate-what-if.jpg) |

## Product design concepts

These are design references, not screenshots of implemented screens or proof that physical-task understanding works. The depicted block assembly is illustrative; the evaluation task will be selected after inspecting the LEGO set.

![Teach concept: demonstration review and candidate Skill Model](design/mockups/03-teach-skill-model-review.png)

See the [full mockup inventory](design/mockups/README.md) for the Do and Simulate concepts and their limitations.

## What works now

- Teach can capture a short demonstration from the browser camera or accept an uploaded video and narration, save the clip locally, then ask Muse Spark for a structured candidate process model with timestamped evidence.
- A person reviews the candidate. Model-proposed prerequisites remain hypotheses unless explicitly mapped to a state and confirmed by the reviewer.
- Do can capture and save a learner clip in-browser or accept an upload, then compare it with the reviewed process model; it can also request a single camera-frame check. These are discrete observations, not continuous tracking.
- Simulate lets a person reorder actions, use timed Play/Pause/Replay or manual stepping, and inspect the first confirmed blocker. A sequence absent from one demonstration is reported as **unobserved**, not impossible.
- Skill candidates and human-reviewed constraint mappings persist in browser-local storage. Uploaded clips and camera frames are not stored by the app after the request.

The current simulation view is procedural rather than a geometry or physics simulator. The matched demonstration / correct attempt / mistake / recovery evaluation is still pending with the selected task.

## Run locally

From the repository root, install the optional API dependencies and start the local SHOWME API:

```sh
python3 -m venv backend/.venv
backend/.venv/bin/pip install -e 'backend[api,meta]'
PYTHONPATH=backend backend/.venv/bin/uvicorn showme.api:app --reload --port 8000
```

Set `MODEL_API_KEY` in the repository’s ignored local `.env` file or in the API process environment. Never commit the key. Model calls can use hackathon API credits.

In a second terminal, start the web app:

```sh
cd apps/web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The app uses the local API at `http://localhost:8000` by default.

## Product and build documents

- [Locked product definition](docs/PRODUCT.md)
- [Hackathon build plan and evidence status](docs/SHOWME_BUILD_PLAN.md)
- [Proof-of-magic experiment](docs/SHOWME_PROOF_OF_MAGIC.md)
- [Final app plan](docs/SHOWME_APP_PLAN.md)
- [Interactive simulation design](docs/SHOWME_SIMULATION_DESIGN.md)
- [Three-minute demo flow](design/flows/demo-flow.md)
- [Daily progress log](docs/DAILY_LOG.md)

## Meta model roles

Muse Spark performs structured interpretation of demonstrations and learner observations. In Do, SAM 3.1 can segment one selected Skill Model object on either a manual camera snapshot or a user-selected timestamp from a recorded learner divergence. Both are opt-in single-frame calls; neither is live tracking. The integration uses Meta's official `meta-sam-parser` to decode segmentation records. Muse Voice is still a possible later addition. SAM has not yet been validated on the chosen LEGO task or against real footage from a separate learner.

## Hackathon and responsible use

Meta Global AI Developer Hackathon 2026 · Indie Developer / Push the Frontier. The submission needs a public repository and a demo video of at most three minutes. Clearly identify work created during the October 27–November 4 build period.

Use safe tasks and footage you have permission to record and share. Avoid faces and private details. Do not commit API keys, private recordings, raw model payloads, or evaluation labels. SHOWME provides guidance; it does not control tools or machinery.
