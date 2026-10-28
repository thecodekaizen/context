"""One real Meta pipeline run; retain legacy repair from identical audit evidence."""
import json,time,shutil,argparse
from pathlib import Path
from veil import VeilClient
from benchmark_support import archive_local_evidence
from veil.core.models import Timeline,VisualTrack
from veil.core.pipeline import repair_seeds
from veil.media.track import track_field
from veil.media.redact import render
from veil.media.inspect import decode_export

parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path('artifacts/public-footage-001'))
base=parser.parse_args().root
root=base/'run'
if root.exists():raise SystemExit('Run exists; no automatic rerun')
root.mkdir()
started=time.monotonic()
with VeilClient(base_url='http://127.0.0.1:8019') as c:
 job=c.create_job(base/'challenge.mp4')
 (root/'job-id.txt').write_text(job['id']+'\n')
 c.cloud_action(job['id'],'detect',seed_omit_phone=True)
 c.process(job['id'])
 c.download(job['id'],root/'initial-export.mp4')
 job=c.cloud_action(job['id'],'verify')
 report=c.verification(job['id'])
 (root/'initial-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Initial audit',report['status'],flush=True)
 tracks=[]
 for category,ms,box,fragments in repair_seeds(report):
  regions,uncertain=track_field(root/'initial-export.mp4',round(ms*job['media']['fps']/1000),box)
  tracks.append(VisualTrack(id=f'legacy-{category}',category=category,source='legacy-full-clip-flow',regions=regions))
  (root/f'legacy-{category}-diagnostic.json').write_text(json.dumps({'uncertain_frames':uncertain},indent=2)+'\n')
 old=Timeline(**{k:job['media'][k] for k in ('width','height','fps','duration_ms')},visual_tracks=tracks,audio_intervals=[])
 render(root/'initial-export.mp4',root/'legacy-repair.mp4',old)
 (root/'legacy-timeline.json').write_text(old.model_dump_json(indent=2)+'\n')
 if job['verification']=='residual_observed':
  c.cloud_action(job['id'],'repair')
  job=c.cloud_action(job['id'],'verify')
 c.download(job['id'],root/'final-export.mp4')
 audit=c.verification(job['id']);receipt=c.receipt(job['id'])
 for name,data in [('final-audit.json',audit),('receipt.json',receipt)]:
  (root/name).write_text(json.dumps(data,indent=2)+'\n')
 archive_local_evidence(job['id'],root/'provider-evidence')
 result={'job':job,'latency_s':time.monotonic()-started,'estimated_usd':receipt['estimated_api_cost_usd'],
         'final_audit':audit['status'],'legacy_utility':decode_export(root/'legacy-repair.mp4'),
         'new_utility':decode_export(root/'final-export.mp4'),'real_public_background':True,'synthetic_privacy_targets':True}
 (root/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2),flush=True)
