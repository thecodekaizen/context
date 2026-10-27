"""Explicit, auditable Muse Spark video calls for the SHOWME experiment."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
import base64

from .process import PROCESS_SCHEMA

MODEL = "muse-spark-1.3"
PROMPT_VERSION = "showme-video-analysis-v2"


class MuseSparkClient:
    def __init__(self, api_key: str, model: str = MODEL) -> None:
        try:
            from openai import APIError, OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the optional Meta client with: pip install -e '.[meta]'") from exc
        self.client = OpenAI(api_key=api_key, base_url="https://api.meta.ai/v1", max_retries=0)
        self._api_error = APIError
        self.model = model

    @classmethod
    def from_env(cls) -> "MuseSparkClient":
        api_key = os.environ.get("MODEL_API_KEY") or _read_repo_key()
        if not api_key:
            raise ValueError("Set MODEL_API_KEY in the local .env file or environment")
        return cls(api_key=api_key, model=os.environ.get("SHOWME_META_MODEL", MODEL))

    def learn(self, video: Path, *, duration_seconds: float, narration: str = "") -> dict[str, Any]:
        """Infer a candidate process from a demonstration clip."""
        return self.analyze_video(
            video,
            prompt=_learning_prompt(duration_seconds, narration),
            schema=PROCESS_SCHEMA,
            schema_name="showme_process_model",
            max_output_tokens=3000,
        )

    def analyze_video(
        self,
        video: Path,
        *,
        prompt: str,
        schema: dict[str, Any],
        schema_name: str,
        max_output_tokens: int = 3000,
    ) -> dict[str, Any]:
        """Upload one video, request strict JSON, and clean up the remote file."""
        video = video.expanduser().resolve()
        if not video.is_file():
            raise ValueError(f"video file does not exist: {video}")
        uploaded = None
        try:
            with video.open("rb") as media:
                uploaded = self.client.files.create(
                    purpose="user_data",
                    file=media,
                    expires_after={"anchor": "created_at", "seconds": 3600},
                )
            return self._structured_response(
                [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_file", "file_id": uploaded.id},
                ],
                schema=schema,
                schema_name=schema_name,
                max_output_tokens=max_output_tokens,
                remote_file_id=uploaded.id,
            )
        except self._api_error as exc:
            raise RuntimeError(
                "Meta Model API request failed. Automatic retries are disabled to avoid "
                "repeating a potentially billable request; inspect billing before retrying."
            ) from exc
        finally:
            if uploaded is not None:
                try:
                    self.client.files.delete(uploaded.id)
                except Exception:
                    # The one-hour expiry is the fallback if remote cleanup fails.
                    pass

    def analyze_image(
        self,
        image: Path,
        *,
        prompt: str,
        schema: dict[str, Any],
        schema_name: str,
        max_output_tokens: int = 1200,
    ) -> dict[str, Any]:
        """Analyze one local image as a data URL; no image file is uploaded or retained."""
        image = image.expanduser().resolve()
        if not image.is_file():
            raise ValueError(f"image file does not exist: {image}")
        encoded = base64.b64encode(image.read_bytes()).decode("ascii")
        data_url = f"data:image/jpeg;base64,{encoded}"
        try:
            return self._structured_response(
                [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": data_url, "detail": "high"},
                ],
                schema=schema,
                schema_name=schema_name,
                max_output_tokens=max_output_tokens,
            )
        except self._api_error as exc:
            raise RuntimeError(
                "Meta Model API request failed. Automatic retries are disabled to avoid "
                "repeating a potentially billable request; inspect billing before retrying."
            ) from exc

    def _structured_response(
        self,
        content: list[dict[str, Any]],
        *,
        schema: dict[str, Any],
        schema_name: str,
        max_output_tokens: int,
        remote_file_id: str | None = None,
    ) -> dict[str, Any]:
        response = self.client.responses.create(
            model=self.model,
            reasoning={"effort": "minimal"},
            max_output_tokens=max_output_tokens,
            text={"format": {
                "type": "json_schema",
                "name": schema_name,
                "strict": True,
                "schema": schema,
            }},
            input=[{"type": "message", "role": "user", "content": content}],
        )
        if getattr(response, "status", None) not in (None, "completed"):
            raise ValueError(f"Muse Spark response did not complete (status={response.status})")
        if getattr(response, "incomplete_details", None):
            raise ValueError("Muse Spark returned an incomplete response")
        output_text = response.output_text
        if not output_text:
            raise ValueError("Muse Spark returned no structured output")
        try:
            result = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise ValueError("Muse Spark returned invalid JSON") from exc
        if not isinstance(result, dict):
            raise ValueError("Muse Spark output must be a JSON object")
        result["_run"] = {
            "model": self.model,
            "prompt_version": PROMPT_VERSION,
            "remote_file_id": remote_file_id,
            "api_response_id": getattr(response, "id", None),
            "usage": _usage(response),
        }
        return result


def _learning_prompt(duration_seconds: float, narration: str = "") -> str:
    narration_section = (
        f"\n\nExpert narration (use as additional evidence, but distinguish spoken claims from visible facts):\n{narration.strip()}"
        if narration.strip()
        else ""
    )
    return f"""Learn a candidate process from this demonstration video only. Do not assume a task or inject an expected mistake. This single clip is one observed trace, not proof of which steps are necessary. Identify only actions and state facts supported by visible evidence. Keep the representation concise: at most 8 states and 7 transitions. Give each transition a stable unique ID. Every transition needs timestamped evidence within the clip duration ({duration_seconds:.3f} seconds); timestamps may be approximate but must point to visible support. Distinguish visible facts from inference. Record ordering_observations only for pairs whose order is visibly supported, with evidence intervals. These observations mean only “happened before in this clip”; they are not prerequisites and must never be phrased as requirements. Do not infer dependencies, required order, or positional rules from one demonstration. If a potential constraint is useful to preserve, put it in candidate_constraints as an unverified hypothesis, and also disclose the uncertainty. Never describe a candidate constraint as a fact or prerequisite. Do not claim hidden conditions. If the procedure or an object is ambiguous, put that uncertainty in uncertainties. Return the requested JSON schema.{narration_section}"""


def _usage(response: Any) -> dict[str, int]:
    usage = getattr(response, "usage", None)
    return {
        "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
        "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
    }


def _read_repo_key() -> str | None:
    repo_root = Path(__file__).resolve().parents[2]
    env_path = repo_root / ".env"
    if not env_path.is_file():
        return None
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("MODEL_API_KEY="):
            value = line.split("=", 1)[1].strip().strip("'\"")
            return value or None
    return None
