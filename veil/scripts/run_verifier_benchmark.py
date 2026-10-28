"""Exactly six real calls on three synthetic exports; no labels or answer keys loaded."""
from pathlib import Path
import argparse,json,hashlib,time
from veil.core.pipeline import MetaPipeline
from veil.media.inspect import inspect_media

p=argparse.ArgumentParser();p.add_argument('--env-file',required=True);p.add_argument('--root',type=Path,default=Path('artifacts/verifier-benchmark-001'));a=p.parse_args()
root=a.root
if (root/'baseline-started.json').exists():raise SystemExit('Baseline already attempted; no automatic rerun')
manifest={'maximum_model_requests':6,'cases':[],'truth_loaded':False,'model_retries':0}
for name in ('clip-a','clip-b','clip-c'):
 path=root/name/'export.mp4'
 if (root/name/'calls.json').exists():raise SystemExit('Case ledger already exists')
 manifest['cases'].append({'id':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(root/'baseline-started.json').write_text(json.dumps(manifest,indent=2)+'\n')
pipeline=MetaPipeline(a.env_file)
results=[]
for item in manifest['cases']:
 folder=root/item['id'];started=time.monotonic()
 try:
  media=inspect_media(folder/'export.mp4')
  report=pipeline.verify(folder,media,0,sparse_ocr=True)
  record={'id':item['id'],'status':'completed','audit_status':report['status'],'latency_s':time.monotonic()-started}
 except Exception as exc:
  record={'id':item['id'],'status':'failed','error_type':type(exc).__name__,'latency_s':time.monotonic()-started}
 ledger=json.loads((folder/'calls.json').read_text()) if (folder/'calls.json').exists() else []
 record.update(model_requests=len(ledger),estimated_usd=sum(x.get('estimated_usd',0) for x in ledger))
 results.append(record)
 (root/'baseline-results.json').write_text(json.dumps(results,indent=2)+'\n')
 print(record,flush=True)
assert sum(r['model_requests'] for r in results)<=6
