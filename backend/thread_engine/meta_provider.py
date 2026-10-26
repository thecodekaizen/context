"""Muse Spark adapter for converting source artifacts into typed memories."""

from __future__ import annotations

import json
import os
from hashlib import sha256
from pathlib import Path
from typing import Any

from .contracts import Memory

MODEL = "muse-spark-1.3"
PROMPT_VERSION = "memory-extraction-v1"
THEMES = (
    "wayfinding", "accessibility", "navigation", "oral-history", "community",
    "visual-language", "materials", "interaction", "purpose",
)

MEMORY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "summary": {"type": "string", "description": "One concise, source-grounded sentence."},
        "themes": {"type": "array", "items": {"type": "string", "enum": list(THEMES)}, "maxItems": 3},
    },
    "required": ["summary", "themes"],
    "additionalProperties": False,
}


class MetaModelProvider:
    """Extract a small, auditable memory from each text artifact using Muse Spark."""

    def __init__(self, *, api_key: str, model: str = MODEL, cache_dir: Path | None = None) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ValueError("Meta mode needs the optional dependency: pip install -e '.[meta]'") from exc
        self.client = OpenAI(api_key=api_key, base_url="https://api.meta.ai/v1")
        self.model = model
        self.cache_dir = cache_dir or Path(os.environ.get("THREAD_CACHE_DIR", ".thread-cache"))
        self.cache_file = self.cache_dir / "memories.json"
        self.usage_file = self.cache_dir / "usage.jsonl"
        self.budget_usd = float(os.environ.get("THREAD_BUDGET_USD", "150"))
        self.cache: dict[str, dict[str, Any]] = {}
        if self.cache_file.exists():
            try:
                self.cache = json.loads(self.cache_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                self.cache = {}
        self.run_usage: dict[str, int | float] = {
            "requests": 0, "cache_hits": 0, "input_tokens": 0,
            "cached_input_tokens": 0, "output_tokens": 0, "estimated_usd": 0.0,
        }

    @classmethod
    def from_env(cls) -> "MetaModelProvider":
        api_key = os.environ.get("MODEL_API_KEY")
        if not api_key:
            raise ValueError("set MODEL_API_KEY after claiming your Meta Model API credits")
        return cls(api_key=api_key, model=os.environ.get("THREAD_META_MODEL", MODEL))

    def extract(self, artifact: dict[str, Any]) -> Memory:
        required = ("id", "date", "modality", "title", "content")
        missing = [field for field in required if not artifact.get(field)]
        if missing:
            raise ValueError(f"source artifact is missing: {', '.join(missing)}")

        encoded_artifact = json.dumps(artifact, ensure_ascii=False, sort_keys=True)
        cache_key = sha256(f"{self.model}:{PROMPT_VERSION}:{encoded_artifact}".encode()).hexdigest()
        if cache_key in self.cache:
            self.run_usage["cache_hits"] += 1
            return Memory.from_dict(self.cache[cache_key])

        # Local circuit breaker, not a billing guarantee: conservatively estimate
        # prompt tokens and reserve the full bounded completion before each call.
        input_chars = len(encoded_artifact) + len(json.dumps(MEMORY_SCHEMA)) + 300
        projected_input_tokens = input_chars / 2.5
        contributor = self.model.endswith("-contributor")
        input_rate, output_rate = ((0.10, 0.20) if contributor else (1.25, 4.25))
        projected_cost = (projected_input_tokens * input_rate + 256 * output_rate) / 1_000_000
        if self.cumulative_estimated_usd() + projected_cost > self.budget_usd:
            raise ValueError(
                f"local cost estimate would exceed THREAD_BUDGET_USD=${self.budget_usd:.2f}; "
                "review billing and usage before continuing"
            )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract one concise, neutral memory from the supplied creative-project artifact. "
                        "Use only explicit evidence. Select up to three themes from the allowed taxonomy; "
                        "do not infer personal traits about the creator. Preserve uncertainty in the summary."
                    ),
                },
                {"role": "user", "content": json.dumps(artifact, ensure_ascii=False)},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "creative_memory", "strict": True, "schema": MEMORY_SCHEMA},
            },
            max_completion_tokens=256,
            reasoning_effort="minimal",
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError(f"Meta model returned no memory for {artifact['id']}")
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Meta model returned invalid structured output for {artifact['id']}") from exc
        memory = Memory.from_dict({
            "id": f"memory-{artifact['id']}",
            "source_id": str(artifact["id"]),
            "date": str(artifact["date"]),
            "modality": str(artifact["modality"]),
            "title": str(artifact["title"]),
            "summary": parsed.get("summary"),
            "themes": parsed.get("themes"),
        })
        usage = response.usage
        input_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
        output_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
        details = getattr(usage, "prompt_tokens_details", None)
        cached_tokens = int(getattr(details, "cached_tokens", 0) or 0)
        cached_rate = 0.002 if contributor else 0.15
        estimated_usd = (
            max(input_tokens - cached_tokens, 0) * input_rate
            + cached_tokens * cached_rate
            + output_tokens * output_rate
        ) / 1_000_000
        self.run_usage["requests"] += 1
        self.run_usage["input_tokens"] += input_tokens
        self.run_usage["cached_input_tokens"] += cached_tokens
        self.run_usage["output_tokens"] += output_tokens
        self.run_usage["estimated_usd"] += estimated_usd

        self.cache[cache_key] = {
            "id": memory.id, "source_id": memory.source_id, "date": memory.date,
            "modality": memory.modality, "title": memory.title,
            "summary": memory.summary, "themes": list(memory.themes),
        }
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file.write_text(json.dumps(self.cache, ensure_ascii=False, indent=2), encoding="utf-8")
        with self.usage_file.open("a", encoding="utf-8") as ledger:
            ledger.write(json.dumps({
                "model": self.model, "input_tokens": input_tokens,
                "cached_input_tokens": cached_tokens, "output_tokens": output_tokens,
                "estimated_usd": estimated_usd,
            }) + "\n")
        return memory

    def usage_summary(self) -> dict[str, int | float]:
        """Return this run's token accounting and the local cumulative estimate."""
        cumulative = self.cumulative_estimated_usd()
        return {
            **self.run_usage,
            "cumulative_estimated_usd": round(cumulative, 6),
            "budget_usd": self.budget_usd,
            "remaining_estimated_usd": round(max(self.budget_usd - cumulative, 0.0), 6),
        }

    def cumulative_estimated_usd(self) -> float:
        cumulative = 0.0
        try:
            for line in self.usage_file.read_text(encoding="utf-8").splitlines():
                cumulative += float(json.loads(line).get("estimated_usd", 0))
        except (OSError, json.JSONDecodeError, ValueError):
            pass
        return cumulative
