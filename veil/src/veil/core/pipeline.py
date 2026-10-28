"""Bounded real inference pipeline. No fixture labels or expected answers are read."""
from collections import defaultdict
import math
import os
from pathlib import Path
import re
import subprocess
import cv2
from veil.core.models import Timeline, VisualTrack, FrameRegion, AudioInterval
from veil.providers.common import Calls, client, save
from veil.providers.sam import segment
from veil.providers.vision import inspect_frames
from veil.providers.voice import transcribe
from veil.media.track import track_field
from veil.media.redact import render
from veil.media.inspect import decode_export
from veil.verification.ocr import inspect_text
from veil.verification.fusion import merge_ocr
from veil.media.sampling import periodic_frames
from veil.media.lifetimes import phone_tracklets


def speech_intervals(result, duration_ms):
    text = result.get('transcript', '')
    if not (re.search(r'\d[\d\s-]{5,}\d', text) or re.search(r'phone|telephone|contact number', text, re.I)):
        return []
    turns = result.get('turns') or []
    if turns:
        start = max(0, min(t['startMs'] for t in turns)-500)
        end = min(duration_ms, max(t['endMs'] for t in turns)+500)
        if start < end:
            return [AudioInterval(start_ms=start, end_ms=end)]
    return [AudioInterval(start_ms=0, end_ms=duration_ms)]


def extract_audio(source, target):
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(source),'-vn','-ac','1',
                    '-ar','24000','-c:a','pcm_s16le',str(target)],check=True,timeout=90)


def sample_frames(source, root, prefix, media):
    count = round(media['duration_ms']*media['fps']/1000)
    indices = sorted(set(min(count-1, max(0, round(count*f))) for f in (.11,.42,.89)))
    cap = cv2.VideoCapture(str(source))
    frames=[]
    try:
        for index in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES,index)
            ok, frame=cap.read()
            if not ok:raise ValueError('Cannot decode requested inspection frame')
            path=root/f'{prefix}-{index}.jpg'
            if not cv2.imwrite(str(path),frame):raise ValueError('Cannot save inspection frame')
            frames.append((round(index/media['fps']*1000),path))
    finally:cap.release()
    return frames


