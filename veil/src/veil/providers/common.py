"""Local credentials and a small explicitly authorized synthetic-data ledger."""
from pathlib import Path
import json,os,time,hashlib
from openai import OpenAI


def client(env_path):
    key=os.getenv('MODEL_API_KEY')
    if not key:
        for line in Path(env_path).read_text().splitlines():
            if line.strip().startswith('MODEL_API_KEY='):
                key=line.split('=',1)[1].strip().strip('\"\'')
    if not key:raise ValueError('MODEL_API_KEY unavailable')
    return OpenAI(api_key=key,base_url='https://api.meta.ai/v1',max_retries=0,timeout=180)


class Calls:
    def __init__(self,root,max_calls=12):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.limit=max_calls
        self.path=self.root/'calls.json'
    def read(self):return json.loads(self.path.read_text()) if self.path.exists() else []
    def begin(self,name,model,endpoint,media):
        rows=self.read()
        if len(rows)>=self.limit:raise ValueError('Smoke call cap exhausted')
        if any(r['name']==name for r in rows):raise ValueError('Attempt already reserved; no automatic retry')
        record={'name':name,'model':model,'endpoint':endpoint,'status':'reserved',
                'cloud_transfer':media,'started_unix_s':time.time()}
        rows.append(record);self.path.write_text(json.dumps(rows,indent=2)+'\n');return time.monotonic()
    def finish(self,name,start,**details):
        rows=self.read();row=next(r for r in rows if r['name']==name)
        row.update(status='completed',latency_s=time.monotonic()-start,**details)
        self.path.write_text(json.dumps(rows,indent=2)+'\n')
    def fail(self,name,start,exc):
        rows=self.read();next(r for r in rows if r['name']==name).update(status='failed_no_retry',latency_s=time.monotonic()-start,error_type=type(exc).__name__)
        self.path.write_text(json.dumps(rows,indent=2)+'\n')

def save(path,value):Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
