# Phase 297 — salud projection gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none  
Status: `EXISTING_SHIM_VALIDATED_NO_CHANGE`

## Scope and finding

The health family is:

- canonical implementation: `/home/mak/flujo/cultura/mak_plataforma/salud.py`
- runtime projection: `/home/mak/plataforma/salud.py`
- provider health data: `/home/mak/research/salud_proveedores.json`

The root file is already a compatibility shim, not a second implementation.
It forwards its CLI to the canonical `snapshot()` and preserves the runtime
path. The canonical snapshot is read-only: it reads `/proc`, disk metadata,
process state and department product counts; it does not start services or
write health state. Provider health persistence belongs to `research_lib.py`,
not this system snapshot.

## Foreground validation

| Command | Exit | Result |
|---|---:|---|
| `python3 -m py_compile` canonical and projection | 0 | both parse |
| `PYTHONPATH=/home/mak/flujo ... pytest` health/provider/capataz tests | 0 | 52 tests pass |
| `python3 /home/mak/plataforma/salud.py` | 0 | valid JSON snapshot |
| snapshot schema assertion | 0 | all 8 required fields present; 5 service entries |
| `systemctl --user is-active mak-hub.service` | 3 | inactive; no service started |

An initial combined test command was not counted because `test_capataz.py`
needs the repository on `PYTHONPATH`; the corrected command above is the
accepted evidence. No provider call, database write, service, worker, cron,
XIO, n8n, WIN or external state changed.

## Decision and next

Keep `/home/mak/plataforma/salud.py` as a required runtime projection. No edit
was necessary. The next semantic crosswalk is `/home/mak/flujo/cultura/mak_plataforma/roles.py`
against its root projection and the autonomous scheduler declarations. The
crontab remains inactive; inspect only and do not re-enable autonomous work.
