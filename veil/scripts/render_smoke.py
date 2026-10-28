"""Assemble observed model results only; do not load the fixture answer key."""
import argparse,json,re,hashlib
from collections import defaultdict
from pathlib import Path
from veil.core.models import Timeline,VisualTrack,FrameRegion,AudioInterval
from veil.media.redact import render
from veil.providers.common import save

p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();root=a.root
tracks=[]
for category,name in [('face','sam-video-face'),('license_plate','sam-video-plate-seeded')]:
 payload=json.loads((root/f'{name}.json').read_text());groups=defaultdict(list)
 for r in payload['regions']:groups[r['track_id']].append(FrameRegion(frame=r['frame'],box=r['box'],confidence=r['confidence']))
 for ident,regions in groups.items():tracks.append(VisualTrack(id=f'{category}-{ident}',category=category,source='sam-3.1'+('/spark-point-seed' if category=='license_plate' else ''),regions=regions))
voice=json.loads((root/'voice-original.json').read_text());intervals=[]
if re.search(r'\d[\d\s-]{5,}\d',voice['transcript']) or re.search(r'phone|telephone|contact number',voice['transcript'],re.I):
 turns=voice.get('turns') or []
 if turns:
  # Conservative complete detected speech envelope; no claim of word alignment.
  intervals=[AudioInterval(start_ms=max(0,min(t['startMs'] for t in turns)-500),end_ms=min(18000,max(t['endMs'] for t in turns)+500))]
 else:intervals=[AudioInterval(start_ms=0,end_ms=18000)]
timeline=Timeline(duration_ms=18000,fps=10,width=960,height=540,visual_tracks=tracks,audio_intervals=intervals)
save(root/'timeline.json',timeline.model_dump(mode='json'))
result=render(root/'input.mp4',root/'redacted.mp4',timeline)
save(root/'render-result.json',{**result,'input_sha256':hashlib.sha256((root/'input.mp4').read_bytes()).hexdigest(),
 'output_sha256':hashlib.sha256((root/'redacted.mp4').read_bytes()).hexdigest(),
 'scope':'Face and plate covers plus conservative speech muting; printed phone not yet protected',
 'safety_claim':'No guarantee of zero residual exposures'})
print(result)