class MetaPipeline:
    def __init__(self, env_file, max_calls=12):
        if not 1<=max_calls<=12:raise ValueError('Call budget must be between 1 and 12')
        self.env_file=env_file
        self.max_calls=max_calls

    def context(self, root):
        return client(self.env_file),Calls(root,max_calls=self.max_calls)

    def detect(self, root, media, *, seed_omit_phone=False, face_action='cover'):
        c,ledger=self.context(root)
        source=root/'input.mp4'
        frames=sample_frames(source,root,'source',media)
        observed=inspect_frames(c,ledger,root,'source-observations',frames,media['width'],media['height'],exported=False)
        tracks=[];uploaded=None
        count=round(media['duration_ms']*media['fps']/1000)
        try:
            with source.open('rb') as stream:
                uploaded=c.files.create(file=stream,purpose='user_data',expires_after={'anchor':'created_at','seconds':3600})
            save(root/'cloud-upload.json',{'file_id':uploaded.id,'scope':'authorized source MP4 for SAM video tracking'})
            rows=segment(c,ledger,root,'face-tracking','human face',file_id=uploaded.id,frame_count=count)
            groups=defaultdict(list)
            for row in rows:groups[str(row['track_id'])].append(FrameRegion(frame=row['frame'],box=row['box']))
            for ident,regions in groups.items():
                tracks.append(VisualTrack(id=f'face-{ident}',category='face',source='sam-3.1',action=face_action,regions=regions))
            # One plate seed per sampled frame; choose first observed instance for this bounded prototype.
            plates=[(f,e) for f in observed.frames for e in f.exposures if e.category=='license_plate']
            if plates:
                f,e=plates[0];x1,y1,x2,y2=e.box
                index=round(f.time_ms*media['fps']/1000)
                prompt=f'<{index}f>7<|box;x1={math.floor(x1)};y1={math.floor(y1)};x2={math.ceil(x2)-1};y2={math.ceil(y2)-1};w={media["width"]};h={media["height"]}|>'
                rows=segment(c,ledger,root,'plate-tracking',prompt,file_id=uploaded.id,frame_count=count)
                if not rows:raise ValueError('Observed plate could not be tracked')
                regions=[FrameRegion(frame=r['frame'],box=r['box']) for r in rows]
                seed=next((r for r in regions if r.frame==index),None)
                field_area=(x2-x1)*(y2-y1)
                if seed is None or (seed.box[2]-seed.box[0])*(seed.box[3]-seed.box[1]) < field_area*.5:
                    # Segmentation may select a character. Keep the observed whole field too.
                    field_regions,uncertain=track_field(source,index,e.box)
                    tracks.append(VisualTrack(id='plate-whole-field',category='license_plate',
                        source='spark/opencv-whole-field-fallback',regions=field_regions))
                    save(root/'plate-field-fallback.json',{'reason':'SAM seed mask is smaller than half the observed sensitive field',
                         'uncertain_frames':uncertain,'threshold_is_heuristic':True})
                tracks.append(VisualTrack(id='plate-7',category='license_plate',source='sam-3.1/spark-seed',regions=regions))
        finally:
            if uploaded:
                try:
                    c.files.delete(uploaded.id);save(root/'cloud-cleanup.json',{'deleted':True})
                except Exception:
                    save(root/'cloud-cleanup.json',{'deleted':False,'expiry_requested_seconds':3600,'needs_attention':True})
        phones=[(f,e) for f in observed.frames for e in f.exposures if e.category=='phone_number']
        if not seed_omit_phone:
            try:
                phone_frames=periodic_frames(source,root,'source-phone-ocr',media)
                phone_ocr=inspect_text(phone_frames,media['width'],media['height'],
                                      Path(os.getenv('VEIL_OCR_CACHE','artifacts/private/ocr-cache')))
            except Exception as exc:
                phone_ocr={'status':'failed','error_type':type(exc).__name__,'findings':[]}
            save(root/'source-phone-ocr.json',phone_ocr)
            phone_tracks,diagnostics=phone_tracklets(phone_ocr['findings'],media)
            tracks.extend(phone_tracks)
            save(root/'phone-lifetimes.json',diagnostics)
            if not phone_tracks and phones:
                f,e=phones[0]
                regions,uncertain=track_field(source,round(f.time_ms*media['fps']/1000),e.box)
                tracks.append(VisualTrack(id='phone-field',category='phone_number',source='spark/opencv-field-fallback',regions=regions))
                save(root/'field-tracking.json',{'uncertain_frames':uncertain,'fallback':'full frame cover on tracking loss'})
        extract_audio(source,root/'source-audio.wav')
        voice=transcribe(c,ledger,root,'source-transcription',root/'source-audio.wav')
        timeline=Timeline(**{k:media[k] for k in ('duration_ms','fps','width','height')},visual_tracks=tracks,
                          audio_intervals=speech_intervals(voice,media['duration_ms']))
        save(root/'timeline.json',timeline.model_dump(mode='json'))
        save(root/'detection-scope.json',{'seeded_phone_omission':seed_omit_phone,
             'limitations':['3 source samples','one plate; up to 64 presence-bounded phone tracklets','no full-scene recall guarantee','no exact spoken-number guarantee']})
        return timeline

    def verify(self, root, media, revision, *, sparse_ocr=False):
        c,ledger=self.context(root)
        source=root/'export.mp4'
        prefix=f'audit-{revision}'
        # This adapter receives only the exported pixels/audio, never original findings or seeded-failure flags.
        frames=sample_frames(source,root,prefix,media)
        observations=inspect_frames(c,ledger,root,prefix,frames,media['width'],media['height'],exported=True)
        audio=root/f'{prefix}.wav';extract_audio(source,audio)
        voice=transcribe(c,ledger,root,f'{prefix}-voice',audio)
        try:
            ocr_frames=frames if sparse_ocr else periodic_frames(source,root,f'{prefix}-ocr',media)
            ocr=inspect_text(ocr_frames,media['width'],media['height'],
                             Path(os.getenv('VEIL_OCR_CACHE','artifacts/private/ocr-cache')))
        except Exception as exc:
            ocr={'status':'failed','error_type':type(exc).__name__,'findings':[]}
        save(root/f'{prefix}-ocr.json',ocr)
        report={'revision':revision,'frames':observations.model_dump(mode='json')['frames'],
                'spoken_phone_intervals':[i.model_dump(mode='json') for i in speech_intervals(voice,media['duration_ms'])],
                'transcript':voice['transcript'],'status':'residual_observed' if any(f.exposures for f in observations.frames) or speech_intervals(voice,media['duration_ms']) else 'no_exposure_observed_in_samples',
                'sample_times_ms':[t for t,_ in frames],'needs_human_review':True,
                'limitations':['3 sampled output frames; short exposures can be missed','same model family may share perception errors','speech recognition may miss or misread numbers','not a zero-leak guarantee']}
        report=merge_ocr(report,ocr)
        report['auditor_version']='sparse-spark_sparse-ocr-baseline' if sparse_ocr else 'sparse-spark_dense-ocr-v1'
        times=ocr.get('sample_times_ms',[])
        report['coverage']={'model_frames':len(frames),'local_ocr_frames':len(times),
             'max_local_ocr_gap_ms':max((b-a for a,b in zip(times,times[1:])),default=None),
             'requested_local_interval_ms':None if sparse_ocr else 250,'coverage_is_sampled':True}
        save(root/f'{prefix}-report.json',report)
        return report

    def repair(self, root, media, report):
        tracks=[]
        phone_observations=[{**e,'time_ms':frame['time_ms']} for frame in report['frames']
                            for e in frame['exposures'] if e['category']=='phone_number']
        phone_tracks,diagnostics=phone_tracklets(phone_observations,media)
        tracks.extend(phone_tracks)
        save(root/'repair-phone-lifetimes.json',diagnostics)
        unidentified=any(len(re.sub(r'\D','',o.get('text') or ''))<7 for o in phone_observations)
        for category, timestamp, box, fragments in repair_seeds(report):
            if category=='phone_number' and phone_tracks and not unidentified:continue
            regions,uncertain=track_field(root/'export.mp4',round(timestamp*media['fps']/1000),box)
            tracks.append(VisualTrack(id=f'repair-{category}',category=category,source='export-audit/opencv-whole-field-envelope',regions=regions))
            save(root/f'repair-{category}-tracking.json',{'uncertain_frames':uncertain,'observed_fragments':fragments,
                 'seed_box':box,'limitation':'non-phone fields or unidentified phones retain conservative full-clip fallback'})
        intervals=[AudioInterval.model_validate(i) for i in report['spoken_phone_intervals']]
        if not tracks and not intervals:raise ValueError('No observed residual exposure to repair')
        timeline=Timeline(**{k:media[k] for k in ('duration_ms','fps','width','height')},visual_tracks=tracks,audio_intervals=intervals)
        save(root/'repair-timeline.json',timeline.model_dump(mode='json'))
        render(root/'export.mp4',root/'repair.partial.mp4',timeline)
        decode_export(root/'repair.partial.mp4')
        return root/'repair.partial.mp4'


def repair_seeds(report):
    """Keep all fragments of each category in its earliest sampled frame."""
    used=set()
    for frame in sorted(report['frames'],key=lambda f:f['time_ms']):
        for category in ('face','license_plate','phone_number'):
            if category in used:continue
            matches=[f for f in frame['exposures'] if f['category']==category]
            if not matches:continue
            used.add(category)
            box=[min(f['box'][0] for f in matches),min(f['box'][1] for f in matches),
                 max(f['box'][2] for f in matches),max(f['box'][3] for f in matches)]
            yield category,frame['time_ms'],box,len(matches)
