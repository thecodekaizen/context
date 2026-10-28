"""Fresh inference on exported media only, without original findings or truth."""
import argparse,base64,json,subprocess
from pathlib import Path
import cv2,httpx2
from veil.providers.common import client,Calls,save
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--env-file',required=True);a=p.parse_args()
root=a.root;c=client(a.env_file);ledger=Calls(root,max_calls=12)
cap=cv2.VideoCapture(str(root/'redacted.mp4'));cap.set(cv2.CAP_PROP_POS_MSEC,2000);ok,frame=cap.read();cap.release()
if not ok:raise ValueError('Export does not decode')
cv2.imwrite(str(root/'export-check.jpg'),frame)
name='spark-export-inspection';t=ledger.begin(name,'muse-spark-1.3','/v1/responses','One frame decoded from actual exported MP4; no input findings or fixture labels')
try:
 schema={'type':'object','properties':{'residual_exposures':{'type':'array','items':{'type':'object','properties':{
  'category':{'type':'string','enum':['face','license_plate','phone_number','other']},'visible_text':{'type':['string','null']},'box':{'type':'array','items':{'type':'number'}},'reason':{'type':'string'}},
  'required':['category','visible_text','box','reason'],'additionalProperties':False}}},'required':['residual_exposures'],'additionalProperties':False}
 r=c.responses.create(model='muse-spark-1.3',reasoning={'effort':'minimal'},max_output_tokens=1500,
  input=[{'role':'user','content':[{'type':'input_text','text':'Inspect this exported video frame for still-visible privacy exposures: recognizable facial features, readable vehicle plate identifiers, readable phone numbers. Opaque covers alone are not evidence of a leak. Report visible evidence only. Boxes use source pixels for 960x540 image. Do not assume what the original contained. An empty list means no exposure observed in this frame, not a privacy guarantee.'},
  {'type':'input_image','image_url':'data:image/jpeg;base64,'+base64.b64encode((root/'export-check.jpg').read_bytes()).decode()}]}],text={'format':{'type':'json_schema','name':'export_exposures','strict':True,'schema':schema}})
 save(root/'spark-export-raw.json',r.model_dump(mode='json'));result=json.loads(r.output_text);save(root/'export-visual-inspection.json',result)
 usage=r.usage.model_dump();ledger.finish(name,t,usage=usage,estimated_usd=(usage['input_tokens']*1.25+usage['output_tokens']*4.25)/1e6)
 print('Fresh export visual inspection:',result,flush=True)
except Exception as exc:ledger.fail(name,t,exc);raise
subprocess.run(['ffmpeg','-y','-i',str(root/'redacted.mp4'),'-vn','-ac','1','-ar','24000','-c:a','pcm_s16le',str(root/'export-audio.wav')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
name='voice-export-inspection';t=ledger.begin(name,'muse-voice-transcribe-1.0','/v1/asr/transcribe','Audio extracted from actual exported MP4 only')
try:
 with (root/'export-audio.wav').open('rb') as audio:
  r=httpx2.post('https://api.meta.ai/v1/asr/transcribe',headers={'Authorization':'Bearer '+c.api_key},files={
    'request':(None,json.dumps({'model':'muse-voice-transcribe-1.0','mode':'ENDPOINTING','audioEncoding':'WAV'}),'application/json'),
    'audio':('export.wav',audio,'audio/wav')},timeout=90.)
 r.raise_for_status();result=r.json();save(root/'export-audio-inspection.json',result);ledger.finish(name,t,estimated_usd=.0009)
 print('Fresh export audio transcription:',result.get('transcript'),flush=True)
except Exception as exc:ledger.fail(name,t,exc);raise
