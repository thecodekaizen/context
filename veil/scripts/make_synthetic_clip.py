"""Deterministic composited motion fixture; truth is evaluation-only."""
import argparse,json,math,subprocess
from pathlib import Path
import cv2
from PIL import Image,ImageDraw,ImageFont

W,H,FPS,DURATION=960,540,10,18
FONT='/System/Library/Fonts/Menlo.ttc'

def run(*args):subprocess.run(list(args),check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
def font(size):return ImageFont.truetype(FONT,size)

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=a.output
 if not (root/'fictional-face.png').exists():raise ValueError('Generate fictional fixture face first')
 face=Image.open(root/'fictional-face.png').convert('RGB').resize((230,270))
 writer=cv2.VideoWriter(str(root/'silent.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),FPS,(W,H));truth=[]
 for index in range(FPS*DURATION):
  t=index/FPS;pan=round(18*math.sin(t/2.8));fy=50+round(6*math.sin(t/2));fx=75+pan
  image=Image.new('RGB',(W,H),(214,224,232));d=ImageDraw.Draw(image)
  d.rectangle((0,350,W,H),fill=(177,189,193));d.line((0,350,W,350),fill=(100,120,130),width=3)
  d.text((20,12),'VEIL / SYNTHETIC PRIVACY FIXTURE',font=font(18),fill=(25,40,55))
  image.paste(face,(fx,fy));d=ImageDraw.Draw(image)
  cx=465+pan+round(24*math.sin(t/3));cy=115
  d.rounded_rectangle((cx,cy,cx+410,cy+180),radius=35,fill=(54,91,127),outline=(30,40,60),width=3)
  d.polygon([(cx+90,cy),(cx+140,cy-55),(cx+285,cy-55),(cx+335,cy)],fill=(80,140,180))
  for x in (cx+78,cx+327):d.ellipse((x-32,cy+148,x+32,cy+212),fill=(30,30,35))
  plate=(cx+95,cy+100,cx+325,cy+160)
  d.rounded_rectangle(plate,radius=5,fill=(250,250,235),outline=(25,25,30),width=4)
  d.text((plate[0]+11,plate[1]+10),'TEST 0146',font=font(31),fill=(12,15,15))
  phone=(50+pan,412,470+pan,487)
  d.rectangle(phone,fill=(255,255,244),outline=(80,90,90),width=2)
  d.text((phone[0]+10,phone[1]+3),'DEMO CONTACT',font=font(16),fill=(60,70,75))
  d.text((phone[0]+10,phone[1]+28),'202-555-0146',font=font(36),fill=(10,10,10))
  occlusion=7.0<=t<8.2
  if occlusion:
   # Occluder crosses one side of face and the right side of plate.
   d.rectangle((fx+125,fy,fx+245,fy+280),fill=(110,120,125))
   d.rectangle((plate[0]+110,plate[1]-8,plate[2]+15,plate[3]+8),fill=(110,120,125))
  writer.write(cv2.cvtColor(__import__('numpy').array(image),cv2.COLOR_RGB2BGR))
  truth.append({'frame':index,'time_ms':round(t*1000),'face_source_panel':[fx,fy,fx+230,fy+270],
                'plate':list(plate),'printed_phone':list(phone),'partial_occlusion':occlusion})
 writer.release()
 text='The demonstration phone number is two zero two, five five five, zero one four six.'
 run('say','-v','Samantha','-r','145','-o',str(root/'speech.aiff'),text)
 run('ffmpeg','-y','-i',str(root/'speech.aiff'),'-ac','1','-ar','24000','-c:a','pcm_s16le',str(root/'speech.wav'))
 speech_seconds=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(root/'speech.wav')]))
 run('ffmpeg','-y','-i',str(root/'speech.wav'),'-af','adelay=3000,apad','-t',str(DURATION),'-ar','24000','-ac','1',str(root/'audio.wav'))
 run('ffmpeg','-y','-i',str(root/'silent.mp4'),'-i',str(root/'audio.wav'),'-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart','-map_metadata','-1','-t',str(DURATION),str(root/'input.mp4'))
 (root/'ground-truth.json').write_text(json.dumps({'synthetic':True,'duration_ms':DURATION*1000,'fps':FPS,
  'face_truth_note':'Rendered source-panel bounds, not pixel-exact facial segmentation ground truth',
  'fake_plate':'TEST 0146','fake_phone':'202-555-0146','speech_start_ms':3000,'speech_end_ms':round((3+speech_seconds)*1000),
  'frames':truth},indent=2)+'\n')
 cap=cv2.VideoCapture(str(root/'input.mp4'));cap.set(cv2.CAP_PROP_POS_MSEC,2000);ok,frame=cap.read();cap.release()
 if not ok:raise ValueError('Fixture cannot be decoded')
 cv2.imwrite(str(root/'sample.jpg'),frame)
 print('Created 18-second input.mp4 with 180 frames and synthetic audio')
if __name__=='__main__':main()
