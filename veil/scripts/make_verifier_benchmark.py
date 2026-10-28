"""Create synthetic candidate exports; answer keys never enter inference directories."""
import json,math,subprocess
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path('artifacts/verifier-benchmark-001')
FPS,W,H,DURATION=12,960,540,8
FONT='/System/Library/Fonts/Menlo.ttc'

def command(args):subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
def font(size):return ImageFont.truetype(FONT,size)

def main():
 if ROOT.exists():raise SystemExit('Fixture root exists; refusing to replace frozen cases')
 ROOT.mkdir(parents=True)
 portrait=Image.open('artifacts/smoke-001/fictional-face.png').convert('RGB').resize((180,210))
 annotation=ROOT/'evaluation-only';annotation.mkdir()
 truths={}
 for ident,kind in [('clip-a','persistent'),('clip-b','brief'),('clip-c','negative')]:
  folder=ROOT/ident;folder.mkdir()
  writer=cv2.VideoWriter(str(folder/'video-only.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),FPS,(W,H))
  for index in range(FPS*DURATION):
   t=index/FPS;pan=round(14*math.sin(t/1.7))
   image=Image.new('RGB',(W,H),(228,222,206));draw=ImageDraw.Draw(image)
   draw.rectangle((0,340,W,H),fill=(133,149,141))
   draw.text((28,24),'WORKSHOP / DEMONSTRATION',font=font(24),fill=(30,40,45))
   draw.rounded_rectangle((45,95,360,290),radius=8,fill=(196,171,131),outline=(80,75,65),width=3)
   draw.text((70,125),'Batch 246',font=font(28),fill=(35,45,45))
   draw.text((70,175),'TOOLS',font=font(30),fill=(35,45,45))
   draw.ellipse((785,305,905,355),fill=(76,105,66))
   draw.rectangle((823,330,868,424),fill=(145,91,54))
   if kind=='persistent':
    image.paste(portrait,(700+pan,90))
    draw=ImageDraw.Draw(image)
    cx=55+pan;cy=278
    draw.rounded_rectangle((cx,cy,cx+490,cy+155),radius=30,fill=(60,101,132),outline=(25,40,50),width=3)
    for wx in (cx+80,cx+400):draw.ellipse((wx-30,cy+124,wx+30,cy+184),fill=(20,25,30))
    plate=(cx+145,cy+62,cx+365,cy+119)
    draw.rectangle(plate,fill=(250,250,238),outline=(25,25,25),width=3)
    draw.text((plate[0]+10,plate[1]+10),'TEST 0287',font=font(29),fill=(12,12,12))
    if 4.2<=t<4.6:draw.rectangle((plate[0]+140,plate[1]-5,plate[2]+5,plate[3]+5),fill=(120,130,130))
   if kind=='persistent' or (kind=='brief' and 24<=index<27):
    px=410+pan;py=462 if kind=='persistent' else 390
    draw.rectangle((px,py,px+390,py+65),fill=(255,254,240),outline=(60,70,70),width=2)
    draw.text((px+16,py+14),'202-555-0189',font=font(36),fill=(12,14,14))
   writer.write(cv2.cvtColor(np.array(image),cv2.COLOR_RGB2BGR))
  writer.release()
  if kind=='persistent':
   command(['ffmpeg','-y','-i','artifacts/smoke-001/speech.wav','-af','adelay=1000,apad','-t','8','-ac','1','-ar','24000',str(folder/'audio.wav')])
  else:
   command(['ffmpeg','-y','-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t','8',str(folder/'audio.wav')])
  command(['ffmpeg','-y','-i',str(folder/'video-only.mp4'),'-i',str(folder/'audio.wav'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-t','8','-map_metadata','-1','-movflags','+faststart',str(folder/'export.mp4')])
  events=[]
  if kind=='persistent':
   events=[{'category':c,'start_ms':0,'end_ms':8000} for c in ('face','license_plate','phone_number')]
   events.append({'category':'spoken_phone','start_ms':1000,'end_ms':7371})
  elif kind=='brief':events=[{'category':'phone_number','start_ms':2000,'end_ms':2250}]
  truths[ident]={'kind':kind,'events':events,'synthetic_only':True,'fps':12,'frames':96,'duration_ms':8000}
 (annotation/'truth.json').write_text(json.dumps(truths,indent=2)+'\n')
 print('Created three frozen candidate exports; keys are evaluation-only.')
if __name__=='__main__':main()
