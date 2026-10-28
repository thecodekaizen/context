"""Archive local synthetic experiment evidence, never arbitrary private jobs."""
import os,re,shutil
from pathlib import Path


def archive_local_evidence(job_id,destination):
    if not re.fullmatch(r'[0-9a-f]{32}',job_id):raise ValueError('Invalid job identity')
    source=Path(os.getenv('VEIL_JOBS_DIR','artifacts/private/jobs'))/job_id
    if not source.is_dir():raise ValueError('Local job evidence unavailable; set VEIL_JOBS_DIR to this test service storage')
    destination.mkdir(exist_ok=True)
    for path in source.iterdir():
        if path.is_file() and path.suffix in ('.json','.txt'):
            shutil.copyfile(path,destination/path.name)
