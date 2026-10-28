from context_core.media import digest, playback_file, probe, run


def test_compatible_mp4_preserves_bytes(clips, tmp_path):
    source = clips / "original.mp4"
    assert playback_file(source, tmp_path / "preview.mp4") == source
    assert not (tmp_path / "preview.mp4").exists()


def test_non_mp4_gets_browser_preview(clips, tmp_path):
    source = tmp_path / "recording.mkv"
    # H.264 in Matroska is decodable but not a broadly compatible video/mp4 response.
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(clips / "original.mp4"),
            "-c",
            "copy",
            str(source),
        ]
    )
    original_hash = digest(source)
    preview = playback_file(source, tmp_path / "preview.mp4")
    info = probe(preview)
    assert info["codec"] == "h264" and info["pixel_format"] == "yuv420p"
    assert "mp4" in info["container"]
    assert abs(info["duration"] - probe(source)["duration"]) <= 0.5
    assert digest(source) == original_hash


def test_odd_dimensions_get_even_browser_preview(tmp_path):
    source = tmp_path / "odd.mkv"
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "testsrc=size=321x181:rate=12:duration=1",
            "-c:v",
            "ffv1",
            str(source),
        ]
    )
    preview = playback_file(source, tmp_path / "preview.mp4")
    info = probe(preview)
    assert info["width"] % 2 == 0 and info["height"] % 2 == 0
    assert info["pixel_format"] == "yuv420p"
