"""Build an inspectable local submission package from committed files only."""

import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data/release"
TARGET.mkdir(parents=True, exist_ok=True)
REVISION = subprocess.run(
    ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
).stdout.strip()
FILES = (
    subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "-z", REVISION],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    .stdout.decode()
    .split("\0")
)
SOURCE = TARGET / "context-source.zip"
with zipfile.ZipFile(SOURCE, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for name in filter(None, FILES):
        path = Path(name)
        if path.name.startswith(".env") and name != ".env.example":
            raise ValueError("Environment secret file cannot be packaged")
        if path.parts[0] in {"data", ".venv", "node_modules"}:
            raise ValueError("Private/generated data cannot be packaged")
        content = subprocess.run(
            ["git", "show", f"{REVISION}:{name}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        ).stdout
        archive.writestr("context/" + name, content)

VIDEO = ROOT / "demo-video/renders/context-demo-3min.mp4"
if not VIDEO.is_file():
    raise ValueError("Render the final narrated video before packaging")
BUNDLE = TARGET / "context-submission.zip"
with zipfile.ZipFile(BUNDLE, "w", compression=zipfile.ZIP_STORED) as archive:
    archive.write(SOURCE, SOURCE.name)
    archive.write(VIDEO, "context-demo-3min.mp4")
    for name in [
        "docs/submission.md",
        "docs/evaluation.md",
        "demo-video/verification.json",
        "docs/demo-script.md",
    ]:
        content = subprocess.run(
            ["git", "show", f"{REVISION}:{name}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        ).stdout
        archive.writestr(name, content)
MANIFEST = {
    "revision": REVISION,
    "files": [],
    "scope": "Source from committed files plus final narrated MP4; no credentials or private media.",
}
for path in [SOURCE, BUNDLE, VIDEO]:
    MANIFEST["files"].append(
        {
            "name": path.name,
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    )
(TARGET / "manifest.json").write_text(json.dumps(MANIFEST, indent=2) + "\n")
print(json.dumps(MANIFEST, indent=2))
