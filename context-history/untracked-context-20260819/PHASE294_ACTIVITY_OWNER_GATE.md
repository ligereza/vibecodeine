# Phase 294 — actividad owner/projection gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none  
Status: `FUSED_CANONICAL_WITH_COMPATIBILITY_PROJECTION`

## Scope and consumer proof

The family was:

- canonical implementation: `/home/mak/flujo/cultura/mak_plataforma/actividad.py`
- runtime projection: `/home/mak/plataforma/actividad.py`

The files were byte-identical before this phase, SHA-256
`c5fcc6fd2a70b9a9b6863a783209ab9768dd6bc877f1286f006241c049a3f1a8`.
Research, GPU guard and Hub import `actividad` through the platform runtime
path. The activity file is append-only telemetry and uses the stable
`mak-activity-v1` schema; it is not the job ledger or a queue database.

## Action

Replaced only the root duplicate with a 1,679-byte compatibility projection
that loads the canonical implementation, re-exports its API and synchronizes
`ACTIVITY_FILE`/`LOCK_FILE` overrides before calls. This preserves direct
imports, temporary test paths and the historical `read`/`inventory` CLI.
The canonical source, activity data, databases, WIN evidence, services,
providers and scheduler were not changed.

Current hashes:

```text
c5fcc6fd2a70b9a9b6863a783209ab9768dd6bc877f1286f006241c049a3f1a8  /home/mak/flujo/cultura/mak_plataforma/actividad.py
f48c411dd6aa80d301f26158ab43cc77eb736dc1485f8a2af3e2f9c3f3c96556  /home/mak/plataforma/actividad.py
```

## Foreground validation

| Command | Exit | Result |
|---|---:|---|
| `python3 -m py_compile` on canonical and projection | 0 | both parse |
| `/home/mak/research/.venv/bin/pytest -q tests/test_mak_gpu_activity.py tests/test_mak_research_router.py` | 0 | 24 tests pass |
| isolated import of root projection with temporary paths | 0 | record/read/inventory contract passes |
| direct CLI `python3 /home/mak/plataforma/actividad.py --limit 1` | 0 | JSON inventory emitted |
| process invariant check from Phase 293 | 0 | no matching persistent MAK process |

All writes in the custom contract check were inside Python's temporary
directory and were removed automatically on context exit. The direct CLI was
read-only against the existing activity log.

## Rollback

The old root bytes are recoverable from the canonical hash above or the phase
artifact. Restore only after an explicit rollback decision; do not delete or
rewrite the activity log. WIN remains read-only.

## Decision and next

`/home/mak/plataforma/actividad.py` is `COMPATIBILITY_PROJECTION`, not junk.
Keep the path because it is consumed by direct runtime imports. The next
exact family is `research_router.py`; `hub.py` is intentionally deferred:
although byte-identical, its canonical file prepends its own directory to
`sys.path` and imports divergent platform modules (`salud`, `backlog`,
`roles`, etc.), so a blind shim could change runtime semantics.
