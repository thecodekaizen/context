"""Track a complete sensitive field, not a single segmented character."""
import cv2,numpy as np
from veil.core.models import FrameRegion


def track_field(source,seed_frame,box):
 cap=cv2.VideoCapture(str(source));frames=[]
 while True:
  ok,frame=cap.read()
  if not ok:break
  frames.append(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY))
 cap.release()
 if not frames or not 0<=seed_frame<len(frames):raise ValueError('Invalid seed frame')
 h,w=frames[0].shape
 def features(gray,b):
  mask=np.zeros_like(gray);x1,y1,x2,y2=np.rint(b).astype(int)
  mask[max(0,y1):min(h,y2),max(0,x1):min(w,x2)]=255
  return cv2.goodFeaturesToTrack(gray,maxCorners=100,qualityLevel=.01,minDistance=4,mask=mask)
 result={seed_frame:list(box)};uncertain=[]
 for direction in (1,-1):
  b=np.asarray(box,dtype=float);previous=frames[seed_frame];points=features(previous,b)
  indices=range(seed_frame+direction,len(frames),direction) if direction==1 else range(seed_frame-1,-1,-1)
  for index in indices:
   current=frames[index]
   if points is None or len(points)<4:
    uncertain.append(index);result[index]=[0,0,w,h]
    # Fail closed for this direction; do not invent locations after tracking loss.
    for remaining in range(index+direction,len(frames),direction) if direction==1 else range(index-1,-1,-1):
     uncertain.append(remaining);result[remaining]=[0,0,w,h]
    break
   following,status,error=cv2.calcOpticalFlowPyrLK(previous,current,points,None)
   if following is None:
    points=None;uncertain.append(index);result[index]=[0,0,w,h];previous=current;continue
   valid=status.ravel()==1
   if valid.sum()<4:points=None;uncertain.append(index);result[index]=[0,0,w,h];previous=current;continue
   delta=np.median(following[valid]-points[valid],axis=0).ravel()
   b+=np.array([delta[0],delta[1],delta[0],delta[1]])
   b[[0,2]]=np.clip(b[[0,2]],0,w);b[[1,3]]=np.clip(b[[1,3]],0,h)
   result[index]=b.tolist();previous=current;points=following[valid].reshape(-1,1,2)
 return [FrameRegion(frame=i,box=result.get(i,[0,0,w,h])) for i in range(len(frames))],sorted(set(uncertain))
