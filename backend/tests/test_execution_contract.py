import importlib.util
import json
from pathlib import Path

import pytest
from context_core.grounded_omissions import grounded_omissions, validate_explanation

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "execution_eval", ROOT / "scripts/execution_eval.py"
)
scorer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scorer)
CONTRACT = json.loads((ROOT / "eval/execution-v1/contract.json").read_text())


def match(start, end, source_start):
    return {
        "kind": "match",
        "edited_start": start,
        "edited_end": end,
        "source_start": source_start,
        "source_end": source_start + end - start,
        "confidence": 0.9,
    }


def test_unmatched_and_boundary_trim_never_create_material_omission():
    assert grounded_omissions({})["status"] == "no material omission"
    assert not grounded_omissions({"segments": [match(0, 8, 2)]})["omissions"]


def test_audio_gap_is_grounded_and_reorder_is_not_missing_material():
    segments = [match(0, 5, 0), match(5, 13, 10)]
    result = grounded_omissions({"audio_alignment": {"segments": segments}})
    omission = result["omissions"][0]
    assert (
        omission["source_start"],
        omission["source_end"],
        omission["edit_position"],
    ) == (5, 10, 5)
    assert omission["matched_evidence"]["modality"] == "audio"
    assert omission["explanation"] is None
    reordered = [match(0, 8, 10), match(8, 13, 0), match(13, 18, 5)]
    assert not grounded_omissions({"segments": reordered})["omissions"]


def test_material_used_elsewhere_is_subtracted_from_apparent_gap():
    result = grounded_omissions(
        {"segments": [match(0, 2, 6), match(2, 7, 0), match(7, 15, 10)]}
    )
    assert [
        (item["source_start"], item["source_end"]) for item in result["omissions"]
    ] == [(5, 6), (8, 10)]


def test_recipe_labels_ignore_reorders_and_intro_trims():
    assert (
        scorer.expected_omissions(
            {"transform": "none", "intervals": [[10, 18], [0, 5], [5, 10]]}
        )
        == []
    )
    assert (
        scorer.expected_omissions({"transform": "none", "intervals": [[2, 18]]}) == []
    )
    assert (
        len(
            scorer.expected_omissions(
                {"transform": "none", "intervals": [[0, 4], [7, 11], [14, 18]]}
            )
        )
        == 2
    )


def test_duplicate_predictions_cannot_inflate_recall():
    expected = [
        {"source_start": 5, "source_end": 10, "edit_position": 5, "modality": "visual"}
    ]
    prediction = {**expected[0], "matched_evidence": {"modality": "audio"}}
    result = scorer.score(expected, [prediction, prediction], CONTRACT)
    assert result["recovered"] == 1
    assert result["predicted"] == 2
    assert result["boundary_errors_seconds"] == [0, 0]


def test_wrong_time_or_modality_and_misses_are_not_recovered():
    label = {
        "source_start": 5,
        "source_end": 10,
        "edit_position": 5,
        "modality": "audio",
    }
    visual = {**label, "matched_evidence": {"modality": "visual"}}
    shifted = {**label, "edit_position": 12, "matched_evidence": {"modality": "audio"}}
    result = scorer.score([label], [visual, shifted], CONTRACT)
    assert result["recovered"] == 0
    assert result["expected"] == 1
    assert result["boundary_errors_seconds"] == []


def test_explanation_requires_finite_timestamps_within_omission():
    omission = grounded_omissions({"segments": [match(0, 5, 0), match(5, 13, 10)]})[
        "omissions"
    ][0]
    explanation = {
        "text": "An interval was removed.",
        "citations": [{"source_start": 5, "source_end": 10}],
    }
    assert validate_explanation(omission, explanation)["explanation"] == explanation
    for start, end in [
        (4, 10),
        (5, 11),
        (float("nan"), 10),
        (5, float("inf")),
        (True, 10),
    ]:
        with pytest.raises(ValueError):
            validate_explanation(
                omission,
                {
                    **explanation,
                    "citations": [{"source_start": start, "source_end": end}],
                },
            )
