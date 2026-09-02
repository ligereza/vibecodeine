# Phase 300 — network monitor boundary gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none  
Status: `STATIC_PASS_EXTERNAL_BOUNDARY_OPEN`

## Scope

- canonical monitor: `/home/mak/flujo/cultura/mak_plataforma/vigilar_red.py`
- runtime wrapper: `/home/mak/plataforma/vigilar_red.py`
- companion monitor: `/home/mak/flujo/cultura/mak_plataforma/red_watch.py`

`vigilar_red.py` is not an ordinary read-only utility. `revisar()` invokes
`ss` to inspect established connections, writes
`/home/mak/plataforma/logs/vigilar_red.json` atomically, and may call
`ntfy_publish` plus write an anti-spam marker. `red_watch.py` probes external
Internet addresses and writes outage state/log transitions. Both are
platform/network boundary tools, not candidates for blind fusion or automatic
execution during this audit.

The root `vigilar_red.py` is already a narrow CLI wrapper using `runpy`; no
second implementation was found and no edit was needed.

## Foreground validation

| Command | Exit | Result |
|---|---:|---|
| `python3 -m py_compile` monitor, wrapper and companion | 0 | all parse |
| operational-entrypoint and atomic-state tests | 0 | 10 tests pass |
| AST boundary check | 0 | state write and external alert classified |
| active crontab count | 0 | 0 entries |
| MAK service state | 0 | Hub/Research/Codex/XIO inactive |

No monitor was run, no network endpoint was called, no notification was sent,
no state/log file was changed, and no scheduler/service was enabled.

## Decision and next

Keep both monitors as authority-gated operational tools. Their presence in
`crontab.mak` is a dormant template declaration, not proof of active service.
Next return to a local deterministic family (`backlog.py`, `capataz.py`,
`revision.py` or `trabajo.py`) and verify its projection/consumer contract;
do not execute any network, provider, scheduler or mutator boundary.
