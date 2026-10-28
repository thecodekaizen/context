"""Independent local text signal on exported pixels; macOS Vision adapter."""
import json
import platform
import re
import shutil
import subprocess
from pathlib import Path


def inspect_text(frames, width, height, cache):
    if platform.system() != 'Darwin' or not shutil.which('swiftc'):
        return {'status':'unavailable','reason':'macOS Vision/Swift compiler unavailable','findings':[]}
    cache.mkdir(parents=True, exist_ok=True)
    binary=cache/'veil-local-ocr'
    source=Path(__file__).with_name('ocr.swift')
    if not binary.exists() or binary.stat().st_mtime < source.stat().st_mtime:
        subprocess.run(['swiftc',str(source),'-o',str(binary)],check=True,timeout=90,capture_output=True)
    result=json.loads(subprocess.check_output([str(binary),*[str(p) for _,p in frames]],timeout=90))
    times={path.name:time for time,path in frames}
    findings=[]
    for frame in result:
        for row in frame['rows']:
            text=row['text']
            # Generic number patterns, not fixture-specific identifiers.
            if re.search(r'(?<!\d)(?:\+?\d[\d ()-]{6,}\d)(?!\d)',text):
                x1,y1,x2,y2=row['box']
                findings.append({'category':'phone_number','time_ms':times[frame['file']],
                    'box':[x1*width,y1*height,x2*width,y2*height],
                    'text':text,'reason':'Local OCR found a phone-like digit sequence in actual exported pixels',
                    'source':'macos-vision-ocr'})
    return {'status':'completed','sample_times_ms':[t for t,_ in frames],
            'findings':findings,'limitations':['phone-like patterns only; false positives possible','sampled frames only','macOS-specific local adapter']}
