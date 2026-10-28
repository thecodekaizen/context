"""Real HTTP/SDK roundtrip using synthetic media and saved reviewed geometry."""
import json
from pathlib import Path
from veil import VeilClient

root=Path('artifacts/smoke-001')
timeline=json.loads((root/'timeline.json').read_text())
timeline['visual_tracks'].extend(json.loads((root/'field-repair-timeline.json').read_text())['visual_tracks'])
with VeilClient(base_url='http://127.0.0.1:8018') as client:
    job=client.create_job(root/'input.mp4')
    result=client.process(job['id'],timeline)
    client.download(job['id'],'artifacts/api-export.mp4')
    receipt=client.receipt(job['id'])
Path('artifacts/api-roundtrip.json').write_text(json.dumps({'job':result,'receipt':receipt,'model_calls':0,'timeline_source':'saved real smoke inference plus reviewed full-field repair geometry'},indent=2)+'\n')
print(json.dumps({'job_id':job['id'],'status':result['status'],'decoded_frames':receipt['media_inspection']['decoded_frames'],'privacy_verification':receipt['privacy_verification']}))
