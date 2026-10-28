"""Five-call normal-path check on frozen hybrid; no seeded failures or repair retry."""
import json,time,argparse
from pathlib import Path
from veil import VeilClient
from benchmark_support import archive_local_evidence

parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path('artifacts/public-footage-001'))
base=parser.parse_args().root
root=base/'normal-run'
if root.exists():raise SystemExit('Normal run exists; refusing automatic rerun')
root.mkdir();start=time.monotonic()
with VeilClient(base_url='http://127.0.0.1:8019') as c:
 job=c.create_job(base/'challenge.mp4')
 (root/'job-id.txt').write_text(job['id']+'\n')
 c.cloud_action(job['id'],'detect')
 c.process(job['id'])
 job=c.cloud_action(job['id'],'verify')
 c.download(job['id'],root/'final-export.mp4')
 report=c.verification(job['id']);receipt=c.receipt(job['id'])
 archive_local_evidence(job['id'],root/'provider-evidence')
 for name,data in [('audit.json',report),('receipt.json',receipt),('result.json',{'job':job,'latency_s':time.monotonic()-start,'estimated_usd':receipt['estimated_api_cost_usd'],'seeded_failure':False})]:
  (root/name).write_text(json.dumps(data,indent=2)+'\n')
 print(json.dumps({'status':job['verification'],'estimated_usd':receipt['estimated_api_cost_usd'],'latency_s':time.monotonic()-start},indent=2))
