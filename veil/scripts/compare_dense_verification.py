"""Local-only comparison: reuse baseline output, add bounded OCR, never call Meta."""
import json,time,argparse
from pathlib import Path
from veil.media.inspect import inspect_media
from veil.media.sampling import periodic_frames
from veil.verification.ocr import inspect_text

parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path('artifacts/verifier-benchmark-001'))
root=parser.parse_args().root
results=[]
for name in ('clip-a','clip-b','clip-c'):
 folder=root/name
 started=time.monotonic()
 media=inspect_media(folder/'export.mp4')
 frames=periodic_frames(folder/'export.mp4',folder,'dense-local',media)
 report=inspect_text(frames,media['width'],media['height'],Path('artifacts/private/ocr-cache'))
 (folder/'dense-ocr.json').write_text(json.dumps(report,indent=2)+'\n')
 results.append({'id':name,'status':report['status'],'frames_sampled':len(frames),
                 'local_latency_s':time.monotonic()-started,'cloud_calls':0,'findings':len(report['findings'])})
 (root/'dense-results.json').write_text(json.dumps(results,indent=2)+'\n')
 print(results[-1],flush=True)
