import pytest
from context_core.alignment import analyze
from context_core.media import probe


@pytest.mark.parametrize(
    "name,kinds",
    [
        ("copy", set()),
        ("trim", {"omission"}),
        ("omission", {"omission"}),
        ("reorder", {"reordering"}),
        ("repeat", {"omission", "repetition"}),
        ("recompressed", set()),
    ],
)
def test_edits(clips, name, kinds):
    result = analyze(clips / "original.mp4", clips / f"{name}.mp4")
    assert result["status"] == "matched"
    assert result["coverage"] > 0.9
    assert {f["kind"] for f in result["findings"]} == kinds
    for s in result["segments"]:
        assert 0 <= s["edited_start"] < s["edited_end"] <= result["edited"]["duration"]
    if name == "omission":
        gap = result["findings"][0]
        assert abs(gap["source_start"] - 4) <= 0.5
        assert abs(gap["source_end"] - 8) <= 0.5
    if name in {"copy", "recompressed"}:
        for s in result["segments"]:
            assert abs(s["edited_start"] - s["source_start"]) <= 0.5


def test_unknown(clips):
    result = analyze(clips / "original.mp4", clips / "unknown.mp4")
    assert result["status"] == "insufficient_evidence"
    assert not result["findings"]


def test_invalid(tmp_path):
    p = tmp_path / "bad.mp4"
    p.write_text("not video")
    with pytest.raises(ValueError):
        probe(p)


def test_ambiguous_static_scene(clips):
    result = analyze(clips / "unknown.mp4", clips / "unknown.mp4")
    assert result["status"] == "insufficient_evidence"
    assert result["coverage"] == 0


def test_unresolved_interior_is_not_an_omission(clips, tmp_path):
    from context_core.media import run

    transformed = tmp_path / "occluded.mp4"
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(clips / "original.mp4"),
            "-vf",
            "drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='between(t,4,6)'",
            "-c:v",
            "libx264",
            str(transformed),
        ]
    )
    result = analyze(clips / "original.mp4", transformed)
    assert result["status"] == "matched"
    assert any(s["kind"] == "unmatched" for s in result["segments"])
    assert not any(f["kind"] == "omission" for f in result["findings"])


@pytest.mark.parametrize("factor", [0.8, 1.25])
def test_speed_changes_do_not_claim_unit_rate_alignment(clips, tmp_path, factor):
    from context_core.media import run

    transformed = tmp_path / "speed.mp4"
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(clips / "original.mp4"),
            "-vf",
            f"setpts={factor}*PTS",
            "-c:v",
            "libx264",
            str(transformed),
        ]
    )
    result = analyze(clips / "original.mp4", transformed)
    assert result["status"] == "insufficient_evidence"
    assert result["diagnostics"]["timing_rejected_fraction"] > 0.5
    assert not result["findings"]


def test_reordering_with_ambiguous_frames_does_not_invent_omissions(clips, tmp_path):
    from context_core.media import run

    original = tmp_path / "original.mp4"
    edited = tmp_path / "edited.mp4"
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(clips / "original.mp4"),
            "-vf",
            "drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='between(t,2,3)'",
            "-c:v",
            "libx264",
            str(original),
        ]
    )
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(original),
            "-filter_complex",
            "[0:v]trim=start=8:end=12,setpts=PTS-STARTPTS[a];[0:v]trim=start=0:end=8,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0[out]",
            "-map",
            "[out]",
            "-c:v",
            "libx264",
            str(edited),
        ]
    )
    result = analyze(original, edited)
    assert result["status"] == "matched"
    assert {f["kind"] for f in result["findings"]} == {"reordering"}
