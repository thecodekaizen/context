"""Bounded video sampling schedules, independent of detections and answer keys."""
import math
from pathlib import Path
import cv2


def periodic_indices(frame_count, fps, interval_ms=250, max_samples=512):
    if frame_count <= 0 or not math.isfinite(fps) or fps <= 0 or interval_ms <= 0:
        raise ValueError('Invalid video sampling parameters')
    stride=max(1,math.floor(fps*interval_ms/1000))
    indices=sorted(set([*range(0,frame_count,stride),frame_count-1]))
    if len(indices)>max_samples:
        raise ValueError('Dense audit would exceed its local frame budget')
    return indices


def periodic_frames(source: Path, root: Path, prefix: str, media, interval_ms=250):
    count=round(media['duration_ms']*media['fps']/1000)
    indices=periodic_indices(count,media['fps'],interval_ms)
    cap=cv2.VideoCapture(str(source))
    result=[]
    try:
        for index in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES,index)
            ok,frame=cap.read()
            if not ok:raise ValueError('Cannot decode dense inspection frame')
            path=root/f'{prefix}-{index}.jpg'
            if not cv2.imwrite(str(path),frame):raise ValueError('Cannot save dense inspection frame')
            result.append((round(index/media['fps']*1000),path))
    finally:
        cap.release()
    return result
