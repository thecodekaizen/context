"""Conservative, independent audio correspondences using normalized correlation.

These intervals locate matching sound. They never authenticate the video images
or establish that omitted material changes meaning.
"""

import numpy as np

from .media import run

AUDIO_RATE = 2000
WINDOW_SECONDS = 1.0
HOP_SECONDS = 0.5
MIN_CORRELATION = 0.82
MIN_UNIQUENESS_MARGIN = 0.10


def waveform(path):
    raw = run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            str(AUDIO_RATE),
            "-f",
            "f32le",
            "pipe:1",
        ]
    )
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def correlate(source, edited, rate=AUDIO_RATE):
    if rate <= 0 or not (np.isfinite(source).all() and np.isfinite(edited).all()):
        raise ValueError("Audio samples and sample rate must be finite and valid")
    window = round(WINDOW_SECONDS * rate)
    hop = round(HOP_SECONDS * rate)
    if min(len(source), len(edited)) < window:
        return {
            "segments": [],
            "anchors": [],
            "reason": "Audio is shorter than the analysis window",
        }
    size = 1 << (len(source) + window - 2).bit_length()
    spectrum = np.fft.rfft(source, n=size)
    sums = np.r_[0.0, np.cumsum(source)]
    squares = np.r_[0.0, np.cumsum(source * source)]
    sums = sums[window:] - sums[:-window]
    energy = squares[window:] - squares[:-window] - sums * sums / window
    anchors = []
    for start in range(0, len(edited) - window + 1, hop):
        clip = edited[start : start + window]
        centered = clip - clip.mean()
        clip_energy = float(centered @ centered)
        # Silence/noise floor cannot establish a correspondence.
        if clip_energy / window < 1e-7:
            continue
        cross = np.fft.irfft(spectrum * np.conj(np.fft.rfft(centered, n=size)), n=size)
        denominator = np.sqrt(np.maximum(energy, 0) * clip_energy)
        scores = np.divide(
            cross[: len(energy)],
            denominator,
            out=np.zeros_like(energy),
            where=denominator > 1e-9,
        )
        best = int(np.argmax(scores))
        score = float(scores[best])
        if score < MIN_CORRELATION:
            continue
        # A repeated sound at a distant position is ambiguous, even if identical.
        alternatives = scores.copy()
        alternatives[max(0, best - rate) : min(len(scores), best + rate + 1)] = -1
        runner_up = float(alternatives.max())
        if score - runner_up < MIN_UNIQUENESS_MARGIN:
            continue
        # A high-energy suffix can dominate a window that straddles a cut.
        # Require each quarter to corroborate the same offset independently.
        aligned = source[best : best + window]
        consistent = True
        for left in range(0, window, max(1, window // 4)):
            a = clip[left : left + window // 4]
            b = aligned[left : left + window // 4]
            a, b = a - a.mean(), b - b.mean()
            energy_a, energy_b = float(a @ a), float(b @ b)
            if min(energy_a, energy_b) / len(a) < 1e-7:
                consistent = False
                break
            local_score = float(a @ b) / np.sqrt(energy_a * energy_b)
            if local_score < 0.70:
                consistent = False
                break
        if not consistent:
            continue
        anchors.append(
            {
                "edited_start": start / rate,
                "edited_end": (start + window) / rate,
                "source_start": best / rate,
                "source_end": (best + window) / rate,
                "correlation": round(score, 4),
                "uniqueness_margin": round(score - runner_up, 4),
            }
        )
    segments = []
    for anchor in anchors:
        offset = anchor["source_start"] - anchor["edited_start"]
        if segments:
            previous = segments[-1]
            previous_offset = previous["source_start"] - previous["edited_start"]
            if (
                anchor["edited_start"] <= previous["edited_end"]
                and abs(offset - previous_offset) <= 0.04
            ):
                previous["edited_end"] = anchor["edited_end"]
                previous["source_end"] = previous["edited_end"] + previous_offset
                previous["confidence"] = min(
                    previous["confidence"], anchor["correlation"]
                )
                continue
        segments.append(
            {
                "id": f"audio-{len(segments)}",
                "kind": "match",
                "evidence": "audio",
                **{
                    k: anchor[k]
                    for k in (
                        "edited_start",
                        "edited_end",
                        "source_start",
                        "source_end",
                    )
                },
                "confidence": anchor["correlation"],
            }
        )
    return {"segments": segments, "anchors": anchors}


def analyze_audio(source_path, edited_path):
    result = correlate(waveform(source_path), waveform(edited_path))
    return {
        "method": "normalized-waveform-correlation-v1",
        "sample_rate": AUDIO_RATE,
        "window_seconds": WINDOW_SECONDS,
        "hop_seconds": HOP_SECONDS,
        "minimum_correlation": MIN_CORRELATION,
        "minimum_uniqueness_margin": MIN_UNIQUENESS_MARGIN,
        **result,
        "limitations": [
            "Matching sound does not establish matching images or speaker intent.",
            "Silence and repeated sound are rejected; dubbing, music replacement and speed changes may remain unresolved.",
        ],
    }
