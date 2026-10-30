"""Internal omissions supported by independent matched intervals on both sides."""

import itertools
import math


def grounded_omissions(evidence):
    omissions = []
    lanes = {
        "visual": evidence.get("segments", []),
        "audio": evidence.get("audio_alignment", {}).get("segments", []),
    }
    for modality, segments in lanes.items():
        matches = sorted(
            (segment for segment in segments if segment["kind"] == "match"),
            key=lambda segment: segment["edited_start"],
        )
        for previous, current in itertools.pairwise(matches):
            edit_gap = current["edited_start"] - previous["edited_end"]
            start, end = previous["source_end"], current["source_start"]
            if not -0.05 <= edit_gap <= 1 or end - start - edit_gap < 0.5:
                continue
            covered = sorted(
                (match["source_start"], match["source_end"])
                for match in matches
                if match["source_end"] > start and match["source_start"] < end
            )
            missing = []
            cursor = start
            for left, right in covered:
                if left - cursor >= 0.5:
                    missing.append((cursor, min(left, end)))
                cursor = max(cursor, right)
            if end - cursor >= 0.5:
                missing.append((cursor, end))
            for left, right in missing:
                record = {
                    "source_start": left,
                    "source_end": right,
                    "edit_position": current["edited_start"],
                    "confidence": min(
                        previous.get("confidence", 0), current.get("confidence", 0)
                    ),
                    "matched_evidence": {
                        "modality": modality,
                        "before": previous,
                        "after": current,
                        "source_sha256": evidence.get("source", {}).get("sha256"),
                        "edited_sha256": evidence.get("edited", {}).get("sha256"),
                    },
                    "explanation": None,
                }
                if not any(
                    old["matched_evidence"]["modality"] != modality
                    and abs(old["source_start"] - left) <= 0.5
                    and abs(old["source_end"] - right) <= 0.5
                    and abs(old["edit_position"] - current["edited_start"]) <= 0.5
                    for old in omissions
                ):
                    omissions.append(record)
    return {
        "status": "matched omissions" if omissions else "no material omission",
        "limitations": "Matched media deletion only; material effect on meaning remains unassessed. Boundary trims are not internal omissions. No match is an abstention, not proof of a faithful edit.",
        "omissions": omissions,
    }


def validate_explanation(omission, explanation):
    if not omission.get("matched_evidence"):
        raise ValueError("Explanation requires deterministic matched evidence")
    if set(explanation) != {"text", "citations"} or not explanation["text"]:
        raise ValueError("Explanation requires text and explicit citations")
    if not explanation["citations"]:
        raise ValueError("Explanation requires an omission citation")
    for citation in explanation["citations"]:
        start, end = citation["source_start"], citation["source_end"]
        if (
            not all(
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(value)
                for value in (start, end)
            )
            or not omission["source_start"] <= start < end <= omission["source_end"]
        ):
            raise ValueError(
                "Explanation cites a time outside matched omission evidence"
            )
    return {**omission, "explanation": explanation}
