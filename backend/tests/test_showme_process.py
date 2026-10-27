"""Tests for SHOWME's process graph boundary."""

import copy
import unittest

from showme.process import validate_references


VALID_PROCESS = {
    "task_summary": "Move the red block onto the blue block.",
    "objects": [
        {"id": "red", "label": "red block", "visual_description": "small red cube"},
        {"id": "blue", "label": "blue block", "visual_description": "large blue cube"},
    ],
    "states": [
        {"id": "separate", "description": "Blocks are separate", "observable_facts": ["gap between blocks"]},
        {"id": "stacked", "description": "Red block rests on blue", "observable_facts": ["red above blue"]},
    ],
    "transitions": [{
        "id": "stack_blocks",
        "from_state": "separate",
        "action": "place red on blue",
        "object_ids": ["red", "blue"],
        "to_state": "stacked",
        "preconditions": [],
        "postconditions": ["red above blue"],
        "evidence": [{"start_seconds": 0.5, "end_seconds": 1.0, "observation": "Red block visibly moves above blue."}],
    }],
    "ordering_observations": [],
    "uncertainties": [],
}


class ProcessValidationTests(unittest.TestCase):
    def test_accepts_well_formed_references(self):
        validate_references(copy.deepcopy(VALID_PROCESS))

    def test_rejects_unknown_from_state(self):
        process = copy.deepcopy(VALID_PROCESS)
        process["transitions"][0]["from_state"] = "missing"
        with self.assertRaisesRegex(ValueError, "unknown from_state"):
            validate_references(process)

    def test_rejects_unknown_to_state(self):
        process = copy.deepcopy(VALID_PROCESS)
        process["transitions"][0]["to_state"] = "missing"
        with self.assertRaisesRegex(ValueError, "unknown to_state"):
            validate_references(process)

    def test_rejects_unknown_object(self):
        process = copy.deepcopy(VALID_PROCESS)
        process["transitions"][0]["object_ids"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "unknown object_id"):
            validate_references(process)

    def test_rejects_duplicate_state_ids(self):
        process = copy.deepcopy(VALID_PROCESS)
        process["states"].append(copy.deepcopy(process["states"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate state id"):
            validate_references(process)

    def test_rejects_duplicate_transition_ids(self):
        process = copy.deepcopy(VALID_PROCESS)
        process["transitions"].append(copy.deepcopy(process["transitions"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate transition id"):
            validate_references(process)

    def test_rejects_ordering_observation_with_unknown_transition(self):
        process = copy.deepcopy(VALID_PROCESS)
        process["ordering_observations"] = [{
            "before_transition_id": "missing",
            "after_transition_id": "stack_blocks",
            "evidence": [{"start_seconds": 0, "end_seconds": 1, "observation": "Visible order."}],
        }]
        with self.assertRaisesRegex(ValueError, "unknown before_transition_id"):
            validate_references(process)

    def test_accepts_evidence_backed_observed_order(self):
        process = copy.deepcopy(VALID_PROCESS)
        process["transitions"].append({
            "id": "separate_blocks",
            "from_state": "separate",
            "action": "move red beside blue",
            "object_ids": ["red", "blue"],
            "to_state": "separate",
            "preconditions": [],
            "postconditions": [],
            "evidence": [{"start_seconds": 0.1, "end_seconds": 0.3, "observation": "Red is placed beside blue."}],
        })
        process["ordering_observations"] = [{
            "before_transition_id": "separate_blocks",
            "after_transition_id": "stack_blocks",
            "evidence": [{"start_seconds": 0.1, "end_seconds": 1.0, "observation": "The side-by-side arrangement occurs before stacking."}],
        }]
        validate_references(process)

    def test_rejects_evidence_interval_beyond_expert_clip(self):
        process = copy.deepcopy(VALID_PROCESS)
        with self.assertRaisesRegex(ValueError, "outside the expert clip"):
            validate_references(process, duration_seconds=0.75)

    def test_rejects_transitions_without_visual_evidence(self):
        process = copy.deepcopy(VALID_PROCESS)
        process["transitions"][0]["evidence"] = []
        with self.assertRaisesRegex(ValueError, "needs at least one evidence interval"):
            validate_references(process)


if __name__ == "__main__":
    unittest.main()
