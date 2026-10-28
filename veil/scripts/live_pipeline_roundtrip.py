"""Bounded live run on approved synthetic clip; intentionally omit one phone cover."""
import json
from pathlib import Path
from veil import VeilClient
from veil.media.inspect import decode_export

root=Path('artifacts/live-pipeline-003')
if root.exists():raise SystemExit('Run already exists; refusing automatic rerun')
root.mkdir()
with VeilClient(base_url='http://127.0.0.1:8019') as client:
    job=client.create_job('artifacts/smoke-001/input.mp4')
    (root/'job-id.txt').write_text(job['id']+'\n')
    job=client.cloud_action(job['id'],'detect',seed_omit_phone=True)
    print('Detection:',job['status'],flush=True)
    client.process(job['id'])
    client.download(job['id'],root/'initial-export.mp4')
    job=client.cloud_action(job['id'],'verify')
    initial=client.verification(job['id'])
    print('Initial audit:',job['verification'],flush=True)
    (root/'initial-audit.json').write_text(json.dumps(initial,indent=2)+'\n')
    if job['verification']=='residual_observed':
        client.cloud_action(job['id'],'repair')
        job=client.cloud_action(job['id'],'verify')
    client.download(job['id'],root/'final-export.mp4')
    final=client.verification(job['id'])
    receipt=client.receipt(job['id'])
    (root/'final-audit.json').write_text(json.dumps(final,indent=2)+'\n')
    (root/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    report={'job':job,'initial_audit':initial['status'],'final_audit':final['status'],
            'media':decode_export(root/'final-export.mp4'),'real_api_calls':True,
            'estimated_usd':receipt.get('estimated_api_cost_usd'),'seeded_failure':True}
    (root/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)
