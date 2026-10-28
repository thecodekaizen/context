import pytest
from veil.media.sampling import periodic_indices


def test_dense_schedule_includes_endpoints_and_brief_exposure():
    indices=periodic_indices(96,12)
    assert indices[0]==0 and indices[-1]==95
    assert len(indices)==33
    assert 24 in indices
    assert max(b-a for a,b in zip(indices,indices[1:]))<=3


def test_sampling_budget_is_hard_not_silent_downsampling():
    with pytest.raises(ValueError):periodic_indices(10000,12)
    for count,fps in ((0,12),(12,0),(12,float('nan'))):
        with pytest.raises(ValueError):periodic_indices(count,fps)


def test_low_fps_never_duplicates_or_invents_frames():
    assert periodic_indices(3,2)==[0,1,2]
    assert periodic_indices(1,12)==[0]


@pytest.mark.parametrize('case,expected_times',[('clip-b',[2000]),('clip-c',[])])
def test_dense_local_audit_on_actual_short_exposure_and_negative(case,expected_times,tmp_path):
    import platform,shutil
    from pathlib import Path
    from veil.media.sampling import periodic_frames
    from veil.verification.ocr import inspect_text
    from veil.media.inspect import inspect_media
    root=Path(__file__).resolve().parents[1]
    cache=root/'artifacts/private/ocr-cache'
    if platform.system()!='Darwin' or not shutil.which('swiftc') or not (cache/'veil-local-ocr').exists():
        pytest.skip('Local compiled macOS OCR adapter unavailable')
    source=root/'artifacts/verifier-benchmark-001'/case/'export.mp4'
    frames=periodic_frames(source,tmp_path,'check',inspect_media(source))
    result=inspect_text(frames,960,540,cache)
    assert result['status']=='completed'
    assert [f['time_ms'] for f in result['findings']]==expected_times
