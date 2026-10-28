import json
from fastapi.testclient import TestClient
from context_core.api import app

client=TestClient(app)

def test_upload_and_evidence(clips):
    with (clips/'original.mp4').open('rb') as a,(clips/'omission.mp4').open('rb') as b:
        r=client.post('/api/analyze',files={'original':('source.mp4',a,'video/mp4'),'edited':('edit.mp4',b,'video/mp4')})
    assert r.status_code==200,r.text
    data=r.json()
    assert data['findings'][0]['kind']=='omission'
    saved=client.get(f"/api/media/{data['id']}/evidence.json")
    assert saved.json()==data
    media=client.get(data['media']['source'],headers={'Range':'bytes=0-99'})
    assert media.status_code==206
    assert len(media.content)==100

def test_bad_upload_and_path():
    r=client.post('/api/analyze',files={'original':('bad.mp4',b'bad'),'edited':('bad.mp4',b'bad')})
    assert r.status_code==422
    assert client.get('/api/media/demo/secret.env').status_code==404

def test_health():
    assert client.get('/api/health').json()['status']=='ok'

def test_review_without_key(clips,monkeypatch):
    monkeypatch.delenv('MODEL_API_KEY',raising=False)
    r=client.post('/api/demo')
    assert r.status_code==200
    response=client.post('/api/investigations/demo/interpret/f0')
    assert response.status_code==503
    assert 'MODEL_API_KEY' in response.json()['detail']
    assert client.post('/api/investigations/not-valid/interpret/f0').status_code==404
