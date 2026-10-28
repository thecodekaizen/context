"""Render explicit optional face blur from real saved geometry, then audit new bytes."""
import argparse,json,hashlib,cv2
from pathlib import Path
from veil.core.models import Timeline
from veil.core.pipeline import MetaPipeline
from veil.media.redact import render
from veil.media.inspect import inspect_media,decode_export

parser=argparse.ArgumentParser();parser.add_argument('--env-file',required=True);parser.add_argument('--output',type=Path,default=Path('artifacts/face-blur-001'))
a=parser.parse_args()
root=a.output
if root.exists():raise SystemExit('Style run exists; refusing automatic rerun')
root.mkdir()
evidence=Path('artifacts/live-pipeline-003/provider-evidence')
data=json.loads((evidence/'timeline.json').read_text())
data['visual_tracks'].extend(json.loads((evidence/'repair-timeline.json').read_text())['visual_tracks'])
for track in data['visual_tracks']:
 track['action']='blur' if track['category']=='face' else 'cover'
timeline=Timeline.model_validate(data)
(root/'timeline.json').write_text(timeline.model_dump_json(indent=2)+'\n')
source=Path('artifacts/smoke-001/input.mp4')
render(source,root/'export.mp4',timeline)
media=inspect_media(root/'export.mp4')
inspection=decode_export(root/'export.mp4')
cap=cv2.VideoCapture(str(root/'export.mp4'))
for ms in (2000,7600,16000):
 cap.set(cv2.CAP_PROP_POS_MSEC,ms);ok,frame=cap.read()
 if ok:cv2.imwrite(str(root/f'frame-{ms}.jpg'),frame)
cap.release()
# This is fresh output verification, not reuse of the opaque variant's passing audit.
audit=MetaPipeline(a.env_file,max_calls=2).verify(root,media,0)
ledger=json.loads((root/'calls.json').read_text())
receipt={'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'output_sha256':hashlib.sha256((root/'export.mp4').read_bytes()).hexdigest(),
 'face_action':'blur','text_action':'cover','automatic_default':'cover',
 'geometry_source':'saved real live-pipeline-003 observations; no ground truth used',
 'verification':audit,'media_inspection':inspection,'model_requests':len(ledger),
 'estimated_usd':sum(c.get('estimated_usd',0) for c in ledger),
 'zero_leaks_guaranteed':False,'needs_human_review':True,
 'limitations':['Gaussian face blur is not a validated identity-anonymization guarantee','geometry remains padded boxes, not SAM contours','only one composited synthetic clip']}
(root/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'audit_status':audit['status'],'model_requests':len(ledger),'estimated_usd':receipt['estimated_usd']},indent=2))
