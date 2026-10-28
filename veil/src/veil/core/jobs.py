"""Local jobs with atomic manifests and per-job mutation locks."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
from uuid import uuid4
from veil.core.models import Timeline
from veil.media.inspect import inspect_media, decode_export
from veil.media.redact import render


class Conflict(Exception):
    pass


class JobStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def directory(self, job_id):
        if not re.fullmatch(r'[0-9a-f]{32}', job_id):
            raise FileNotFoundError('Unknown job')
        path = self.root / job_id
        if not path.is_dir():
            raise FileNotFoundError('Unknown job')
        return path

    @staticmethod
    def write(path, value):
        temp = path.with_name(path.name + '.' + uuid4().hex + '.tmp')
        temp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
        os.replace(temp, path)

    def get(self, job_id):
        return json.loads((self.directory(job_id) / 'job.json').read_text())

    @contextmanager
    def lock(self, job_id):
        path = self.directory(job_id) / '.lock'
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            raise Conflict('Job is busy; interrupted jobs may require manual lock removal') from exc
        try:
            os.close(fd)
            yield
        finally:
            path.unlink(missing_ok=True)

    def create(self, stream):
        job_id = uuid4().hex
        directory = self.root / job_id
        directory.mkdir(mode=0o700)
        source = directory / 'input.mp4'
        try:
            size = 0
            with source.open('wb') as output:
                while chunk := stream.read(1024 * 1024):
                    size += len(chunk)
                    if size > 100 * 1024 * 1024:
                        raise ValueError('Upload exceeds 100 MiB')
                    output.write(chunk)
            metadata = inspect_media(source)
            if not metadata['has_audio']:
                raise ValueError('This prototype requires an audio stream')
            job = {'id': job_id, 'status': 'uploaded', 'media': metadata,
                   'detection': 'not_run', 'verification': 'not_run',
                   'needs_human_review': True}
            self.write(directory / 'job.json', job)
            return job
        except Exception:
            shutil.rmtree(directory)
            raise

    def redact(self, job_id, timeline: Timeline):
        with self.lock(job_id):
            directory = self.directory(job_id)
            job = self.get(job_id)
            if job['status'] != 'uploaded':
                raise Conflict('Create a new job to render a different timeline')
            media = job['media']
            if (timeline.width, timeline.height) != (media['width'], media['height']):
                raise ValueError('Timeline dimensions differ from input')
            if abs(timeline.fps - media['fps']) > .001 or abs(timeline.duration_ms - media['duration_ms']) > 100:
                raise ValueError('Timeline timing differs from input')
            for track in timeline.visual_tracks:
                for region in track.regions:
                    if region.box[2] > timeline.width or region.box[3] > timeline.height:
                        raise ValueError('Region extends beyond input frame')
            if any(i.end_ms > timeline.duration_ms for i in timeline.audio_intervals):
                raise ValueError('Audio interval extends beyond input')
            job['status'] = 'rendering'
            self.write(directory / 'job.json', job)
            try:
                self.write(directory / 'timeline.json', timeline.model_dump(mode='json'))
                render(directory / 'input.mp4', directory / 'export.partial.mp4', timeline)
                inspection = decode_export(directory / 'export.partial.mp4')
                os.replace(directory / 'export.partial.mp4', directory / 'export.mp4')
                receipt = {'job_id': job_id, 'input_sha256': digest(directory / 'input.mp4'),
                           'output_sha256': digest(directory / 'export.mp4'),
                           'timeline_source': 'client_supplied_reviewed_timeline',
                           'automatic_detection': 'not_run', 'privacy_verification': 'not_run',
                           'needs_human_review': True, 'zero_leaks_guaranteed': False,
                           'media_inspection': inspection, 'api_cost_usd': 0}
                self.write(directory / 'receipt.json', receipt)
                job.update(status='rendered', verification='not_run')
                self.write(directory / 'job.json', job)
                return job
            except Exception:
                job['status'] = 'failed'
                self.write(directory / 'job.json', job)
                raise
            finally:
                (directory / 'export.partial-silent.mp4').unlink(missing_ok=True)
                (directory / 'export.partial.mp4').unlink(missing_ok=True)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
