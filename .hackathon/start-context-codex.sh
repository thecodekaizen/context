#!/usr/bin/env bash
set -euo pipefail

# Launch Codex through the user's existing OmniRoute / Antigravity account.
# No credentials are written to disk. No files in the existing repo are replaced.
# Usage:
#   ANTIGRAVITY_MODEL='agy/<exact-model-id>' bash launch-codex-omniroute.sh
# Optional:
#   CONTEXT_REPO='/absolute/path/to/existing/repo' ...

BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT="$HOME/Code/Projects/hackathons"
REPO="${CONTEXT_REPO:-}"
if [[ -z "$REPO" ]]; then
  for candidate in "$PARENT/context" "$PARENT/CONTEXT" "$PARENT/video-intelligence"; do
    if [[ -d "$candidate/.git" ]]; then REPO="$candidate"; break; fi
  done
fi
if [[ -z "$REPO" || ! -d "$REPO" ]]; then
  echo "Could not safely identify the EXISTING CONTEXT repository."
  echo "Set CONTEXT_REPO=/absolute/path/to/your/existing/repo and rerun."
  echo "Existing directories under $PARENT:"
  [[ ! -d "$PARENT" ]] || find "$PARENT" -maxdepth 2 -name .git -type d -print | sed 's@/.git@@'
  exit 2
fi
command -v codex >/dev/null || { echo 'codex CLI is not on PATH'; exit 3; }
command -v omniroute >/dev/null || { echo 'omniroute CLI is not on PATH'; exit 3; }

# Detect exact Antigravity model IDs from the router catalog; never guess.
MODEL="${ANTIGRAVITY_MODEL:-}"
if [[ -z "$MODEL" ]]; then
  MODEL="$(python3 - <<'PY' 2>/dev/null || true
import os, json, urllib.request
url = os.environ.get('OMNIROUTE_MODELS_URL', 'http://localhost:20128/v1/models')
req=urllib.request.Request(url, headers={'Authorization': 'Bearer '+os.environ.get('OMNIROUTE_API_KEY','local')})
try:
  with urllib.request.urlopen(req, timeout=4) as response:
    data=json.load(response)
  ids=[m.get('id','') for m in data.get('data',[]) if isinstance(m,dict)]
  ids=[i for i in ids if i.startswith(('antigravity/','agy/'))]
  ranked=sorted(ids,key=lambda i:(not ('pro' in i and 'high' in i), not ('pro' in i), not ('sonnet' in i),i))
  print(ranked[0] if ranked else '')
except Exception:
  pass
PY
)"
fi
if [[ -z "$MODEL" ]]; then
  echo 'Could not discover an Antigravity model from the local OmniRoute catalog.'
  echo 'Supply the exact model ID from your verified OmniRoute setup, e.g.:'
  echo "  ANTIGRAVITY_MODEL='agy/<your-valid-id>' bash launch-codex-omniroute.sh"
  echo 'For a remote OmniRoute, the env var is recommended.'
  exit 4
fi

mkdir -p "$REPO/.hackathon"
for file in START_AGENT.md VIDEO_INTELLIGENCE_VISION_DECISIONS.md VIDEO_INTELLIGENCE_IMPLEMENTATION_PLAN.md CODEX_START_HERE.md DATASET_REGISTRY.csv CONTEXT_Vision_Studio_React.zip; do
  if [[ -f "$BUNDLE_DIR/$file" ]]; then
    if [[ ! -e "$REPO/.hackathon/$file" ]]; then
      cp "$BUNDLE_DIR/$file" "$REPO/.hackathon/$file"
    else
      echo "Preserved existing $REPO/.hackathon/$file"
    fi
  fi
done

# Copy UX reference assets without replacing any existing files.
if [[ -d "$BUNDLE_DIR/ux" ]]; then
  mkdir -p "$REPO/.hackathon/ux"
  while IFS= read -r -d '' source_file; do
    relative="${source_file#"$BUNDLE_DIR/ux/"}"
    dest="$REPO/.hackathon/ux/$relative"
    mkdir -p "$(dirname "$dest")"
    if [[ ! -e "$dest" ]]; then cp "$source_file" "$dest"; fi
  done < <(find "$BUNDLE_DIR/ux" -type f -print0)
fi

printf 'Repo: %s\nModel: %s\n' "$REPO" "$MODEL"
echo 'Launching INTERACTIVE Codex session with project knowledge and incompatible desktop MCP tools disabled...'
cd "$REPO"
exec omniroute run codex --model "$MODEL" -- \
  --approve-for-me \
  -c 'mcp_servers.cua_repl.enabled=false' \
  -c 'mcp_servers.node_repl.enabled=false' \
  -C "$REPO" \
  "$(cat "$REPO/.hackathon/START_AGENT.md")"
