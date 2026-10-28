"""Generated moving scenes; edits are produced independently of inference."""
from pathlib import Path
from .media import run

def generate(directory):
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=True)
    original=directory/'original.mp4'
    run(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc2=size=480x270:rate=24:duration=12','-c:v','libx264','-crf','18',str(original)])
    recipes={'copy':[(0,12)],'trim':[(2,10)],'omission':[(0,4),(8,12)],'reorder':[(8,12),(0,4),(4,8)],'repeat':[(0,4),(0,4),(8,12)],'recompressed':[(0,12)]}
    for name,parts in recipes.items():
        filters=';'.join(f'[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{i}]' for i,(a,b) in enumerate(parts))
        filters+=';' + ''.join(f'[v{i}]' for i in range(len(parts)))+f'concat=n={len(parts)}:v=1:a=0,scale=320:180[out]'
        run(['ffmpeg','-v','error','-y','-i',str(original),'-filter_complex',filters,'-map','[out]','-c:v','libx264','-crf','30',str(directory/f'{name}.mp4')])
    run(['ffmpeg','-v','error','-y','-f','lavfi','-i','smptebars=size=320x180:rate=24:duration=5','-c:v','libx264',str(directory/'unknown.mp4')])
    return directory

if __name__=='__main__':
    import sys
    generate(sys.argv[1] if len(sys.argv)>1 else 'data/demo')
