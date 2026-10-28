"""Real model calls on a generated clip. No fixture answer key enters inference."""
import argparse,base64,json,time
from pathlib import Path
from veil.providers.common import client,Calls,save
from veil.providers.sam import segment


def main():
 p=argparse.ArgumentParser();p.add_argument('--env-file',required=True);p.add_argument('--root',type=Path,required=True);a=p.parse_args()
 root=a.root;c=client(a.env_file);ledger=Calls(root,max_calls=12);summary={'real_api_calls':True,'synthetic_only':True,'experiments':{}}
 def run(name,fn):
  try:result=fn();summary['experiments'][name]={'status':'verified_by_api_test','result':result}
  except Exception as exc:
   summary['experiments'][name]={'status':'failed','error_type':type(exc).__name__,'error':str(exc)[:300]}
  save(root/'smoke-results.json',summary);print(name,summary['experiments'][name]['status'],flush=True)
 for category,prompt in [('face','human face'),('plate','vehicle license plate')]:
  run(f'sam-image-{category}',lambda category=category,prompt=prompt:segment(c,ledger,root,f'sam-image-{category}',prompt,image=root/'sample.jpg'))
 file=None
 try:
  with (root/'input.mp4').open('rb') as source:file=c.files.create(file=source,purpose='user_data',expires_after={'anchor':'created_at','seconds':3600})
  save(root/'upload.json',{'file_id':file.id,'synthetic_only':True,'purpose':'SAM video smoke','expires_after_seconds':3600})
  for category,prompt in [('face','human face'),('plate','vehicle license plate')]:
   run(f'sam-video-{category}',lambda category=category,prompt=prompt:segment(c,ledger,root,f'sam-video-{category}',prompt,file_id=file.id))
 finally:
  if file:
   try:c.files.delete(file.id);save(root/'upload-cleanup.json',{'deleted':True})
   except Exception:save(root/'upload-cleanup.json',{'deleted':False,'fallback':'one-hour expiry'})
 def voice():
  name='voice-original';t=ledger.begin(name,'muse-voice-transcribe-1.0','/v1/asr/transcribe','Synthetic 18-second mono 24kHz PCM WAV')
  try:
   import httpx2
   with (root/'audio.wav').open('rb') as audio:
    response=httpx2.post('https://api.meta.ai/v1/asr/transcribe',headers={'Authorization':'Bearer '+c.api_key},files={
       'request':(None,json.dumps({'model':'muse-voice-transcribe-1.0','mode':'ENDPOINTING','audioEncoding':'WAV','languageBias':['English']}),'application/json'),
       'audio':('synthetic.wav',audio,'audio/wav')},timeout=90.)
   response.raise_for_status();r=response.json();save(root/'voice-original.json',r)
   ledger.finish(name,t,estimated_usd=.0009,audio_seconds=18)
   return r
  except Exception as exc:ledger.fail(name,t,exc);raise
 run('voice',voice)
 def spark():
  name='spark-original';t=ledger.begin(name,'muse-spark-1.3','/v1/responses','One synthetic JPEG frame')
  schema={'type':'object','properties':{'findings':{'type':'array','items':{'type':'object','properties':{
     'category':{'type':'string','enum':['face','license_plate','phone_number','other']},'text':{'type':['string','null']},
     'box':{'type':'array','items':{'type':'number'}},'reason':{'type':'string'}},'required':['category','text','box','reason'],'additionalProperties':False}}},'required':['findings'],'additionalProperties':False}
  try:
   r=c.responses.create(model='muse-spark-1.3',reasoning={'effort':'minimal'},max_output_tokens=1500,input=[{'role':'user','content':[
    {'type':'input_text','text':'Inspect this synthetic video frame for privacy exposures: human faces, vehicle license plates, and phone numbers. Exclude headings and ordinary background. Return every detected exposure with tight box [left,top,right,bottom] in source image pixels (960 by 540). Do not assume an exposure exists unless visible. Report observed strings; do not invent confidence.'},
    {'type':'input_image','image_url':'data:image/jpeg;base64,'+base64.b64encode((root/'sample.jpg').read_bytes()).decode()}]}],text={'format':{'type':'json_schema','name':'privacy_findings','strict':True,'schema':schema}})
   save(root/'spark-original-raw.json',r.model_dump(mode='json'));result=json.loads(r.output_text);save(root/'spark-original.json',result)
   usage=r.usage.model_dump();cost=(usage['input_tokens']*1.25+usage['output_tokens']*4.25)/1e6
   ledger.finish(name,t,usage=usage,estimated_usd=cost);return result
  except Exception as exc:ledger.fail(name,t,exc);raise
 run('spark',spark)
 save(root/'smoke-results.json',summary)
if __name__=='__main__':main()
