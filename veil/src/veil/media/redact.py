"""Render actual video using half-open per-frame boxes and conservative covers."""
from pathlib import Path
import math,subprocess
import cv2
from veil.core.models import Timeline


def covered_bounds(box,width,height,padding=12):
 x1,y1,x2,y2=box
 return max(0,math.floor(x1)-padding),max(0,math.floor(y1)-padding),min(width,math.ceil(x2)+padding),min(height,math.ceil(y2)+padding)

def render(source:Path,target:Path,timeline:Timeline,padding=12):
 cap=cv2.VideoCapture(str(source));fps=cap.get(cv2.CAP_PROP_FPS)
 width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
 if not cap.isOpened() or (width,height)!=(timeline.width,timeline.height) or abs(fps-timeline.fps)>1e-5:raise ValueError('Media geometry does not match timeline')
 frame_count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));by_frame={}
 for track in timeline.visual_tracks:
  for region in track.regions:
   if region.frame>=frame_count:raise ValueError('Region outside source video')
   by_frame.setdefault(region.frame,[]).append(region.box)
 intermediate=target.with_name(target.stem+'-silent.mp4')
 writer=cv2.VideoWriter(str(intermediate),cv2.VideoWriter_fourcc(*'mp4v'),fps,(width,height))
 if not writer.isOpened():raise ValueError('Cannot open video writer')
 count=0
 try:
  while True:
   ok,frame=cap.read()
   if not ok:break
   for box in by_frame.get(count,[]):
    x1,y1,x2,y2=covered_bounds(box,width,height,padding)
    frame[y1:y2,x1:x2]=0
   writer.write(frame);count+=1
 finally:writer.release();cap.release()
 if count!=frame_count:raise ValueError('Source decoding stopped early')
 filters=[f"volume=0:enable='between(t,{i.start_ms/1000:.3f},{i.end_ms/1000:.3f})'" for i in timeline.audio_intervals]
 args=['ffmpeg','-y','-i',str(intermediate),'-i',str(source),'-map','0:v:0','-map','1:a:0',
       '-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart','-map_metadata','-1']
 if filters:args+=['-af',','.join(filters)]
 subprocess.run(args+[str(target)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 return {'frames_rendered':count,'frames_with_visual_cover':len(by_frame),'audio_intervals':len(filters)}
