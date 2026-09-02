# Phase 212 — language and deploy dependency/runtime matrix

Date: 2026-08-15 (America/Santiago)

## Matrix

| Slice | Runtime inputs | External dependencies | Side effects | Static result |
|---|---|---|---|---|
| `/home/mak/lenguaje` | `/home/mak/lenguaje` dictionaries/lexicon; Research and Codex output directories | Python stdlib; `corregir.py` imports the local Research wrapper (`research_lib`) and may call the configured capable model only when explicitly invoked | `hook_barrido.py` appends markers; `cron_lexicon.sh` rewrites lexicon log/output; `corregir.py` writes a sibling `.corregido.md` | all four language modules compile; both language copies import in isolated process; both shell scripts pass `bash -n` |
| `/home/mak/flujo/cultura/mak_lenguaje` | canonical source projection for language tools | Python stdlib plus local `research_lib` boundary for correction | same write-capable behavior; cron lines are paused in the documented crontab | compile/syntax pass; no execution |
| `/home/mak/flujo-deploy` + `/home/mak/bin/mak_sync_safe.py` | disposable deploy worktree; root department projections | Python stdlib, `git` CLI, filesystem permissions, `fcntl`; no provider package | fetch/reset deploy worktree, backup live drift, copy projections, write manifest; **not called** | deploy script compiles; source consumer and rollback paths are explicit |

## Commands and exit codes

- `python -m py_compile` for 9 Python files (4 root language, 4 canonical
  language, 1 deploy script): every file exit 0.
- `bash -n` for 4 language shell scripts: every file exit 0.
- Isolated import of `lenguaje_lib`, `hook_barrido`, `corregir` and
  `mak_sync_safe`: exit 0 (`imports=4`).
- No cron, `git fetch/reset`, deploy copy, provider call, model call or worker
  was executed.

## Decision

Language and deploy are not dead duplicate folders. They are distinct
consumers with different side effects and platform roles. Keep them physically
separate, document the canonical/physical relationship, and do not merge their
files solely because both have Spanish/English names or mirrored scripts.

## Next concrete action

Run the read-only RD route/field-data audit: enumerate every route touching
`rd.db` or `rd_datos.db`, classify GET/POST and filesystem/database side
effects, and validate only the GET surface. Do not ingest field data or call a
mutating route.

