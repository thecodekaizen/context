"""Command-line utilities for the SHOWME proof-of-magic experiment."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from .media import make_model_video, prepare_video
from .meta import MuseVideoLearner
from .observe import observe_video, validate_observation
from .process import validate_references


def _default_output(video: Path, phase: str) -> Path:
    root = Path(__file__).resolve().parents[2]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return root / ".showme-runs" / phase / f"{video.stem}-{stamp}"


def main() -> int:
    parser = argparse.ArgumentParser(prog="showme", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    prepare = commands.add_parser(
        "prepare-video",
        help="inspect a local video and extract timestamped frame samples",
    )
    prepare.add_argument("video", type=Path, help="local source video; not uploaded")
    prepare.add_argument("--output", type=Path, help="new output directory")
    prepare.add_argument("--sample-every", type=float, default=1.0, help="requested interval in seconds")
    prepare.add_argument("--max-frames", type=int, default=24, help="maximum frame count (1–240)")

    learn = commands.add_parser(
        "learn-video",
        help="upload one MP4 to Muse Spark and save a candidate process model",
    )
    learn.add_argument("video", type=Path, help="local MP4 demonstration; uploaded for inference")
    learn.add_argument("--output", type=Path, help="new run directory")

    observe = commands.add_parser(
        "observe-video",
        help="compare a learner MP4 with a learned process and save evidence-linked observations",
    )
    observe.add_argument("process", type=Path, help="learned process JSON")
    observe.add_argument("video", type=Path, help="local learner MP4; uploaded for inference")
    observe.add_argument("--output", type=Path, help="new run directory")

    args = parser.parse_args()
    phase = {"learn-video": "learned", "observe-video": "observed"}.get(args.command, "prepared")
    output = args.output or _default_output(args.video, phase)
    if args.command == "learn-video":
        return _learn_video(args.video, output)
    if args.command == "observe-video":
        return _observe_video(args.process, args.video, output)

    try:
        manifest = prepare_video(
            args.video,
            output,
            sample_every_seconds=args.sample_every,
            max_frames=args.max_frames,
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"showme: {exc}", file=sys.stderr)
        return 2

    print(json.dumps({
        "prepared_directory": str(output.resolve()),
        "duration_seconds": manifest["source"]["duration_seconds"],
        "frames_written": len(manifest["frames"]),
        "audio_present": manifest["source"]["audio_present"],
        "source_sha256": manifest["source"]["source_sha256"],
    }, indent=2))
    return 0



def _learn_video(video: Path, output: Path) -> int:
    try:
        manifest = prepare_video(video, output / "media", sample_every_seconds=1, max_frames=24)
        model_video = make_model_video(video, output / "model-input.mp4")
        learner = MuseVideoLearner.from_env()
        process = learner.learn(output / "model-input.mp4", duration_seconds=manifest["source"]["duration_seconds"])
        process["_run"]["source_media"] = manifest["source"]
        process["_run"]["model_media"] = model_video
        validate_references(process, duration_seconds=manifest["source"]["duration_seconds"])
        process["_validation"] = "passed"
        (output / "process.json").write_text(
            json.dumps(process, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"showme: {exc}", file=sys.stderr)
        return 2

    usage = process.get("_run", {}).get("usage", {})
    print(json.dumps({
        "run_directory": str(output.resolve()),
        "process_file": str((output / "process.json").resolve()),
        "model": process.get("_run", {}).get("model"),
        "states": len(process.get("states", [])),
        "transitions": len(process.get("transitions", [])),
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "validation": process.get("_validation", "not_run"),
    }, indent=2))
    return 0



def _observe_video(process_path: Path, video: Path, output: Path) -> int:
    try:
        process = json.loads(process_path.read_text(encoding="utf-8"))
        if not isinstance(process, dict):
            raise ValueError("learned process must be a JSON object")
        source_duration = process.get("_run", {}).get("source_media", {}).get("duration_seconds")
        validate_references(process, duration_seconds=source_duration)
        manifest = prepare_video(video, output / "media", sample_every_seconds=1, max_frames=24)
        model_video = make_model_video(video, output / "model-input.mp4")
        learner = MuseVideoLearner.from_env()
        observation = observe_video(
            learner,
            output / "model-input.mp4",
            process,
            manifest["source"]["duration_seconds"],
        )
        validate_observation(observation, process, manifest["source"]["duration_seconds"])
        observation["_run"]["source_media"] = manifest["source"]
        observation["_run"]["model_media"] = model_video
        observation["_run"]["process_file"] = str(process_path.expanduser().resolve())
        (output / "observation.json").write_text(
            json.dumps(observation, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"showme: {exc}", file=sys.stderr)
        return 2

    print(json.dumps({
        "run_directory": str(output.resolve()),
        "observation_file": str((output / "observation.json").resolve()),
        "events": len(observation.get("events", [])),
        "divergences": len(observation.get("divergences", [])),
        "recovery_status": observation.get("recovery_status"),
        "usage": observation.get("_run", {}).get("usage", {}),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
