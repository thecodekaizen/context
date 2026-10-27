# Backend experiments

The new `showme` package is the active hackathon direction. The earlier
`thread_engine` remains available as legacy research; do not extend it for
SHOWME features.

## Prepare local video

```bash
PYTHONPATH=backend backend/.venv/bin/python -m showme prepare-video path/to/clip.mp4
```

This uses `ffprobe` and `ffmpeg` locally. It writes a manifest and timestamped
JPEG frames under `.showme-runs/`; the source is not modified or uploaded.

## Learn from one demonstration

Install the optional SDK once with `pip install -e 'backend[meta]'`, then run:

```bash
PYTHONPATH=backend backend/.venv/bin/python -m showme learn-video path/to/demo.mp4
```

This uploads one MP4 to the Meta Model API, asks Muse Spark for a structured
candidate process, records token usage, requests one-hour file expiry, and tries
to delete the uploaded file after inference. The local run directory is ignored
by Git. A model response is a hypothesis, not ground truth; check its timestamped
evidence before using it for learner-state evaluation. The cross-reference
validator is an intentional first learning exercise and currently reports as
pending until implemented.

## Compare a learner attempt

After reviewing the learned process artifact, compare one neutral-named learner
clip against it:

```bash
PYTHONPATH=backend backend/.venv/bin/python -m showme observe-video \
  .showme-runs/learned/your-run/process.json path/to/learner.mp4
```

The observer receives the learned process and one video. It never receives the
human evaluation key. It writes timestamped events and divergence evidence to
`.showme-runs/observed/`; local validation rejects unknown state/object IDs,
invalid timestamps, and unsupported recovery claims. A passing validator only
means the response is structurally grounded in the process IDs and clip time; it
does not prove the model understood the physical task.
