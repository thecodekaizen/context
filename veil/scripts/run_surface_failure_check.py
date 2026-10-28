"""Adversarial diagnostic on the EXISTING development clip; not a new benchmark case.

Intentionally valid but wrong quads test whether geometry validity can stand in
for privacy. Original identifiers are supplied only to exported-pixel OCR.
"""
import argparse
from pathlib import Path
import sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_surface_demo import frame_audit
from veil.core.models import Timeline
from veil.media.surface import SurfaceReplacement
from veil.media.redact import render
from veil.media.inspect import decode_export
from veil.providers.common import save

p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--ocr-cache',type=Path,required=True);a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=False);started=time.monotonic()
t=Timeline.model_validate_json((a.root/'timeline.json').read_text())
plan=SurfaceReplacement.model_validate_json((a.root/'surface-plan.json').read_text())
plan.asset_path=str((a.root/'replacement.png').resolve())
# Explicit fault injection. Enlarged fixture support boxes allow a mathematically
# valid wrong quad: containment is not a semantic localization guarantee.
for region in t.visual_tracks[0].regions:
    x1,y1,x2,y2=region.box;region.box=(x1,y1,min(t.width,x2+115),y2)
for frame in plan.frames:
    frame.corners=[(x+110,y) for x,y in frame.corners]
plan.geometry_source='deliberately shifted fixture quads; invalid localization, valid homographies'
bad_render=render(a.root/'original.mp4',a.output/'rejected-candidate.mp4',t,natural_replacements=[plan])
bad_audit=frame_audit(a.output/'rejected-candidate.mp4',a.output,'candidate-frames',a.ocr_cache)
save(a.output/'candidate-render.json',bad_render)
status='diagnostic_failed_to_detect_seeded_leak'
final_audit=None
if bad_audit['status']=='residual_observed':
    # Targeted conservative response: the sole affected track switches to cover.
    # This diagnostic uses the source and existing protective regions, not truth
    # decoded by a model or an invented corrected quad.
    fallback=render(a.root/'original.mp4',a.output/'fallback.mp4',t)
    final_audit=frame_audit(a.output/'fallback.mp4',a.output,'fallback-frames',a.ocr_cache)
    save(a.output/'fallback-render.json',fallback)
    status='candidate_rejected_fallback_requires_visual_review' if final_audit['status']=='no_original_identifier_observed_in_checked_frames' else 'fallback_not_cleared'
result={'status':status,'seeded_fault':'110-pixel horizontal geometry displacement; support boxes expanded for diagnostic',
    'candidate':{'media':decode_export(a.output/'rejected-candidate.mp4'),'audit':bad_audit},
    'fallback_audit':final_audit,'elapsed_s':time.monotonic()-started,'api_calls':0,'api_cost_usd':0,
    'scope':'one intentional fault on existing development footage, not held-out evidence or six-case result',
    'needs_human_visual_review':True,'ordinary_API_natural_strategy':'not_integrated',
    'conclusion':'Valid homographies do not prove privacy; inspect actual exported media and retain rejected candidates.'}
save(a.output/'results.json',result)
print({'status':status,'candidate_residual_observations':len(bad_audit['residual_findings']),'fallback_status':final_audit['status'] if final_audit else None})
