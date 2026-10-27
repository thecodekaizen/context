"""Tests for evidence and state checks on learner observations."""

import copy
import unittest

from showme.observe import observation_prompt, observation_schema, validate_observation
from test_showme_process import VALID_PROCESS


class ObservationValidationTests(unittest.TestCase):
    def setUp(self):
        self.process = copy.deepcopy(VALID_PROCESS)
        self.valid = {
            "events": [
                {"time_seconds": 1.0, "action": "start", "state_id": "separate", "assessment": "consistent", "object_ids": ["red", "blue"], "evidence": "The blocks are apart."},
                {"time_seconds": 4.0, "action": "stack", "state_id": "stacked", "assessment": "consistent", "object_ids": ["red", "blue"], "evidence": "Red rests on blue."},
            ],
            "divergences": [],
            "recovery_status": "no_divergence_observed",
            "uncertainties": [],
        }

    def test_accepts_grounded_valid_timeline(self):
        validate_observation(self.valid, self.process, 5.0)

    def test_rejects_unknown_state(self):
        output = copy.deepcopy(self.valid)
        output["events"][0]["state_id"] = "invented"
        with self.assertRaisesRegex(ValueError, "unknown state_id"):
            validate_observation(output, self.process, 5.0)

    def test_rejects_timestamp_outside_clip(self):
        output = copy.deepcopy(self.valid)
        output["events"][1]["time_seconds"] = 5.0
        with self.assertRaisesRegex(ValueError, "within the clip"):
            validate_observation(output, self.process, 5.0)

    def test_rejects_out_of_order_events(self):
        output = copy.deepcopy(self.valid)
        output["events"].reverse()
        with self.assertRaisesRegex(ValueError, "chronological"):
            validate_observation(output, self.process, 5.0)

    def test_recovered_requires_divergence_and_later_consistent_state(self):
        output = copy.deepcopy(self.valid)
        output["recovery_status"] = "recovered"
        with self.assertRaisesRegex(ValueError, "without a visible divergence"):
            validate_observation(output, self.process, 5.0)

    def test_accepts_recovery_only_after_later_consistent_state(self):
        output = copy.deepcopy(self.valid)
        output["events"][0]["assessment"] = "divergent"
        output["divergences"] = [{
            "time_seconds": 1.5,
            "process_difference": "red block is beside rather than above blue",
            "object_ids": ["red", "blue"],
            "evidence": "At 1.5s the blocks are side by side.",
        }]
        output["recovery_status"] = "recovered"
        validate_observation(output, self.process, 5.0)

    def test_rejects_recovery_without_later_consistent_event(self):
        output = copy.deepcopy(self.valid)
        output["events"][0]["assessment"] = "divergent"
        output["events"][1]["assessment"] = "divergent"
        output["divergences"] = [{
            "time_seconds": 1.5,
            "process_difference": "unexpected arrangement",
            "object_ids": ["red"],
            "evidence": "Visible at 1.5s.",
        }]
        output["recovery_status"] = "recovered"
        with self.assertRaisesRegex(ValueError, "later process-consistent"):
            validate_observation(output, self.process, 5.0)

    def test_observation_schema_limits_model_to_declared_ids(self):
        schema = observation_schema(self.process)
        state_enum = schema["properties"]["events"]["items"]["properties"]["state_id"]["enum"]
        self.assertEqual(state_enum, ["separate", "stacked", "unknown"])

    def test_prompt_does_not_include_run_metadata(self):
        self.process["_run"] = {"remote_file_id": "secret-file-id", "model": "muse-spark-1.3"}
        prompt = observation_prompt(self.process, 12.0)
        self.assertNotIn("secret-file-id", prompt)
        self.assertIn("may be correct, divergent", prompt)

    def test_prompt_does_not_treat_demo_order_as_a_requirement(self):
        prompt = observation_prompt(self.process, 12.0)
        self.assertIn("not required prerequisites", prompt)
        self.assertIn("not call a learner divergent only because", prompt)


if __name__ == "__main__":
    unittest.main()
