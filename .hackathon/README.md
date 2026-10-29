# CONTEXT interactive Codex session via OmniRoute / Antigravity

This is an interactive Codex launcher. It installs nothing, does not delete existing project files, and starts a new Codex terminal session with `START_AGENT.md` as its initial instruction.

## Usage

Unzip the bundle to Downloads, then run:

```bash
CONTEXT_REPO="$HOME/Code/Projects/hackathons/context" bash "$HOME/Downloads/context-codex-interactive/start-context-codex.sh"
```

If auto-discovery from OmniRoute's local model catalog fails, provide your already verified Antigravity model ID:

```bash
CONTEXT_REPO="$HOME/Code/Projects/hackathons/context" \
ANTIGRAVITY_MODEL='YOUR_VERIFIED_MODEL_ID' \
bash "$HOME/Downloads/context-codex-interactive/start-context-codex.sh"
```

Requires `omniroute`, `codex`, a working OmniRoute service or connection, and your existing CONTEXT Git repo. The script copies missing reference files to `.hackathon/` and never overwrites files that exist. It disables `cua_repl` and `node_repl` only for this session (previous JSON schema error suspects), keeps workspace sandboxing, and loads the complete project context into the initial prompt. No deployment, publishing or submission authorized.
