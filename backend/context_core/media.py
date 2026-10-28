"""Bounded FFmpeg operations; timestamps are seconds relative to decoded start."""
import hashlib
import json
import subprocess
from pathlib import Path
import numpy as np

RATE = 4
MAX_DURATION = 600

def run(args, timeout=120):
    try:
        return subprocess.run(args, check=True, capture_output=True, timeout=timeout).stdout
    except subprocess.CalledProcessError as exc:
        raise ValueError('Media decoding failed: ' + exc.stderr.decode(errors='replace')[-500:]) from exc
    except subprocess.TimeoutExpired as exc:
        raise ValueError('Media processing timed out') from exc

def probe(path):
    raw = json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))
    stream = next((s for s in raw['streams'] if s['codec_type'] == 'video'), None)
    if not stream:
        raise ValueError('A video stream is required')
    duration = float(raw['format'].get('duration', stream.get('duration', 0)))
    if not 0 < duration <= MAX_DURATION:
        raise ValueError(f'Video must be between 0 and {MAX_DURATION} seconds')
    return dict(duration=duration, width=stream['width'], height=stream['height'], codec=stream['codec_name'], has_audio=any(s['codec_type']=='audio' for s in raw['streams']))

def fingerprints(path):
    # Area reduction suppresses compression noise; retain color and spatial layout.
    raw = run(['ffmpeg','-v','error','-i',str(path),'-an','-vf',f'fps={RATE},scale=24:16:flags=area','-pix_fmt','rgb24','-f','rawvideo','pipe:1'])
    frames = np.frombuffer(raw, dtype=np.uint8).reshape(-1,16*24*3).astype(np.float32)/255
    if not len(frames):
        raise ValueError('No decodable frames')
    return np.arange(len(frames))/RATE, frames

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()
