"""Targeted repair based only on independent exported-frame findings."""
import argparse,json,cv2,base64
from pathlib import Path
from veil.providers.common import client,Calls,save
from veil.providers.sam import segment
from veil.core.models import Timeline,VisualTrack,FrameRegion
from veil.media.redact import render
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--env-file',required=True);a=p.parse_args()
root=a.root;c=client(a.env_file);ledger=Calls(root,max_calls=12)
findings=json.loads((root/'export-visual-inspection.json').read_text())['residual_exposures']
if not findings:raise ValueError('No residual exposure was independently observed')
finding=findings[0];x1,y1,x2,y2=finding['box'];x=max(0,min(959,round((x1+x2)/2)));y=max(0,min(539,round((y1+y2)/2)))
prompt=f'<20f>9<|point;x={x};y={y};w=960;h=540|>'
save(root/'repair-request.json',{'source':'independent actual-export review','finding':finding,'prompt':prompt,'ground_truth_used':False})
f=None
try:
 with (root/'redacted.mp4').open('rb') as media:f=c.files.create(file=media,purpose='user_data',expires_after={'anchor':'created_at','seconds':3600})
 regions=segment(c,ledger,root,'sam-repair-track',prompt,file_id=f.id)
finally:
 if f:
  try:c.files.delete(f.id)
  except Exception:pass
track=VisualTrack(id='repair-'+regions[0]['track_id'],category=finding['category'],source='sam-3.1/export-review-point',regions=[FrameRegion(frame=r['frame'],box=r['box']) for r in regions])
timeline=Timeline(duration_ms=18000,fps=10,width=960,height=540,visual_tracks=[track],audio_intervals=[])
save(root/'repair-timeline.json',timeline.model_dump(mode='json'))
result=render(root/'redacted.mp4',root/'repaired.mp4',timeline);save(root/'repair-render.json',result)
cap=cv2.VideoCapture(str(root/'repaired.mp4'));cap.set(cv2.CAP_PROP_POS_MSEC,2000);ok,frame=cap.read();cap.release()
if not ok:raise ValueError('Repaired output cannot be decoded')
cv2.imwrite(str(root/'repaired-sample.jpg'),frame)
name='spark-repaired-inspection';t=ledger.begin(name,'muse-spark-1.3','/v1/responses','One frame from actual repaired MP4, no expected findings or ground truth')
try:
 schema={'type':'object','properties':{'residual_exposures':{'type':'array','items':{'type':'object','properties':{
  'category':{'type':'string','enum':['face','license_plate','phone_number','other']},'visible_text':{'type':['string','null']},'reason':{'type':'string'}},
  'required':['category','visible_text','reason'],'additionalProperties':False}}},'required':['residual_exposures'],'additionalProperties':False}
 r=c.responses.create(model='muse-spark-1.3',reasoning={'effort':'minimal'},max_output_tokens=1200,input=[{'role':'user','content':[
  {'type':'input_text','text':'Inspect this exported frame for still-visible privacy exposures: recognizable facial features, readable vehicle plate identifiers, readable phone numbers. An opaque cover alone is not evidence of a leak. Report observed evidence only. Do not infer what an original video might have contained. An empty result is limited to this frame, not a privacy guarantee.'},
  {'type':'input_image','image_url':'data:image/jpeg;base64,'+base64.b64encode((root/'repaired-sample.jpg').read_bytes()).decode()}]}],text={'format':{'type':'json_schema','name':'repaired_privacy_review','strict':True,'schema':schema}})
 save(root/'repaired-inspection-raw.json',r.model_dump(mode='json'));result=json.loads(r.output_text);save(root/'repaired-visual-inspection.json',result)
 usage=r.usage.model_dump();ledger.finish(name,t,usage=usage,estimated_usd=(usage['input_tokens']*1.25+usage['output_tokens']*4.25)/1e6)
 print('Repaired export sample inspection:',result)
except Exception as exc:ledger.fail(name,t,exc);raise
