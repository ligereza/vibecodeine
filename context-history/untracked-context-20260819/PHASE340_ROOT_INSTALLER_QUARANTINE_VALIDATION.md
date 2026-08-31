# Phase 340 — root installer reversible quarantine

Date: 2026-08-15 (America/Santiago)

## Action

Moved exactly two ledgered files, with no deletion or execution:

- `/home/mak/install_mak.sh` →
  `/home/mak/flujo/context/quarantine/phase339_root_installers/install_mak.sh`
- `/home/mak/instalar.sh` →
  `/home/mak/flujo/context/quarantine/phase339_root_installers/instalar.sh`

The quarantine targets were confirmed absent before the move. Both files still
pass `bash -n`, retain mode `0755`, original byte sizes and original SHA-256
hashes. The inverse operation is a direct move from the quarantine paths back
to their original `/home/mak/*` paths, after checking the originals are absent.

## Post-action validation

- Original paths are absent; quarantine files exist and are readable.
- `cron_active=0`.
- No `flujo serve`, uvicorn, MAK sync, SearXNG, Ollama, Blender or Docker
  container was started by this action.
- A pre-existing root `dockerd` process was observed (PID 3169, started
  2026-08-13 20:10:25). `docker ps` showed no running containers; `docker ps
  -a` showed only stopped `searxng` and `open-webui` containers. Nothing was
  stopped, removed or altered.

## Disposition

`QUARANTINED_REVERSIBLY; EXTERNAL_DOCKER_STATE_PRESERVED`.

The root installer clutter is removed from the active `/home/mak/*` surface
without destroying historical evidence. Docker remains an external host
state; it is outside this cleanup action and requires separate authority if it
is ever to be stopped or cleaned.

