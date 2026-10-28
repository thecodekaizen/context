"""Validate actual media, without claiming privacy verification."""
import json
import subprocess
from fractions import Fraction
from pathlib import Path
import cv2
import numpy as np


def inspect_media(path: Path) -> dict:
    try:
        probe = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-show_streams', '-show_format',
            '-of', 'json', str(path)], stderr=subprocess.PIPE, timeout=20))
        video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        fps = float(Fraction(video['avg_frame_rate']))
        nominal = float(Fraction(video['r_frame_rate']))
        duration = float(video.get('duration', probe['format']['duration']))
    except (subprocess.SubprocessError, KeyError, ValueError, StopIteration, ZeroDivisionError) as exc:
        raise ValueError('Cannot read a valid video stream') from exc
    if not 0 < duration <= 60 or not 0 < fps <= 60:
        raise ValueError('Local prototype accepts videos up to 60 seconds and 60 fps')
    if abs(fps - nominal) > .001:
        raise ValueError('Variable-frame-rate input is unsupported; normalize it first')
    if video['width'] * video['height'] > 1920 * 1080:
        raise ValueError('Local prototype accepts at most 1080p')
    return {'width': video['width'], 'height': video['height'], 'fps': fps,
            'duration_ms': round(duration * 1000),
            'has_audio': any(s['codec_type'] == 'audio' for s in probe['streams']),
            'container_duration_s': float(probe['format']['duration'])}


def decode_export(path: Path) -> dict:
    metadata = inspect_media(path)
    cap = cv2.VideoCapture(str(path))
    count = 0
    near_black=[]
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if float(np.mean(np.max(frame,axis=2)<40)) > .95:
            near_black.append(count)
        count += 1
    cap.release()
    if count == 0 or abs(count / metadata['fps'] * 1000 - metadata['duration_ms']) > 150:
        raise ValueError('Export decoding is incomplete')
    return {**metadata, 'decoded_frames': count, 'privacy_verification': 'not_run',
            'near_full_frame_black_frames':near_black,
            'utility_status':'excessive_masking' if len(near_black)>count*.1 else 'review_required',
            'needs_human_review': True}
