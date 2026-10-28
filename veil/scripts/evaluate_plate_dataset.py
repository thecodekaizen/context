"""Bounded, image-only external synthetic plate benchmark; never a video recall claim."""
import argparse, hashlib, json, zipfile
from pathlib import Path
import cv2
import numpy as np
from veil.providers.common import Calls, client, save
from veil.providers.vision import inspect_frames


def prepare(archive, root):
    if root.exists(): raise ValueError('Choose a fresh benchmark directory')
    checksum=hashlib.md5(archive.read_bytes()).hexdigest()
    if checksum != '1c4a9db36e5f0a662ca7a5a0fcb513dc': raise ValueError('Dataset checksum mismatch')
    root.mkdir(parents=True)
    truth=[]
    with zipfile.ZipFile(archive) as z:
        candidates=sorted(n for n in z.namelist() if n.lower().endswith(('.png','.jpg','.jpeg')) and '/test/' in '/'+n.lower())
        if len(candidates)<6: raise ValueError('Test split not found')
        # Frozen selection before inference; no selecting based on model success.
        for i in range(6):
            name=candidates[i*len(candidates)//6]
            plate=cv2.imdecode(np.frombuffer(z.read(name),np.uint8),cv2.IMREAD_COLOR)
            if plate is None: raise ValueError('Invalid image')
            w=[193,145,96,193,145,96][i]; h=round(plate.shape[0]*w/plate.shape[1])
            x,y=[(80,120),(340,180),(220,100),(300,90),(100,220),(430,210)][i]
            canvas=np.full((360,640,3),72,np.uint8)
            cv2.rectangle(canvas,(40,60),(600,300),(115,110,100),-1)
            canvas[y:y+h,x:x+w]=cv2.resize(plate,(w,h))
            path=root/f'sample-{i}.jpg';cv2.imwrite(str(path),canvas)
            truth.append({'sample':i,'source_member':name,'box':[x,y,x+w,y+h], 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    save(root/'evaluation-only.json',truth)
    save(root/'manifest.json',{'dataset':'https://zenodo.org/records/13342103','license':'CC BY 4.0','archive_md5':checksum,'samples':[{k:r[k] for k in ('sample','sha256')} for r in truth], 'scope':'Six frozen synthetic test-split plate crops composited on simple vehicle-like canvases; image detection only. No natural video tracking claim.', 'max_calls':4})


def run(root, env):
    manifest=json.loads((root/'manifest.json').read_text())
    for row in manifest['samples']:
        if hashlib.sha256((root/f'sample-{row["sample"]}.jpg').read_bytes()).hexdigest()!=row['sha256']: raise ValueError('Changed fixture')
    ledger=Calls(root,4); api=client(env); results=[]
    # No truth file, original filenames or source labels enter requests.
    for start in (0,3):
        frames=[(i*1000,root/f'sample-{i}.jpg') for i in range(start,start+3)]
        observations=inspect_frames(api,ledger,root,f'detect-{start}',frames,640,360,exported=False)
        for frame in observations.frames:
            image=cv2.imread(str(root/f'sample-{frame.time_ms//1000}.jpg'))
            mask=np.zeros((360,640),np.uint8)
            for e in frame.exposures:
                if e.category!='license_plate':continue
                x1,y1,x2,y2=e.box
                mask[max(0,int(y1)-4):min(360,int(np.ceil(y2))+4),max(0,int(x1)-4):min(640,int(np.ceil(x2))+4)]=255
            image[mask>0]=0
            cv2.imwrite(str(root/f'redacted-{frame.time_ms//1000}.jpg'),image)
            cv2.imwrite(str(root/f'mask-{frame.time_ms//1000}.png'),mask)
        inspect_frames(api,ledger,root,f'verify-{start}',[(i*1000,root/f'redacted-{i}.jpg') for i in range(start,start+3)],640,360,exported=True)
    # Evaluation happens only after all inference has completed.
    for r in json.loads((root/'evaluation-only.json').read_text()):
        mask=cv2.imread(str(root/f'mask-{r["sample"]}.png'),0)>0
        x1,y1,x2,y2=r['box'];gt=np.zeros_like(mask);gt[y1:y2,x1:x2]=True
        results.append({'sample':r['sample'],'plate_pixel_coverage':float((mask&gt).sum()/gt.sum()),'unnecessary_mask_fraction_of_frame':float((mask&~gt).sum()/mask.size),'masked_frame_fraction':float(mask.mean())})
    save(root/'results.json',{'samples':results,'fully_covered':sum(r['plate_pixel_coverage']==1 for r in results),'sample_size':len(results),'estimated_usd':sum(r.get('estimated_usd',0) for r in ledger.read()),'limitations':['six synthetic still-image composites, no natural video/temporal recall','same-model review can share detection errors','no tuning or retries on this sample']})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','run']);p.add_argument('--root',type=Path,required=True);p.add_argument('--archive',type=Path);p.add_argument('--env-file',type=Path);a=p.parse_args()
    if a.mode=='prepare':prepare(a.archive,a.root)
    else:run(a.root,a.env_file)
