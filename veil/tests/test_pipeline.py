"""Local unit checks only: no model responses are fabricated as product evidence."""
import pytest
from fastapi.testclient import TestClient
from veil.api.app import create_app
from veil.core.pipeline import speech_intervals, sample_frames
from veil.providers.vision import Observations
from pathlib import Path


def test_cloud_calls_require_explicit_consent(tmp_path):
    with TestClient(create_app(tmp_path)) as client:
        assert client.post('/v1/jobs/'+'0'*32+'/detect',json={}).status_code==422
        assert client.post('/v1/jobs/'+'0'*32+'/verify',json={
            'allow_cloud_transfer':False,'media_is_synthetic_or_consented':True}).status_code==422
        assert client.post('/v1/jobs/'+'0'*32+'/verify',json={
            'allow_cloud_transfer':True,'media_is_synthetic_or_consented':True,
            'seed_omit_phone':True}).status_code==422


def test_speech_redaction_conservative_envelope_and_fallback():
    intervals=speech_intervals({'transcript':'The phone number is 55460146','turns':[
        {'startMs':2540,'endMs':8060},{'startMs':8300,'endMs':8940}]},18000)
    assert (intervals[0].start_ms,intervals[0].end_ms)==(2040,9440)
    assert speech_intervals({'transcript':'ordinary background conversation'},18000)==[]
    full=speech_intervals({'transcript':'my phone number is two zero two'},18000)
    assert (full[0].start_ms,full[0].end_ms)==(0,18000)


def test_sampling_reads_actual_video_at_bounded_timestamps(tmp_path):
    source=Path(__file__).resolve().parents[1]/'artifacts/smoke-001/input.mp4'
    frames=sample_frames(source,tmp_path,'test',{'duration_ms':18000,'fps':10})
    assert len(frames)==3
    assert all(path.is_file() for _,path in frames)
    assert [t for t,_ in frames]==[2000,7600,16000]


def test_observation_schema_rejects_unknown_categories():
    with pytest.raises(ValueError):
        Observations.model_validate({'frames':[{'time_ms':0,'exposures':[
            {'category':'invented','box':[0,0,1,1],'text':None,'reason':'invalid'}]}]})


def test_normalized_coordinate_contract_is_explicit():
    from veil.providers.vision import NormalizedObservations
    assert NormalizedObservations.model_validate({'coordinate_space':'normalized_0_1000','frames':[]})
    with pytest.raises(ValueError):
        NormalizedObservations.model_validate({'coordinate_space':'source_pixels','frames':[]})


def test_ocr_pattern_from_actual_export(tmp_path):
    import platform
    import shutil
    if platform.system()!='Darwin' or not shutil.which('swiftc'):
        pytest.skip('macOS Vision adapter unavailable')
    from veil.verification.ocr import inspect_text
    root=Path(__file__).resolve().parents[1]
    # Reuse an already compiled local binary; never compile or call cloud models in this test.
    cache=root/'artifacts/private/ocr-cache'
    if not (cache/'veil-local-ocr').exists():
        pytest.skip('Compile adapter once using the documented local setup')
    result=inspect_text([(2000,root/'artifacts/smoke-001/export-check.jpg'),(7500,root/'artifacts/smoke-001/protected-7500.jpg')],960,540,cache)
    assert result['status']=='completed'
    assert any('202-555-0146' in f['text'] for f in result['findings'])
    assert not any(f['time_ms']==7500 for f in result['findings'])
    assert all(0<=f['box'][1]<f['box'][3]<=540 for f in result['findings'])


def test_repair_envelope_keeps_all_observed_fragments():
    from veil.core.pipeline import repair_seeds
    # Unit data only: verifies the first-fragment regression, not model accuracy.
    report={'frames':[{'time_ms':2000,'exposures':[
        {'category':'license_plate','box':[10,20,40,50]},
        {'category':'license_plate','box':[70,22,100,48]}]},
        {'time_ms':4000,'exposures':[{'category':'license_plate','box':[50,20,80,50]}]}]}
    assert list(repair_seeds(report))==[('license_plate',2000,[10,20,100,50],2)]


def test_sdk_workflow_requires_explicit_permission_before_network():
    from veil import VeilClient
    with VeilClient() as client:
        with pytest.raises(ValueError):
            client.protect('does-not-exist.mp4','out.mp4',allow_cloud_transfer=False,
                           media_is_synthetic_or_consented=True)
