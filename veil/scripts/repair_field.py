"""Repair full observed field; detector metadata and fixture truth are not consulted."""
import argparse,json,cv2,base64,hashlib
from pathlib import Path
from veil.providers.common import client,Calls,save
from veil.core.models import Timeline,VisualTrack
from veil.media.track import track_field
from veil.media.redact import render
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--env-file',required=True);a=p.parse_args()
root=a.root
finding=next(f for f in json.loads((root/'export-visual-inspection.json').read_text())['residual_exposures'] if f['category']=='phone_number')
regions,uncertain=track_field(root/'redacted.mp4',20,finding['box'])
timeline=Timeline(duration_ms=18000,fps=10,width=960,height=540,visual_tracks=[VisualTrack(id='full-field-repair',category='phone_number',source='export-review/opencv-optical-flow',regions=regions)],audio_intervals=[])
save(root/'field-repair-timeline.json',timeline.model_dump(mode='json'))
result=render(root/'redacted.mp4',root/'protected.mp4',timeline)
save(root/'field-repair-render.json',{**result,'tracking_uncertain_frames':uncertain,
 'rule':'Cover complete observed field, with frame-specific optical-flow geometry; full-frame fail-closed cover on tracking loss',
 'source':'independent review of actual exported video','ground_truth_used':False})
cap=cv2.VideoCapture(str(root/'protected.mp4'));content=[{'type':'input_text','text':'Inspect each of these exported video frames for still-visible privacy exposures: recognizable facial features, readable vehicle plate identifiers, readable phone numbers. Opaque covers alone are not leaks. Only report visible evidence. Do not infer original content. Return one result for each supplied timestamp; empty findings are scoped to those frames only, never a guarantee for the full video.'}]
for ms in (2000,7500,16000):
 cap.set(cv2.CAP_PROP_POS_MSEC,ms);ok,frame=cap.read()
 if not ok:raise ValueError('Protected export cannot decode')
 path=root/f'protected-{ms}.jpg';cv2.imwrite(str(path),frame)
 content.extend([{'type':'input_text','text':f'Frame timestamp: {ms} ms'},{'type':'input_image','image_url':'data:image/jpeg;base64,'+base64.b64encode(path.read_bytes()).decode()}])
cap.release()
ledger=Calls(root/'field-repair-audit',max_calls=1);c=client(a.env_file);name='protected-export-review'
t=ledger.begin(name,'muse-spark-1.3','/v1/responses','Three decoded frames from actual protected MP4; independent of original detections and evaluation truth')
try:
 schema={'type':'object','properties':{'frames':{'type':'array','items':{'type':'object','properties':{'time_ms':{'type':'integer'},'exposures':{'type':'array','items':{'type':'object','properties':{'category':{'type':'string'},'visible_text':{'type':['string','null']},'reason':{'type':'string'}},'required':['category','visible_text','reason'],'additionalProperties':False}}},'required':['time_ms','exposures'],'additionalProperties':False}}},'required':['frames'],'additionalProperties':False}
 r=c.responses.create(model='muse-spark-1.3',reasoning={'effort':'minimal'},max_output_tokens=1500,input=[{'role':'user','content':content}],text={'format':{'type':'json_schema','name':'protected_frames_review','strict':True,'schema':schema}})
 save(root/'protected-review-raw.json',r.model_dump(mode='json'));review=json.loads(r.output_text);save(root/'protected-review.json',review)
 usage=r.usage.model_dump();ledger.finish(name,t,usage=usage,estimated_usd=(usage['input_tokens']*1.25+usage['output_tokens']*4.25)/1e6)
 print('Protected export independent review:',review)
except Exception as exc:ledger.fail(name,t,exc);raise
