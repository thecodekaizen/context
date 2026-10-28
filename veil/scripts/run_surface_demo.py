"""Milestone-one synthetic rendering experiment, not a tracking benchmark.

Every corner and fallback box is explicitly fixture-authored. No model inference.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
import cv2
import numpy as np
from PIL import Image, ImageDraw
from veil.core.models import Timeline, VisualTrack, FrameRegion
from veil.media.redact import render
from veil.media.surface import SurfaceReplacement
from veil.media.inspect import decode_export
from veil.verification.original_text import audit_original_text
from veil.providers.common import save

WIDTH,HEIGHT,FPS,COUNT=640,360,12,72
IDENTIFIER='2025550146'


def texture(text):
    image=np.full((84,280,3),(220,226,230),np.uint8)
    cv2.rectangle(image,(2,2),(277,81),(65,65,65),2)
    size=cv2.getTextSize(text,cv2.FONT_HERSHEY_SIMPLEX,1.15,2)[0]
    cv2.putText(image,text,((280-size[0])//2,53),cv2.FONT_HERSHEY_SIMPLEX,1.15,(25,25,25),2,cv2.LINE_AA)
    return image


def prepare(root):
    if root.exists():raise ValueError('Choose a fresh experiment directory')
    root.mkdir(parents=True)
    rng=np.random.default_rng(14)
    background=np.clip(rng.normal(110,4,(HEIGHT,WIDTH,3)),0,255).astype(np.uint8)
    original=texture(IDENTIFIER);replacement=texture('DEMO')
    cv2.imwrite(str(root/'replacement.png'),replacement)
    writer=cv2.VideoWriter(str(root/'source-silent.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),FPS,(WIDTH,HEIGHT))
    if not writer.isOpened():raise ValueError('Writer unavailable')
    geometry=[];regions=[];truth=[]
    src=np.float32([[0,0],[279,0],[279,83],[0,83]])
    for i in range(COUNT):
        t=i/FPS
        image=np.roll(background,round(8*math.sin(t)),axis=1).copy()
        # Deliberately simple generated vehicle context, not filmed road footage.
        cv2.rectangle(image,(85,80),(555,300),(155,148,140),-1)
        cv2.rectangle(image,(140,95),(500,155),(65,65,65),-1)
        cv2.circle(image,(140,290),28,(35,35,35),-1);cv2.circle(image,(500,290),28,(35,35,35),-1)
        x=160+36*math.sin(t*.8);y=190+10*math.cos(t)
        q=np.float32([[x,y],[x+276-15*math.sin(t),y+8*math.sin(t)],
                      [x+268,y+82],[x+6,y+79]])
        matrix=cv2.getPerspectiveTransform(src,q)
        warped=cv2.warpPerspective(original,matrix,(WIDTH,HEIGHT),borderMode=cv2.BORDER_REPLICATE)
        mask=np.zeros((HEIGHT,WIDTH),np.uint8);cv2.fillConvexPoly(mask,np.rint(q).astype(np.int32),255)
        image[mask>0]=warped[mask>0]
        cv2.putText(image,'SYNTHETIC / FIXTURE GEOMETRY',(14,25),cv2.FONT_HERSHEY_SIMPLEX,.5,(240,240,240),1,cv2.LINE_AA)
        writer.write(image)
        box=[float(q[:,0].min()-3),float(q[:,1].min()-3),float(q[:,0].max()+3),float(q[:,1].max()+3)]
        regions.append(FrameRegion(frame=i,box=box));geometry.append({'frame':i,'corners':q.tolist(),'status':'visible'})
        truth.append({'frame':i,'corners':q.tolist()})
    writer.release()
    subprocess.run(['ffmpeg','-y','-i',str(root/'source-silent.mp4'),'-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t','6','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(root/'original.mp4')],check=True,capture_output=True)
    timeline=Timeline(duration_ms=6000,fps=FPS,width=WIDTH,height=HEIGHT,
        visual_tracks=[VisualTrack(id='plate-001',category='license_plate',source='fixture-authored geometry, not model detection',regions=regions)],audio_intervals=[])
    plan=SurfaceReplacement(track_id='plate-001',asset_path=str((root/'replacement.png').resolve()),
        geometry_source='fixture-authored quadrilaterals, no automatic tracking',frames=geometry)
    save(root/'timeline.json',timeline.model_dump(mode='json'));save(root/'surface-plan.json',plan.model_dump(mode='json'))
    save(root/'evaluation-only.json',{'original_identifier':IDENTIFIER,'frames':truth})
    save(root/'manifest.json',{'scope':'One synthetic development clip; known corners supplied. No tracking, SAM or natural-scene validation.',
        'source_sha256':hashlib.sha256((root/'original.mp4').read_bytes()).hexdigest(),
        'api_calls':0,'api_cost_usd':0,'manual_initializations':'Fixture-author defines the generating trajectory; all per-frame geometry supplied',
        'replacement_asset_generated_once':True,'human_preference':'not_run'})
    return timeline,plan


def frame_audit(video,root,prefix,cache):
    directory=root/prefix;directory.mkdir()
    cap=cv2.VideoCapture(str(video));frames=[];index=0
    while True:
        ok,image=cap.read()
        if not ok:break
        path=directory/f'{index:04}.png';cv2.imwrite(str(path),image)
        frames.append((round(index/FPS*1000),path));index+=1
    cap.release()
    report,ocr=audit_original_text(video,frames,[IDENTIFIER],WIDTH,HEIGHT,cache)
    save(root/f'{prefix}-ocr.json',ocr)
    save(root/f'{prefix}-audit.json',report)
    return report


def quality(root):
    a=cv2.VideoCapture(str(root/'original.mp4'));b=cv2.VideoCapture(str(root/'natural.mp4'))
    truth=json.loads((root/'evaluation-only.json').read_text())['frames'];outside=[];areas=[];decoded=0;black=[]
    samples={0,24,48,71};review=Image.new('RGB',(WIDTH*3,HEIGHT*4));draw=ImageDraw.Draw(review)
    baseline=cv2.VideoCapture(str(root/'opaque.mp4'))
    for item in truth:
        ok,source=a.read();valid,result=b.read();baseok,opaque=baseline.read()
        if not(ok and valid and baseok):raise ValueError('Video decode truncated')
        mask=np.zeros((HEIGHT,WIDTH),np.uint8);cv2.fillConvexPoly(mask,np.rint(item['corners']).astype(np.int32),255)
        outer=cv2.dilate(mask,np.ones((3,3),np.uint8));areas.append(float((outer>0).mean()))
        # Wider tolerance band isolates unaffected scene from codec edge ringing.
        unrelated=cv2.dilate(mask,np.ones((33,33),np.uint8))==0
        outside.append(float(np.abs(source.astype(float)-result)[unrelated].mean()))
        if float((result.max(axis=2)<40).mean())>.95:black.append(item['frame'])
        if item['frame'] in samples:
            row=sorted(samples).index(item['frame'])
            for col,(name,image) in enumerate([('Original',source),('Opaque',opaque),('Replacement',result)]):
                review.paste(Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB)),(WIDTH*col,HEIGHT*row))
                draw.text((WIDTH*col+10,HEIGHT*row+35),f'{name}: frame {item["frame"]}',fill='white')
        decoded+=1
    a.release();b.release();baseline.release();review.save(root/'comparison.jpg')
    result={'frames_checked':decoded,'mean_outside_region_absolute_pixel_difference_0_255':float(np.mean(outside)),
        'maximum_frame_mean_outside_difference':max(outside),'mean_edited_frame_fraction':float(np.mean(areas)),
        'near_full_frame_blackouts':black,'geometry_stability':'not independently measured: supplied fixture corners',
        'visual_naturalness':'human review required','temporal_flicker':'not independently measured',
        'limitations':['Codec re-encoding changes pixels outside edit region','Same synthetic development fixture is not independent validation','No occlusion, reflective surface or automatic tracking evaluated']}
    save(root/'quality.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--ocr-cache',type=Path,required=True);args=p.parse_args()
    started=time.monotonic();timeline,plan=prepare(args.root)
    baseline=render(args.root/'original.mp4',args.root/'opaque.mp4',timeline)
    natural=render(args.root/'original.mp4',args.root/'natural.mp4',timeline,natural_replacements=[plan])
    save(args.root/'render-decisions.json',{'baseline':baseline,'natural':natural})
    # Test fail-closed behavior at actual video level, using the same source and track.
    bad=plan.model_copy(deep=True);bad.frames=[g for g in bad.frames if g.frame not in (24,25)]
    fallback=render(args.root/'original.mp4',args.root/'fallback.mp4',timeline,natural_replacements=[bad])
    save(args.root/'fallback-decisions.json',fallback)
    inspections={name:decode_export(args.root/f'{name}.mp4') for name in ('original','opaque','natural','fallback')}
    reports={name:frame_audit(args.root/f'{name}.mp4',args.root,f'{name}-frames',args.ocr_cache) for name in ('original','opaque','natural','fallback')}
    q=quality(args.root)
    save(args.root/'results.json',{'media':inspections,'privacy':reports,'quality':q,'elapsed_s':time.monotonic()-started,
        'api_calls':0,'api_cost_usd':0,'acceptance':'pending manual frame/video inspection and independent tracking tests',
        'six_clip_gate':'not_run','blinded_preference':'not_run'})
