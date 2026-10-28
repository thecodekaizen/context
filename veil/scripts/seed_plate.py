"""Follow Spark-observed objects with SAM; never read fixture ground truth."""
import argparse,json
from pathlib import Path
from veil.providers.common import client,Calls,save
from veil.providers.sam import segment
p=argparse.ArgumentParser();p.add_argument('--env-file',required=True);p.add_argument('--root',type=Path,required=True);a=p.parse_args()
root=a.root;c=client(a.env_file);ledger=Calls(root,max_calls=12)
finding=next(f for f in json.loads((root/'spark-original.json').read_text())['findings'] if f['category']=='license_plate')
x1,y1,x2,y2=finding['box'];x=round((x1+x2)/2);y=round((y1+y2)/2)
prompt=f'<20f>7<|point;x={x};y={y};w=960;h=540|>'
save(root/'plate-seed.json',{'source':'spark-original frame at 2000ms','prompt':prompt,'ground_truth_used':False})
f=None
try:
 with (root/'input.mp4').open('rb') as media:f=c.files.create(file=media,purpose='user_data',expires_after={'anchor':'created_at','seconds':3600})
 regions=segment(c,ledger,root,'sam-video-plate-seeded',prompt,file_id=f.id)
 print('Seeded SAM plate regions:',len(regions))
finally:
 if f:
  try:c.files.delete(f.id)
  except Exception:pass
