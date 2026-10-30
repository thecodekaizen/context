"""Bounded, operator-managed technical source candidates, not verified originals."""

import json
import re
import shutil
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from .domain_policy import ROOT, require_files
from .media import digest

CATALOG_ROOT = ROOT / "data/source-catalog"
MAX_RECORDS = 100


class CatalogRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    title: str = Field(min_length=1, max_length=250)
    origin_url: str = Field(min_length=1, max_length=2000)
    license: str = Field(min_length=1, max_length=2000)
    tags: list[str] = Field(default_factory=list, max_length=20)


def records(root=None):
    root = Path(root) if root is not None else CATALOG_ROOT
    paths = sorted((root / "records").glob("*.json"))
    if len(paths) > MAX_RECORDS:
        raise ValueError("Technical source catalog exceeds its configured record limit")
    return [CatalogRecord.model_validate_json(path.read_text()) for path in paths]


def rank_records(entries, queries, limit=4):
    """Caption words order candidates; only later alignment establishes a match."""
    terms = set(re.findall(r"[a-z0-9]+", " ".join(queries).lower()))

    def score(record):
        words = set(
            re.findall(
                r"[a-z0-9]+", (record.title + " " + " ".join(record.tags)).lower()
            )
        )
        return (-len(terms & words), record.title.lower(), record.sha256)

    return sorted(entries, key=score)[:limit]


def register(path, *, title, origin_url, license, tags=(), root=None):
    """Register admitted bytes with provenance; never label them an original."""
    from urllib.parse import urlsplit

    parsed = urlsplit(origin_url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise ValueError(
            "Source provenance must be a public HTTPS URL without credentials"
        )
    path = Path(path)
    admission = require_files({"source": path})
    sha256 = admission["source"]["sha256"]
    record = CatalogRecord(
        sha256=sha256,
        title=title,
        origin_url=origin_url,
        license=license,
        tags=list(tags),
    )
    if not record.title.strip() or not record.license.strip():
        raise ValueError("Source title and license/permission record are required")
    root = Path(root) if root is not None else CATALOG_ROOT
    target = root / "media" / f"{sha256}.mp4"
    target.parent.mkdir(parents=True, exist_ok=True)
    if path.resolve() != target.resolve():
        shutil.copyfile(path, target)
    if digest(target) != sha256:
        raise ValueError("Registered source changed during acquisition")
    record_dir = root / "records"
    record_dir.mkdir(parents=True, exist_ok=True)
    temporary = record_dir / f"{sha256}.tmp"
    temporary.write_text(json.dumps(record.model_dump(), indent=2))
    temporary.replace(record_dir / f"{sha256}.json")
    return record
