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
        "from_state": "separate",
        "action": "place red on blue",
        "object_ids": ["red", "blue"],
        "to_state": "stacked",
        "preconditions": [],
        "postconditions": ["red above blue"],
        "evidence": [],
    }],
    "constraints": [],
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


if __name__ == "__main__":
    unittest.main()
