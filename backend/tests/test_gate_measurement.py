"""The scorer must choose support from within the edited piece, not a
quantized tail of the preceding/following match across its cut boundary.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from run_smoke_test_classification import measure_boundaries


def segment(a, b, source):
    return {"kind": "match", "edited_start": a, "edited_end": b, "source_start": source}


def test_quantized_boundary_does_not_choose_the_other_side_of_cut():
    alignment = {"segments": [segment(0, 4.1, 20), segment(4.1, 8, 0.1)]}
    assert measure_boundaries(alignment, [(20, 24), (0, 4)])["passed"]


def test_wrong_offset_and_large_unsupported_gap_still_fail():
    assert not measure_boundaries({"segments": [segment(0, 4, 50)]}, [(20, 24)])[
        "passed"
    ]
    assert not measure_boundaries({"segments": [segment(3, 4, 23)]}, [(20, 24)])[
        "passed"
    ]


def test_continuous_segment_can_cover_multiple_recipe_pieces():
    result = measure_boundaries({"segments": [segment(0, 8, 20)]}, [(20, 24), (24, 28)])
    assert result["passed"]
