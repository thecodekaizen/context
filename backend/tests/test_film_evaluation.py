"""Optional regression against locally downloaded, licensed production footage."""

from pathlib import Path

import pytest
from context_core.alignment import analyze

DATA = Path(__file__).resolve().parents[2] / "data/evaluation"
pytestmark = pytest.mark.skipif(
    not (DATA / "source.mp4").exists(),
    reason="Optional Blender evaluation: run scripts/evaluate.py --download first",
)


@pytest.mark.parametrize(
    "name,kinds",
    [
        ("copy", set()),
        ("omission", {"omission"}),
        ("reordered", {"reordering"}),
        ("repeated", {"omission", "repetition"}),
        ("fractional_trim", {"omission"}),
        ("heavy_compression", set()),
        ("overlay", set()),
    ],
)
def test_production_footage_findings(name, kinds):
    result = analyze(DATA / "source.mp4", DATA / f"{name}.mp4")
    assert result["status"] == "matched"
    assert {f["kind"] for f in result["findings"]} == kinds
    omissions = [f for f in result["findings"] if f["kind"] == "omission"]
    assert len(omissions) == (
        2 if name == "fractional_trim" else 1 if name in {"omission", "repeated"} else 0
    )
    if name == "omission":
        assert abs(omissions[0]["source_start"] - 8) <= 0.5
        assert abs(omissions[0]["source_end"] - 14) <= 0.5


@pytest.mark.parametrize(
    "name", ["brightness", "small_crop", "speed_change", "unrelated"]
)
def test_unsupported_or_unrelated_is_unresolved(name):
    result = analyze(DATA / "source.mp4", DATA / f"{name}.mp4")
    assert result["status"] == "insufficient_evidence"
    assert not result["findings"]
