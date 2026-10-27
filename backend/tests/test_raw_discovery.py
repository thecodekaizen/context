"""Source-boundary and citation validation for raw Muse discovery."""

from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest

from thread_engine.raw_discovery import (
    DiscoveryValidationError,
    load_raw_archive,
    validate_discovery,
)

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "datasets/synthetic/creative-evolution.json"


class RawArchiveTests(unittest.TestCase):
    def test_loader_projects_only_project_and_raw_artifacts(self) -> None:
        archive = load_raw_archive(DATASET)
        self.assertEqual(set(archive), {"project", "artifacts"})
        self.assertEqual(len(archive["artifacts"]), 6)
        self.assertEqual(
            set(archive["artifacts"][0]),
            {"id", "date", "modality", "title", "content"},
        )

    def test_loader_rejects_invalid_dates_before_model_call(self) -> None:
        data = json.loads(DATASET.read_text(encoding="utf-8"))
        data["artifacts"][0]["date"] = "2025-02-30"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "invalid.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid date"):
                load_raw_archive(path)


class CitationValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.archive = load_raw_archive(DATASET)

    def candidate(self) -> dict[str, object]:
        return {
            "observations": [
                {"artifact_id": "artifact-001", "date": "2022-03-14", "observation": "Early brief focuses on routes."},
                {"artifact_id": "artifact-005", "date": "2025-02-08", "observation": "Stories lead the later draft."},
            ],
            "candidate_finding": "The project appears to become more story-led while retaining wayfinding.",
            "supporting_artifacts": [
                {"artifact_id": "artifact-001", "date": "2022-03-14", "relevance": "Early navigation goal."},
                {"artifact_id": "artifact-005", "date": "2025-02-08", "relevance": "Later stories lead."},
            ],
            "complicating_artifacts": [
                {"artifact_id": "artifact-006", "date": "2025-11-21", "relevance": "Route index remains."}
            ],
            "limitations": "Synthetic archive with gaps.",
        }

    def test_valid_timeline_citations_are_accepted_and_marked_unconfirmed(self) -> None:
        result = validate_discovery(self.candidate(), self.archive)
        self.assertTrue(result["human_confirmation_required"])

    def test_assertive_candidate_is_withheld(self) -> None:
        value = self.candidate()
        value["candidate_finding"] = "The project focus shifted from navigation to oral history."
        with self.assertRaisesRegex(DiscoveryValidationError, "explicit tentative wording"):
            validate_discovery(value, self.archive)

    def test_fabricated_artifact_is_rejected(self) -> None:
        value = self.candidate()
        value["supporting_artifacts"][1]["artifact_id"] = "artifact-999"  # type: ignore[index]
        with self.assertRaisesRegex(DiscoveryValidationError, "unknown artifact"):
            validate_discovery(value, self.archive)

    def test_mismatched_source_date_is_rejected(self) -> None:
        value = self.candidate()
        value["supporting_artifacts"][0]["date"] = "2020-01-01"  # type: ignore[index]
        with self.assertRaisesRegex(DiscoveryValidationError, "mismatched date"):
            validate_discovery(value, self.archive)

    def test_evolution_needs_multiple_distinct_source_dates(self) -> None:
        value = self.candidate()
        value["supporting_artifacts"] = [value["supporting_artifacts"][0]]  # type: ignore[index]
        with self.assertRaisesRegex(DiscoveryValidationError, "at least two"):
            validate_discovery(value, self.archive)

    def test_empty_candidate_is_valid_when_evidence_is_insufficient(self) -> None:
        value = self.candidate()
        value["candidate_finding"] = ""
        value["supporting_artifacts"] = []
        result = validate_discovery(value, self.archive)
        self.assertEqual(result["candidate_finding"], "")


if __name__ == "__main__":
    unittest.main()
