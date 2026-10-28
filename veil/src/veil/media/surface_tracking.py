"""One manually initialized planar surface, LK flow + RANSAC; no label access.

Stops on lost correspondence. Does not infer re-entry or hidden geometry.
"""
from pathlib import Path
import cv2
import numpy as np
from veil.media.surface import SurfaceFrame, perspective


def track_surface(source: Path, initial_corners, *, start_frame=0):
    cap=cv2.VideoCapture(str(source))
    if not cap.isOpened():raise ValueError('Cannot open source video')
    count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if not 0 <= start_frame < count:
        cap.release();raise ValueError('Initialization outside video')
    try:
        perspective(initial_corners,(100,40),(width,height))
        cap.set(cv2.CAP_PROP_POS_FRAMES,start_frame);ok,previous=cap.read()
        if not ok:raise ValueError('Cannot decode initialization')
        previous=cv2.cvtColor(previous,cv2.COLOR_BGR2GRAY)
        quad=np.float32(initial_corners)
        mask=np.zeros_like(previous);cv2.fillConvexPoly(mask,np.rint(quad).astype(np.int32),255)
        # Erode borders to favor points on the same plane, not background.
        mask=cv2.erode(mask,np.ones((5,5),np.uint8))
        points=cv2.goodFeaturesToTrack(previous,maxCorners=120,qualityLevel=.01,minDistance=4,mask=mask)
        frames=[SurfaceFrame(frame=start_frame,corners=quad.tolist())]
        diagnostics=[{'frame':start_frame,'status':'manually_initialized','features':0 if points is None else len(points)}]
        lost=points is None or len(points)<8
        for index in range(start_frame+1,count):
            ok,image=cap.read()
            if not ok:raise ValueError('Video stopped before declared frame count')
            gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            reason=None;stats={}
            if lost:
                reason='Tracking lost; explicit reinitialization required'
            else:
                forward,valid,_=cv2.calcOpticalFlowPyrLK(previous,gray,points,None,winSize=(21,21),maxLevel=3)
                if forward is None:
                    reason='Optical flow returned no correspondences'
                else:
                    backward,back_valid,_=cv2.calcOpticalFlowPyrLK(gray,previous,forward,None,winSize=(21,21),maxLevel=3)
                    if backward is None:
                        reason='Backward optical flow unavailable'
                    else:
                        fb=np.linalg.norm(backward-points,axis=2).ravel()
                        selected=(valid.ravel()>0)&(back_valid.ravel()>0)&np.isfinite(fb)&(fb<=1.5)
                        before=points[selected].reshape(-1,2);after=forward[selected].reshape(-1,2)
                        stats={'consistent_features':len(before)}
                        if len(before)<8:
                            reason='Fewer than eight consistent plane features'
                        else:
                            matrix,inliers=cv2.findHomography(before,after,cv2.RANSAC,1.5)
                            ratio=0 if inliers is None else float(inliers.mean())
                            stats['ransac_inlier_fraction']=ratio
                            if matrix is None or ratio<.7 or int(inliers.sum())<6:
                                reason='Insufficient homography inliers'
                            else:
                                candidate=cv2.perspectiveTransform(quad[None],matrix)[0]
                                try:perspective(candidate,(100,40),(width,height))
                                except ValueError as exc:reason=str(exc)
                                if reason is None:
                                    shift=float(np.max(np.linalg.norm(candidate-quad,axis=1)))
                                    stats['maximum_corner_displacement_px']=shift
                                    if shift>max(width,height)*.08:
                                        reason='Implausibly large per-frame corner displacement'
                                if reason is None:
                                    quad=candidate;points=after[inliers.ravel()>0].reshape(-1,1,2)
            if reason:
                lost=True
                frames.append(SurfaceFrame(frame=index,status='uncertain'))
                diagnostics.append({'frame':index,'status':'uncertain','reason':reason,**stats})
            else:
                frames.append(SurfaceFrame(frame=index,corners=quad.tolist()))
                diagnostics.append({'frame':index,'status':'tracked',**stats})
            previous=gray
        return frames,{'initialization':'one manually selected source-frame quadrilateral',
            'method':'pyramidal LK forward/backward consistency and RANSAC homography',
            'thresholds_are_heuristics':True,'frames':diagnostics,
            'limitations':['No automatic surface localization','No full-occlusion or re-entry recovery',
                'Inliers are not a calibrated confidence or proof of correct surface identity',
                'No temporal smoothing is applied; drift remains possible']}
    finally:cap.release()
