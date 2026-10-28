import numpy as np
import pytest
from veil.core.models import VisualTrack
from veil.media.redact import apply_redactions


def test_blur_is_face_only_and_cover_is_default():
    values={'id':'track','category':'face','source':'unit','regions':[]}
    assert VisualTrack(**values).action=='cover'
    assert VisualTrack(**values,action='blur').action=='blur'
    for category in ('license_plate','phone_number'):
        with pytest.raises(ValueError):VisualTrack(**{**values,'category':category},action='blur')


def test_cover_wins_overlap_in_either_operation_order():
    original=np.random.default_rng(7).integers(80,256,(80,100,3),dtype=np.uint8)
    operations=[((10,10,80,70),'blur'),((30,30,60,50),'cover')]
    for order in (operations,operations[::-1]):
        result=apply_redactions(original.copy(),order,padding=0)
        assert np.max(result[30:50,30:60])==0
        assert np.array_equal(result[:10],original[:10])
        assert not np.array_equal(result[10:30,10:80],original[10:30,10:80])


def test_original_sensitive_pixels_do_not_spread_outside_cover_through_blur():
    plain=np.full((80,100,3),150,dtype=np.uint8)
    with_secret=plain.copy();with_secret[30:50,30:60]=255
    operations=[((10,10,80,70),'blur'),((30,30,60,50),'cover')]
    assert np.array_equal(apply_redactions(plain,operations,padding=0),
                          apply_redactions(with_secret,operations,padding=0))


def test_explicit_face_style_is_detection_only_in_api(tmp_path):
    from fastapi.testclient import TestClient
    from veil.api.app import create_app,CloudRequest
    assert CloudRequest.model_validate({'allow_cloud_transfer':True,
        'media_is_synthetic_or_consented':True,'face_action':'blur'}).face_action=='blur'
    with TestClient(create_app(tmp_path)) as client:
        response=client.post('/v1/jobs/'+'0'*32+'/verify',json={
            'allow_cloud_transfer':True,'media_is_synthetic_or_consented':True,'face_action':'blur'})
        assert response.status_code==422
