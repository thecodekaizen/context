"""Track the existing development fixture from one initial quad; no model calls."""
from pathlib import Path
import argparse
import sys,json,time
import numpy as np
sys.path.insert(0,'scripts')
from run_surface_demo import frame_audit
from veil.core.models import Timeline
from veil.media.surface import SurfaceReplacement
from veil.media.surface_tracking import track_surface
from veil.media.redact import render
from veil.media.inspect import decode_export
from veil.providers.common import save
parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args()
r=args.root;out=r/'tracked';out.mkdir(exist_ok=False)
p=SurfaceReplacement.model_validate_json((r/'surface-plan.json').read_text())
t=Timeline.model_validate_json((r/'timeline.json').read_text());start=time.monotonic()
# Only initialization is passed; remaining fixture corners never enter tracking.
frames,diagnostics=track_surface(r/'original.mp4',p.frames[0].corners)
p.frames=frames;p.geometry_source='one manually initialized quad + local LK/RANSAC; fallback boxes remain fixture authored'
p.asset_path=str((r/'replacement.png').resolve())
report=render(r/'original.mp4',out/'natural-tracked.mp4',t,natural_replacements=[p])
audit=frame_audit(out/'natural-tracked.mp4',out,'export-frames',Path('artifacts/private/ocr-cache'))
# Ground truth only now used for scoring, after inference/tracking and export.
truth=json.loads((r/'evaluation-only.json').read_text())['frames']
errors=[float(np.linalg.norm(np.asarray(f.corners)-np.asarray(g['corners']),axis=1).mean()) for f,g in zip(frames,truth) if f.corners is not None]
save(out/'geometry.json',[f.model_dump(mode='json') for f in frames]);save(out/'tracking.json',diagnostics)
save(out/'render.json',report)
save(out/'results.json',{'media':decode_export(out/'natural-tracked.mp4'),'privacy':audit,
    'mean_corner_error_px':float(np.mean(errors)), 'maximum_frame_mean_corner_error_px':max(errors),
    'natural_frames':report['natural_replacement']['natural_frames'],'fallback_frames':report['natural_replacement']['fallback_frames'],
    'elapsed_s':time.monotonic()-start,'api_calls':0,'api_cost_usd':0,
    'scope':'same synthetic development clip, one source-frame initialization; protective fallback boxes still fixture-authored, not model-detected',
    'manual_preference':'not_run'})
print(json.dumps({'natural_frames':report['natural_replacement']['natural_frames'],'fallback_frames':report['natural_replacement']['fallback_frames'],'mean_corner_error_px':float(np.mean(errors)),'audit_status':audit['status']}))
