"""Tests for creator challenge, confirmation, and artifact gating."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from thread_engine.review import review_finding


FINDING = {
    "id": "candidate-1",
    "project_title": "Tiny Type Lab",
    "hypothesis": "The project appears to broaden from code tools toward readable text while retaining coding.",
    "supporting_evidence": [
        {"source_id": "type-001", "date": "2023-02-10", "summary": "The initial font targets code editors.", "theme": "developer tools"},
        {"source_id": "type-005", "date": "2025-01-09", "summary": "The text cut supports handouts and labels.", "theme": "text readability"},
    ],
    "counter_evidence": [],
    "continuity_evidence": [
        {"source_id": "type-006", "date": "2025-08-18", "summary": "Code remains the showcase use case.", "theme": "code readability"}
    ],
    "uncertainty": ["The archive contains only a few dated summaries."],
}


class ReviewFlowTests(unittest.TestCase):
    def run_flow(self, answers: list[str], output_dir: Path):
        questions: list[str] = []

        def ask(question: str) -> str:
            questions.append(question)
            return answers.pop(0)

        emitted: list[str] = []
        state = review_finding(FINDING, ask=ask, emit=emitted.append, output_dir=output_dir)
        return state, questions, emitted

    def test_artifact_requires_creator_answers_and_exact_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            state, questions, emitted = self.run_flow(
                [
                    "The print workshop changed what we thought the typeface could support.",
                    "Coding remains the main use, while text makes the family more useful.",
                    "keep",
                    "CONFIRM",
                ],
                Path(folder),
            )
            self.assertEqual(state["stage"], "artifact-created")
            self.assertEqual(len(questions), 4)
            artifact = Path(state["artifact_path"])
            self.assertTrue(artifact.exists())
            body = artifact.read_text(encoding="utf-8")
            self.assertIn(state["insight_id"], body)
            self.assertIn("type-006", body)
            session = json.loads((Path(folder) / "sessions" / f"{state['session_id']}.json").read_text())
            self.assertEqual(session["stage"], "artifact-created")
            self.assertTrue(any("Confirm" in line for line in emitted))

    def test_rejected_candidate_never_creates_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            state, _, _ = self.run_flow(
                [
                    "The print workshop changed what we thought the typeface could support.",
                    "Coding remains the main use, while text makes the family more useful.",
                    "reject",
                ],
                Path(folder),
            )
            self.assertEqual(state["stage"], "rejected")
            self.assertEqual(list(Path(folder).glob("direction-note-*.md")), [])

    def test_revised_interpretation_still_requires_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            state, _, _ = self.run_flow(
                [
                    "This is too strong; print tests were one exploratory use case.",
                    "Coding remains the core project and the text cut is an extension.",
                    "revise",
                    "The project appears to extend a coding typeface for readable text as well.",
                    "yes",
                ],
                Path(folder),
            )
            self.assertEqual(state["stage"], "unconfirmed")
            self.assertEqual(list(Path(folder).glob("direction-note-*.md")), [])


if __name__ == "__main__":
    unittest.main()
