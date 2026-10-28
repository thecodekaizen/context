"""Thin HTTP client; processing stays inside the engine."""
from pathlib import Path
import httpx


class VeilClient:
    def __init__(self, base_url='http://127.0.0.1:8000', *, transport=None):
        self.http = httpx.Client(base_url=base_url, timeout=180, transport=transport)

    def close(self):
        self.http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def create_job(self, path):
        with Path(path).open('rb') as video:
            response = self.http.post('/v1/jobs', files={'video': ('input.mp4', video, 'video/mp4')})
        response.raise_for_status()
        return response.json()

    def process(self, job_id, timeline):
        response = self.http.post(f'/v1/jobs/{job_id}/redact', json=timeline)
        response.raise_for_status()
        return response.json()

    def receipt(self, job_id):
        response = self.http.get(f'/v1/jobs/{job_id}/receipt')
        response.raise_for_status()
        return response.json()

    def download(self, job_id, destination):
        target = Path(destination)
        temporary = target.with_name(target.name + '.partial')
        try:
            with self.http.stream('GET', f'/v1/jobs/{job_id}/export') as response:
                response.raise_for_status()
                with temporary.open('wb') as output:
                    for chunk in response.iter_bytes():
                        output.write(chunk)
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
