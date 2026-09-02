# Phase 330 — local MAK/FLUJO doctor gate

Date: 2026-08-15 (America/Santiago)

Command: `PYTHONPATH=/home/mak/flujo/src:/home/mak/flujo
PYTHONDONTWRITEBYTECODE=1 /home/mak/venvs/flujo/bin/python -m flujo doctor`.

Result: exit code 0. Version, Python interpreter, UTF-8 stdout, repo root,
workspace, jobs, inbox, datadrops, optional index state, pending airdrop and
local port availability reported OK. The only warning was pre-existing local
working-tree changes; no Git command that mutates state was executed.

Physical safety recheck: `cron_active=0`; no matching `flujo serve`, uvicorn,
MAK sync, SearXNG, Ollama or Blender process was present. No source, data,
database, package, service, Git or WIN path changed.

Disposition: `LOCAL_HOST_HEALTH_VERIFIED`.

