"""Application service shared by the CLI and the HTTP API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from .cli import load_dataset
from .contracts import to_dict
from .discovery import discover_evolution

ProviderName = Literal["fixture", "meta"]
DEFAULT_DATASET = Path(__file__).resolve().parents[2] / "datasets" / "synthetic" / "creative-evolution.json"


def discover_dataset(
    *, dataset_path: Path = DEFAULT_DATASET, provider_name: ProviderName = "fixture"
) -> dict[str, Any]:
    """Run extraction and temporal analysis, returning one JSON-ready finding."""
    project_id, project_title, memories = load_dataset(dataset_path)
    model = None
    usage = None
    if provider_name == "meta":
        try:
            data = json.loads(dataset_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"cannot read source artifacts: {exc}") from exc
        artifacts = data.get("artifacts")
        if not isinstance(artifacts, list):
            raise ValueError("Meta mode requires an 'artifacts' list containing source text")
        from .meta_provider import MetaModelProvider

        provider = MetaModelProvider.from_env()
        memories = [provider.extract(item) for item in artifacts]
        model = provider.model
        usage = provider.usage_summary()

    finding = discover_evolution(
        project_id=project_id,
        project_title=project_title,
        memories=memories,
        extraction_provider=provider_name,
        extraction_model=model,
    )
    if finding is None:
        raise ValueError("No sufficiently supported evolution finding in this dataset.")
    result = to_dict(finding)
    if usage is not None:
        result["api_usage"] = usage
    return result
