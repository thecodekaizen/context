"""All-frame evaluation only; answer keys never enter the engine or verifier."""
import json,wave,subprocess,argparse
from pathlib import Path
import cv2,numpy as np

parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path('artifacts/public-footage-001'))
root=parser.parse_args().root;run=root/'run'
truth=json.loads((root/'evaluation-only/truth.json').read_text())
results={}
paths={'legacy-repair':run/'legacy-repair.mp4','final-export':run/'final-export.mp4'}
normal=root/'normal-run/final-export.mp4'
if normal.exists():paths['normal-export']=normal
for name,video_path in paths.items():
 cap=cv2.VideoCapture(str(video_path));coverage=[];blackouts=[];index=0
 while True:
  ok,frame=cap.read()
  if not ok:break
  if float(np.mean(np.max(frame,axis=2)<40))>.95:blackouts.append(index)
  for exposure in truth['frames'][index]['phone_regions']:
   x1,y1,x2,y2=exposure['box'];region=frame[y1:y2,x1:x2]
   coverage.append({'frame':index,'event':exposure['synthetic_value'],
                    'black_fraction':float(np.mean(np.max(region,axis=2)<40))})
  index+=1
 cap.release()
 audio=run/(name+'.wav')
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(video_path),'-vn','-ac','1','-ar','24000',str(audio)],check=True)
 with wave.open(str(audio)) as source:
  rate=source.getframerate();samples=np.frombuffer(source.readframes(source.getnframes()),dtype='<i2').astype(float)/32768
 speech=samples[truth['speech_interval_ms'][0]*rate//1000:truth['speech_interval_ms'][1]*rate//1000]
 by_event={}
 for item in coverage:by_event.setdefault(item['event'],[]).append(item['black_fraction'])
 results[name]={'decoded_frames':index,'phone_visible_frames':len(coverage),
   'min_phone_rectangle_cover_fraction':min(c['black_fraction'] for c in coverage),
   'events':{key:{'frames':len(values),'min_black_fraction':min(values)} for key,values in by_event.items()},
   'phone_frames_below_99pct_cover':[c['frame'] for c in coverage if c['black_fraction']<.99],
   'near_full_frame_blackouts':blackouts,'near_full_frame_blackout_count':len(blackouts),
   'speech_rms':float(np.sqrt(np.mean(speech**2))),'speech_max_abs':float(np.max(np.abs(speech)))}
# Plan collateral is a diagnostic, not independent output verification.
for name,timeline_path in [('legacy-repair',run/'legacy-timeline.json'),('final-export',run/'provider-evidence/repair-timeline.json'),('normal-export',root/'normal-run/provider-evidence/timeline.json')]:
 if not timeline_path.exists():continue
 timeline=json.loads(timeline_path.read_text());outside=0;total=0
 active={f['frame'] for f in truth['frames'] if f['phone_regions']}
 for track in timeline['visual_tracks']:
  if track['category']!='phone_number':continue
  for region in track['regions']:
   x1,y1,x2,y2=region['box'];area=(x2-x1)*(y2-y1);total+=area
   if region['frame'] not in active:outside+=area
 results[name]['plan_area_outside_phone_presence_fraction']=outside/total if total else None
report={'comparisons':results,'evaluation_only':True,'ground_truth_used_in_inference':False,
 'limitations':['one real-camera background with synthetic targets','phone rectangles only, not face identity accuracy',
 'black-pixel coverage does not prove zero residual information','planned mask-area diagnostic can double-count overlapping tracks',
 'targeted development case, not held-out or real-person benchmark']}
(root/'evaluation-only/results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
