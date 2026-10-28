import json
import os
import shutil
import threading
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool
from .alignment import analyze
from .fixtures import generate
from .context_pack import build_pack
from .meta import interpret
import httpx

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
app=FastAPI(title='CONTEXT',version='0.1.0')
lock=threading.Lock()

def investigation(directory):
    result=analyze(directory/'original.mp4',directory/'edited.mp4')
    result['id']=directory.name
    result['media']={k:f'/api/media/{directory.name}/{v}.mp4' for k,v in [('source','original'),('edited','edited')]}
    (directory/'evidence.json').write_text(json.dumps(result,indent=2))
    return result

@app.get('/api/health')
def health():
    return {'status':'ok','meta_configured':bool(os.getenv('MODEL_API_KEY'))}

@app.post('/api/analyze')
async def upload(original:UploadFile=File(...),edited:UploadFile=File(...)):
    if not lock.acquire(blocking=False):
        raise HTTPException(429,'An analysis is already running. Try again shortly.')
    directory=DATA/uuid4().hex; directory.mkdir()
    try:
        for name,file in [('original',original),('edited',edited)]:
            size=0
            with (directory/f'{name}.mp4').open('wb') as out:
                while block:=await file.read(1024*1024):
                    size+=len(block)
                    if size>200*1024*1024:
                        raise HTTPException(413,'Each video must be under 200 MB')
                    out.write(block)
        return await run_in_threadpool(investigation,directory)
    except ValueError as exc:
        shutil.rmtree(directory,ignore_errors=True)
        raise HTTPException(422,str(exc)) from exc
    except Exception:
        shutil.rmtree(directory,ignore_errors=True)
        raise
    finally:
        lock.release()

@app.post('/api/demo')
async def demo():
    if not lock.acquire(blocking=False):
        raise HTTPException(429,'An analysis is already running')
    try:
        directory=DATA/'demo';
        if not (directory/'omission.mp4').exists():
            await run_in_threadpool(generate,directory)
        shutil.copyfile(directory/'omission.mp4',directory/'edited.mp4')
        return await run_in_threadpool(investigation,directory)
    finally:
        lock.release()

@app.get('/api/media/{identifier}/{filename}')
def media(identifier:str,filename:str):
    if not (identifier=='demo' or len(identifier)==32 and all(c in '0123456789abcdef' for c in identifier)) or filename not in {'original.mp4','edited.mp4','evidence.json'}:
        raise HTTPException(404)
    path=DATA/identifier/filename
    if not path.is_file(): raise HTTPException(404)
    return FileResponse(path)

@app.post('/api/investigations/{identifier}/interpret/{finding_id}')
async def review(identifier:str,finding_id:str):
    if not (identifier=='demo' or len(identifier)==32 and all(c in '0123456789abcdef' for c in identifier)):
        raise HTTPException(404)
    directory=DATA/identifier
    if not (directory/'evidence.json').is_file():
        raise HTTPException(404,'Investigation does not exist')
    if not os.getenv('MODEL_API_KEY'):
        raise HTTPException(503,'Meta analysis unavailable: configure MODEL_API_KEY in the server environment.')
    if not lock.acquire(blocking=False):
        raise HTTPException(429,'An analysis is already running')
    try:
        evidence=json.loads((directory/'evidence.json').read_text())
        clips=await run_in_threadpool(build_pack,directory,evidence,finding_id)
        result=await interpret(evidence,finding_id,clips)
        # Save separately so model statements never become deterministic findings.
        target=directory/f'interpretation-{finding_id}.json'
        temporary=target.with_suffix('.tmp')
        temporary.write_text(json.dumps(result,indent=2))
        temporary.replace(target)
        return result
    except ValueError as exc:
        raise HTTPException(422,str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(502,'Meta request failed. Check account access and server configuration; measured evidence is unchanged.') from exc
    finally:
        lock.release()

if (ROOT/'web/dist').exists():
    app.mount('/',StaticFiles(directory=ROOT/'web/dist',html=True),name='web')
