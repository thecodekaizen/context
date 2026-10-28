"""Real public camera background plus declared synthetic privacy overlays."""
import json,math,subprocess,hashlib,argparse
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path('artifacts/public-footage-001')
FONT='/System/Library/Fonts/Menlo.ttc'

def main():
 global ROOT
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT);ROOT=parser.parse_args().root
 target=ROOT/'challenge.mp4'
 if target.exists():raise SystemExit('Refusing to overwrite frozen challenge')
 cap=cv2.VideoCapture(str(ROOT/'background.mp4'))
 writer=cv2.VideoWriter(str(ROOT/'challenge-silent.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),12,(360,640))
 portrait=Image.open('artifacts/smoke-001/fictional-face.png').convert('RGB').resize((88,104))
 truth=[];index=0
 while True:
  ok,frame=cap.read()
  if not ok:break
  image=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB));draw=ImageDraw.Draw(image)
  draw.rectangle((0,0,360,32),fill=(15,25,35))
  draw.text((8,8),'VEIL / SYNTHETIC TEST OVERLAYS',font=ImageFont.truetype(FONT,12),fill=(240,245,250))
  face_x=246+round(4*math.sin(index/12));face_y=352
  image.paste(portrait,(face_x,face_y))
  exposures=[]
  if 15<=index<54:
   text='202-555-0189';x=36+round(18*math.sin(index/11));y=135+round(index*.9)
  elif 75<=index<78:
   text='202-555-0128';x=42;y=500
  else:text=None
  if text:
   draw=ImageDraw.Draw(image)
   draw.rounded_rectangle((x,y,x+282,y+52),radius=4,fill=(255,253,239),outline=(30,45,55),width=2)
   f=ImageFont.truetype(FONT,27);position=(x+15,y+10)
   draw.text(position,text,font=f,fill=(8,12,15))
   box=draw.textbbox(position,text,font=f)
   exposures.append({'category':'phone_number','box':list(box),'synthetic_value':text})
  writer.write(cv2.cvtColor(np.array(image),cv2.COLOR_RGB2BGR))
  truth.append({'frame':index,'time_ms':round(index*1000/12),'phone_regions':exposures,
                'face_source_panel':[face_x,face_y,face_x+88,face_y+104]})
  index+=1
 cap.release();writer.release()
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'challenge-silent.mp4'),'-i','artifacts/smoke-001/speech.wav',
  '-filter_complex','[1:a]adelay=1000,apad[a]','-map','0:v:0','-map','[a]','-t','8','-c:v','libx264','-crf','18',
  '-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart','-map_metadata','-1',str(target)],check=True)
 evaluation=ROOT/'evaluation-only';evaluation.mkdir(exist_ok=True)
 (evaluation/'truth.json').write_text(json.dumps({'fps':12,'duration_ms':8000,'frames':truth,
  'speech_interval_ms':[1000,7371],'face_metric':'source panel is not facial segmentation truth'},indent=2)+'\n')
 (ROOT/'challenge-provenance.json').write_text(json.dumps({'background':'source-provenance.json','hybrid':True,
  'not_real_person_data':True,'privacy_targets':'fictional generated portrait and fake visual/spoken phone numbers',
  'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'frames':index,
  'limitation':'real public camera background with synthetic exposures, not a real-person privacy benchmark'},indent=2)+'\n')
 print('Created frozen public-camera hybrid:',index,'frames')
if __name__=='__main__':main()
