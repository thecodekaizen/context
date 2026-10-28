"""Loopback-only reference API; no cloud transfers occur on these routes."""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from veil.core.jobs import JobStore, Conflict
from veil.core.models import Timeline


def create_app(root: Path | None = None):
    app = FastAPI(title='VEIL', version='0.2.0', description='Local reviewed-timeline rendering. Automatic detection and privacy audit are not yet exposed.')
    store = JobStore(root or Path(os.getenv('VEIL_JOBS_DIR', 'artifacts/private/jobs')))
    app.state.store = store

    @app.exception_handler(FileNotFoundError)
    async def missing(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=404, content={'detail': 'Unknown job or artifact'})

    @app.exception_handler(Conflict)
    async def conflict(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=409, content={'detail': str(exc)})

    @app.post('/v1/jobs', status_code=201)
    def create_job(video: UploadFile):
        try:
            return store.create(video.file)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        finally:
            video.file.close()

    @app.get('/v1/jobs/{job_id}')
    def get_job(job_id: str):
        return store.get(job_id)

    @app.post('/v1/jobs/{job_id}/redact')
    def redact_job(job_id: str, timeline: Timeline):
        try:
            return store.redact(job_id, timeline)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.get('/v1/jobs/{job_id}/findings')
    def findings(job_id: str):
        import json
        directory = store.directory(job_id)
        path = directory / 'timeline.json'
        return {'detection': 'not_run', 'source': 'client_supplied_reviewed_timeline',
                'timeline': json.loads(path.read_text()) if path.exists() else None}

    @app.get('/v1/jobs/{job_id}/receipt')
    def receipt(job_id: str):
        import json
        directory = store.directory(job_id)
        if store.get(job_id)['status'] != 'rendered':
            raise Conflict('Export is not ready')
        return json.loads((directory / 'receipt.json').read_text())

    @app.get('/v1/jobs/{job_id}/export')
    def export(job_id: str):
        directory = store.directory(job_id)
        if store.get(job_id)['status'] != 'rendered':
            raise Conflict('Export is not ready')
        return FileResponse(directory / 'export.mp4', media_type='video/mp4', filename='veil-redacted.mp4')

    return app
