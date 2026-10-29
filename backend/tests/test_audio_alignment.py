import numpy as np
import pytest
from context_core.audio_alignment import correlate


def signal():
    return np.random.default_rng(4831).normal(0, 0.1, 24000)


def test_audio_trim_reorder_and_gain():
    source = signal()
    edited = np.r_[source[14000:20000], source[2000:8000]] * 0.4
    result = correlate(source, edited)
    segments = result["segments"]
    assert len(segments) == 2
    for segment, expected in zip(segments, [(0, 3, 7, 10), (3, 6, 1, 4)], strict=True):
        actual = tuple(
            segment[k]
            for k in ("edited_start", "edited_end", "source_start", "source_end")
        )
        assert np.allclose(actual, expected, atol=0.01)


def test_silence_unrelated_and_repeated_audio_are_not_evidence():
    source = signal()
    assert not correlate(source, np.zeros(5000))["segments"]
    unrelated = np.random.default_rng(234).normal(0, 0.1, 5000)
    assert not correlate(source, unrelated)["segments"]
    assert not correlate(np.tile(source[:4000], 4), source[:4000])["segments"]


def test_speed_change_does_not_create_unit_speed_mapping():
    source = signal()
    changed = np.interp(np.arange(0, len(source), 1.25), np.arange(len(source)), source)
    assert not correlate(source, changed)["segments"]


def test_compressed_audio_remains_separate_from_ambiguous_images(tmp_path):
    import wave

    from context_core.alignment import analyze
    from context_core.media import run

    rate = 8000
    t = np.arange(rate * 8) / rate
    sound = 0.25 * np.sin(2 * np.pi * (140 * t + 9 * t * t + 0.3 * t**3))
    wav = tmp_path / "sound.wav"
    with wave.open(str(wav), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes((sound * 32767).astype("<i2").tobytes())
    original, edit = tmp_path / "source.mp4", tmp_path / "edit.mp4"
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=blue:s=320x180:r=24:d=8",
            "-i",
            str(wav),
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-shortest",
            str(original),
        ]
    )
    graph = "[0:v]trim=4:7,setpts=PTS-STARTPTS[v0];[0:a]atrim=4:7,asetpts=PTS-STARTPTS[a0];[0:v]trim=0:3,setpts=PTS-STARTPTS[v1];[0:a]atrim=0:3,asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]"
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(original),
            "-filter_complex",
            graph,
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            str(edit),
        ]
    )
    result = analyze(original, edit)
    assert result["coverage"] == 0
    assert result["findings"] == []
    audio = result["audio_alignment"]["segments"]
    assert len(audio) == 2
    assert abs(audio[0]["source_start"] - 4) < 0.05
    assert abs(audio[1]["source_start"]) < 0.05


def test_invalid_audio_is_not_matching_evidence():
    source = signal()
    source[100] = np.nan
    with pytest.raises(ValueError, match="finite"):
        correlate(source, np.ones(5000))


def test_loud_matching_suffix_cannot_validate_unrelated_prefix():
    source = signal()
    # Most energy matches at source 6s, but the first quarter is unrelated.
    source[12000:12500] *= 0.01
    edit = source[12000:14000].copy()
    edit[:500] = np.random.default_rng(92).normal(0, 0.001, 500)
    result = correlate(source, edit)
    assert result["segments"] == []
