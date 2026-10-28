"""Evaluation only: fixture truth never enters inference or rendering."""
import argparse
import json
import subprocess
import wave
from pathlib import Path
import cv2
import numpy as np
from veil.providers.common import save

p = argparse.ArgumentParser()
p.add_argument('--root', type=Path, required=True)
p.add_argument('--video', default='protected.mp4')
a = p.parse_args()
root = a.root
truth = json.loads((root / 'ground-truth.json').read_text())
cap = cv2.VideoCapture(str(root / a.video))
full, visible, phone = [], [], []
while True:
    ok, frame = cap.read()
    if not ok:
        break
    entry = truth['frames'][len(full)]
    x1,y1,x2,y2 = entry['plate']
    full.append(float(np.mean(np.max(frame[y1:y2,x1:x2], axis=2) < 40)))
    if entry['partial_occlusion']:
        x2 = x1 + 110  # Fixture's known occluder boundary, evaluation only.
    visible.append(float(np.mean(np.max(frame[y1:y2,x1:x2], axis=2) < 40)))
    px,py,_,_ = entry['printed_phone']
    # Printed digits only; card heading and background are not sensitive data.
    phone.append(float(np.mean(np.max(frame[py+35:py+65,px+10:px+270],axis=2) < 40)))
cap.release()
audio_path = root / 'protected-audio.wav'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(root/a.video),'-vn','-ac','1','-ar','24000','-c:a','pcm_s16le',str(audio_path)],check=True)
with wave.open(str(audio_path)) as audio:
    rate=audio.getframerate()
    samples=np.frombuffer(audio.readframes(audio.getnframes()),dtype='<i2').astype(float)/32768
speech=samples[truth['speech_start_ms']*rate//1000:truth['speech_end_ms']*rate//1000]
def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
original, output = probe(root/'input.mp4'), probe(root/a.video)
result={
 'video':a.video,'decoded_video_frames':len(full),'expected_video_frames':len(truth['frames']),
 'plate_full_rectangle_black_fraction_min':min(full),
 'plate_visible_rectangle_black_fraction_min':min(visible),
 'plate_visible_frames_below_99pct_cover':[i for i,v in enumerate(visible) if v<.99],
 'printed_digits_rectangle_black_fraction_min':min(phone),
 'muted_speech_rms':float(np.sqrt(np.mean(speech**2))),
 'muted_speech_max_absolute_sample':float(np.max(np.abs(speech))),
 'source_container_duration_s':float(original['format']['duration']),
 'output_container_duration_s':float(output['format']['duration']),
 'output_codecs':[s['codec_name'] for s in output['streams']],
 'evaluation_only':True,
 'limitations':['One composited synthetic fixture, not a real-camera benchmark.',
 'Black-pixel coverage is a mask coverage check, not proof of unreadability or absence of other leaks.',
 'Occluded plate region is excluded only in visible-region metric; full rectangle metric is retained.',
 'Face source-panel bounds are not pixel-accurate facial ground truth.']}
save(root/'protected-media-checks.json',result)
print(json.dumps(result,indent=2))
