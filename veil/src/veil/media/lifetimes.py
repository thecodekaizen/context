"""Presence-bounded phone fields derived only from timestamped observations."""
from bisect import bisect_right
import math,re
import numpy as np
from veil.core.models import FrameRegion,VisualTrack


def phone_tracklets(observations,media,*,margin_ms=250,max_gap_ms=500,max_tracks=64):
    if margin_ms<0 or max_gap_ms<=0:raise ValueError('Invalid lifetime bounds')
    prepared=[]
    for observation in observations:
        if observation.get('category')!='phone_number':continue
        identity=re.sub(r'\D','',observation.get('text') or '')
        if len(identity)<7:continue
        region=FrameRegion(frame=0,box=observation['box'])
        timestamp=observation['time_ms']
        if not 0<=timestamp<media['duration_ms']:raise ValueError('Observation outside video')
        prepared.append({**observation,'identity':identity,'box':list(region.box)})
    # Prefer field-level OCR geometry over duplicate Spark boxes for the same identifier.
    ocr_ids={o['identity'] for o in prepared if o.get('source')=='macos-vision-ocr'}
    prepared=[o for o in prepared if o['identity'] not in ocr_ids or o.get('source')=='macos-vision-ocr']
    tracks=[];diagonal=math.hypot(media['width'],media['height'])
    for observation in sorted(prepared,key=lambda o:o['time_ms']):
        candidates=[]
        center=np.array(observation['box'][:2])+np.array(observation['box'][2:])
        center=center/2
        for track in tracks:
            previous=track[-1];dt=observation['time_ms']-previous['time_ms']
            if previous['identity']!=observation['identity'] or not 0<dt<=max_gap_ms:continue
            old=(np.array(previous['box'][:2])+np.array(previous['box'][2:]))/2
            distance=float(np.linalg.norm(center-old))
            # Broad image-plane gate; heuristic, not a calibrated physical speed limit.
            if distance<=diagonal*(.15+.5*dt/1000):candidates.append((distance,track))
        if candidates:min(candidates,key=lambda c:c[0])[1].append(observation)
        else:
            tracks.append([observation])
            if len(tracks)>max_tracks:raise ValueError('Phone tracklet budget exceeded')
    result=[];diagnostics=[]
    count=round(media['duration_ms']*media['fps']/1000)
    for ident,observed in enumerate(tracks):
        times=[o['time_ms'] for o in observed];boxes=np.array([o['box'] for o in observed],dtype=float)
        velocity=np.zeros(4)
        if len(times)>1:
            velocity=np.median(np.diff(boxes,axis=0)/(np.diff(times)[:,None]/1000),axis=0)
        start=max(0,times[0]-margin_ms);end=min(media['duration_ms'],times[-1]+margin_ms)
        regions=[]
        for frame in range(count):
            timestamp=frame/media['fps']*1000
            if not start<=timestamp<=end:continue
            right=bisect_right(times,timestamp)
            if right==0:
                projected=boxes[0]+velocity*(timestamp-times[0])/1000
                pair=np.array([boxes[0],projected])
            elif right==len(times):
                projected=boxes[-1]+velocity*(timestamp-times[-1])/1000
                pair=np.array([boxes[-1],projected])
            else:pair=boxes[[right-1,right]]
            # Conservative envelope of adjacent measured/projected boxes, never GT coordinates.
            box=[max(0,float(pair[:,0].min())),max(0,float(pair[:,1].min())),
                 min(media['width'],float(pair[:,2].max())),min(media['height'],float(pair[:,3].max()))]
            if box[2]<=box[0] or box[3]<=box[1]:raise ValueError('Predicted field left image bounds')
            regions.append(FrameRegion(frame=frame,box=box))
        result.append(VisualTrack(id=f'phone-observed-{ident}',category='phone_number',
                      source='ocr/temporal-observation-envelope',regions=regions))
        diagnostics.append({'track_id':result[-1].id,'observations':len(observed),
            'observed_start_ms':times[0],'observed_end_ms':times[-1],
            'planned_start_ms':start,'planned_end_ms':end,'velocity_box_pixels_per_second':velocity.tolist()})
    return result,{'tracks':diagnostics,'margin_ms':margin_ms,'max_gap_ms':max_gap_ms,
        'limitations':['constant-velocity extrapolation only within bounded observation margins',
        'unsampled faster motion or shorter appearances may escape detection','numeric OCR identity can be wrong',
        'spatial association gate is heuristic; no general multi-object guarantee']}
