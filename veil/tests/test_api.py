import json
from pathlib import Path
from fastapi.testclient import TestClient
from veil.api.app import create_app
from veil.core.jobs import Conflict
from veil.core.models import Timeline
from veil.media.inspect import decode_export
import pytest

FIXTURE = Path(__file__).resolve().parents[1] / 'artifacts/smoke-001'


def test_real_upload_render_download_and_receipt(tmp_path):
    app = create_app(tmp_path / 'jobs')
    with TestClient(app) as client:
        with (FIXTURE / 'input.mp4').open('rb') as media:
            response = client.post('/v1/jobs', files={'video': ('../../outside.mp4', media, 'video/mp4')})
        assert response.status_code == 201, response.text
        job = response.json()
        job_id = job['id']
        assert client.get(f'/v1/jobs/{job_id}/export').status_code == 409
        timeline = json.loads((FIXTURE / 'timeline.json').read_text())
        repair = json.loads((FIXTURE / 'field-repair-timeline.json').read_text())
        timeline['visual_tracks'].extend(repair['visual_tracks'])
        response = client.post(f'/v1/jobs/{job_id}/redact', json=timeline)
        assert response.status_code == 200, response.text
        assert response.json()['status'] == 'rendered'
        receipt = client.get(f'/v1/jobs/{job_id}/receipt').json()
        assert receipt['privacy_verification'] == 'not_run'
        assert receipt['zero_leaks_guaranteed'] is False
        assert receipt['media_inspection']['decoded_frames'] == 180
        exported = client.get(f'/v1/jobs/{job_id}/export')
        assert exported.status_code == 200
        target = tmp_path / 'download.mp4'
        target.write_bytes(exported.content)
        assert decode_export(target)['decoded_frames'] == 180
        assert client.post(f'/v1/jobs/{job_id}/redact', json=timeline).status_code == 409
        assert client.get(f'/v1/jobs/{job_id}').json()['verification'] == 'not_run'
        assert not (tmp_path / 'outside.mp4').exists()


def test_invalid_upload_and_unknown_job(tmp_path):
    with TestClient(create_app(tmp_path)) as client:
        assert client.post('/v1/jobs', files={'video': ('bad.mp4', b'not a video')}).status_code == 422
        assert list(tmp_path.iterdir()) == []
        assert client.get('/v1/jobs/' + '0' * 32).status_code == 404


def test_lock_prevents_concurrent_mutations(tmp_path):
    app = create_app(tmp_path)
    with (FIXTURE / 'input.mp4').open('rb') as stream:
        job = app.state.store.create(stream)
    with app.state.store.lock(job['id']):
        with pytest.raises(Conflict):
            with app.state.store.lock(job['id']):
                pass
    assert not (tmp_path / job['id'] / '.lock').exists()


def test_invalid_timeline_leaves_job_uploaded(tmp_path):
    app=create_app(tmp_path)
    with (FIXTURE/'input.mp4').open('rb') as stream:
        job=app.state.store.create(stream)
    timeline=json.loads((FIXTURE/'timeline.json').read_text())
    timeline['width']=10
    with pytest.raises(ValueError):
        app.state.store.redact(job['id'],Timeline.model_validate(timeline))
    assert app.state.store.get(job['id'])['status']=='uploaded'
