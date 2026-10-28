"""Generate fictional fixture imagery with Meta; no real likeness or reference."""
import argparse,base64
from pathlib import Path
from veil.providers.common import client,Calls,save
p=argparse.ArgumentParser();p.add_argument('--env-file',required=True);p.add_argument('--output',type=Path,required=True)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
c=client(a.env_file);ledger=Calls(a.output);name='fictional-face-source'
t=ledger.begin(name,'muse-image-1.0','/v1/images/generations','Text prompt only; no personal media')
try:
 r=c.images.generate(model='muse-image-1.0',prompt='A clear front-facing head-and-shoulders studio photograph of a wholly fictional adult person, neutral expression, plain pale blue background, entire face unobstructed, natural lighting, no text, no logos, no resemblance to any named or real person. Synthetic privacy-engine test fixture.',n=1,response_format='b64_json',extra_body={'reasoning_strength':'low','output_format':'png','tool_enablement':{'enable_web_search':False,'enable_image_search':False,'enable_shell':False}})
 (a.output/'fictional-face.png').write_bytes(base64.b64decode(r.data[0].b64_json))
 ledger.finish(name,t,estimated_usd=.01,note='Fixture source only, not a privacy-engine model role')
 save(a.output/'face-provenance.json',{'source':'Meta generated fictional adult','real_person_media':False,'no_reference_images':True,'usage':'synthetic fixture only'})
 print('Saved fictional-face.png')
except Exception as exc:ledger.fail(name,t,exc);raise
