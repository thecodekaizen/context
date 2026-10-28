"""Conservative visual sequence alignment with explicit ambiguity rejection."""

import itertools

import numpy as np

from .media import RATE, VideoSamples, sample

THRESHOLD = 0.075


def analyze(original, edited):
    return align_samples(sample(original), sample(edited))


def align_samples(source_samples: VideoSamples, edited_samples: VideoSamples):
    source, published = source_samples.info, edited_samples.info
    st, sf = source_samples.times, source_samples.frames
    et, ef = edited_samples.times, edited_samples.frames
    indices, errors, ambiguous = [], [], []
    for frame in ef:
        distances = np.mean(np.abs(sf - frame), axis=1)
        best = int(np.argmin(distances))
        # Near temporal neighbors are expected to look similar; distant ties are ambiguous.
        alternatives = distances[np.abs(st - st[best]) > 1.0]
        tie = bool(len(alternatives) and alternatives.min() < distances[best] + 0.008)
        indices.append(best if distances[best] <= THRESHOLD and not tie else -1)
        errors.append(float(distances[best]))
        ambiguous.append(tie)
    # Detect sustained non-unit playback before creating 1x player mappings.
    # Overlapping 4-second windows require enough unambiguous correspondences
    # and a tight linear fit, so an isolated cut does not imply a speed change.
    raw_indices = np.asarray(indices)
    rejected = np.zeros(len(indices), dtype=bool)
    for a in range(0, max(1, len(indices) - 7), 8):
        b = min(len(indices), a + 16)
        valid = np.flatnonzero(raw_indices[a:b] >= 0) + a
        if len(valid) < max(8, (b - a) * 0.6):
            continue
        x = et[valid]
        y = st[raw_indices[valid]]
        slope, intercept = np.polyfit(x, y, 1)
        residual = float(np.max(np.abs(y - (slope * x + intercept))))
        if residual <= 0.3 and 0.3 < slope < 3 and abs(slope - 1) > 0.08:
            rejected[a:b] = True
    for i in np.flatnonzero(rejected):
        indices[i] = -1
    segments = []
    start = 0

    def emit(a, b):
        valid = indices[a] >= 0
        if valid and (
            b - a < 2
            or st[indices[b - 1]] - st[indices[a]] + 1 / RATE <= 0.5 * ((b - a) / RATE)
        ):
            valid = False
        segments.append(
            {
                "id": f"s{len(segments)}",
                "kind": "match" if valid else "unmatched",
                "edited_start": float(et[a]),
                "edited_end": min(published["duration"], b / RATE),
                "source_start": float(st[indices[a]]) if valid else None,
                "source_end": min(
                    source["duration"], float(st[indices[b - 1]]) + 1 / RATE
                )
                if valid
                else None,
                "confidence": round(
                    max(0, 1 - float(np.mean(errors[a:b])) / THRESHOLD), 3
                )
                if valid
                else 0,
            }
        )

    for i in range(1, len(indices)):
        prev, curr = indices[i - 1], indices[i]
        continuous = (prev < 0 and curr < 0) or (
            prev >= 0
            and curr >= 0
            and abs((curr - prev) - 1) <= 1
            and abs((curr - indices[start]) - (i - start)) <= 1
        )
        if not continuous:
            emit(start, i)
            start = i
    emit(start, len(indices))
    # Reject sub-second islands: isolated visual coincidences are not source evidence.
    for s in segments:
        if s["kind"] == "match" and s["edited_end"] - s["edited_start"] < 0.5:
            s.update(kind="unmatched", source_start=None, source_end=None, confidence=0)
    matches = [s for s in segments if s["kind"] == "match"]
    coverage = (
        sum(s["edited_end"] - s["edited_start"] for s in matches)
        / published["duration"]
    )
    findings = []

    def finding(kind, a, b, **extra):
        findings.append(
            dict(
                id=f"f{len(findings)}", kind=kind, source_start=a, source_end=b, **extra
            )
        )

    covered = sorted((s["source_start"], s["source_end"]) for s in matches)
    possible_coverage = list(covered)
    unplaced_uncertainty = False
    for segment in segments:
        if segment["kind"] != "unmatched":
            continue
        before = next(
            (
                m
                for m in reversed(matches)
                if m["edited_end"] <= segment["edited_start"]
            ),
            None,
        )
        after = next(
            (m for m in matches if m["edited_start"] >= segment["edited_end"]), None
        )
        offsets = []
        if before:
            offsets.append(before["source_end"] - before["edited_end"])
        if after:
            offsets.append(after["source_start"] - after["edited_start"])
        if offsets and max(offsets) - min(offsets) <= 0.5:
            # This is only possible coverage, used to withhold omission claims.
            # It never creates a match or a synchronized playback interval.
            offset = sum(offsets) / len(offsets)
            possible_coverage.append(
                (
                    max(0, segment["edited_start"] + offset),
                    min(source["duration"], segment["edited_end"] + offset),
                )
            )
        elif segment["edited_end"] - segment["edited_start"] >= 0.5:
            unplaced_uncertainty = True
    possible_coverage.sort()
    if coverage >= 0.5:
        proposed = []
        # An unmatched interval is uncertainty, not evidence of an omission.
        # Only infer missing source ranges across an observed cut or at an
        # aligned edit boundary, and subtract material used elsewhere.
        first, last = matches[0], matches[-1]
        if first["edited_start"] <= 0.25 and first["source_start"] >= 0.5:
            proposed.append((0, first["source_start"]))
        if (
            published["duration"] - last["edited_end"] <= 0.25
            and source["duration"] - last["source_end"] >= 0.5
        ):
            proposed.append((last["source_end"], source["duration"]))
        for previous, current in itertools.pairwise(matches):
            edited_gap = current["edited_start"] - previous["edited_end"]
            source_gap = current["source_start"] - previous["source_end"]
            if edited_gap <= 0.5 and source_gap - edited_gap >= 0.5:
                proposed.append((previous["source_end"], current["source_start"]))
        missing = []
        for left, right in [] if unplaced_uncertainty else proposed:
            cursor = left
            for a, b in possible_coverage:
                if b <= cursor or a >= right:
                    continue
                if a - cursor >= 0.5:
                    missing.append((cursor, min(a, right)))
                cursor = max(cursor, b)
            if right - cursor >= 0.5:
                missing.append((cursor, right))
        for a, b in sorted(set(missing)):
            finding("omission", a, b)
        for prev, curr in itertools.pairwise(matches):
            if curr["source_start"] < prev["source_start"] - 0.25:
                finding(
                    "reordering",
                    curr["source_start"],
                    curr["source_end"],
                    edited_start=curr["edited_start"],
                )
        for i, s in enumerate(matches):
            if any(
                min(s["source_end"], p["source_end"])
                - max(s["source_start"], p["source_start"])
                >= 0.5
                for p in matches[:i]
            ):
                finding(
                    "repetition",
                    s["source_start"],
                    s["source_end"],
                    edited_start=s["edited_start"],
                )
    return {
        "schema_version": "1.0",
        "method": {
            "name": "spatial-color-sequence-v2",
            "sample_rate": RATE,
            "threshold": THRESHOLD,
            "timestamp_tolerance_seconds": 0.5,
        },
        "source": {**source, "sha256": source_samples.sha256},
        "edited": {**published, "sha256": edited_samples.sha256},
        "diagnostics": {
            "timing_rejected_fraction": round(float(np.mean(rejected)), 3),
            "ambiguous_frame_fraction": round(float(np.mean(ambiguous)), 3),
        },
        "status": "matched" if coverage >= 0.5 else "insufficient_evidence",
        "coverage": round(coverage, 3),
        "segments": segments,
        "findings": findings,
        "limitations": [
            "Visual matching only; audio and speaker intent are not analyzed.",
            "Repeated/static scenes may be rejected as ambiguous.",
            "Cropping, overlays, speed changes and large color changes are not reliably supported.",
            "Omissions require a supported cut or aligned boundary; unresolved source ranges are not labeled omitted. An edit alone does not establish misleading intent.",
        ],
    }
