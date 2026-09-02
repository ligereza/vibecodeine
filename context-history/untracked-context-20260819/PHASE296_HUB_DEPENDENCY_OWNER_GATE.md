# Phase 296 — Hub dependency owner/projection gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none  
Status: `FUSED_CANONICAL_WITH_RUNTIME_ALIAS`

## Crosswalk

The exact family was:

- canonical implementation: `/home/mak/flujo/cultura/mak_plataforma/hub.py`
- historical runtime path: `/home/mak/plataforma/hub.py`

The pre-change files were byte-identical, SHA-256
`9a8b861d6065606fcef3c9c4ba13350cfe94f6e8c806ad07df7cfccdb96b0255`.
The Hub imports 17 local modules. The dependency audit classified them as:

| Dependency group | Result |
|---|---|
| `copilot`, `providers`, `discernment`, `cuotas`, `ideas`, `gpu_guard`, `ledger`, `revision_episodios`, `visual_index`, `xio_evidence` | exact canonical/runtime pairs |
| `salud`, `backlog`, `revision`, `roles`, `trabajo`, `contrato_archivo`, `actividad`, `filtro_entrada` | runtime shims to canonical owners |
| `percepcion` | intentional Curatoria path `/home/mak/flujo/cultura/mak_curatoria/percepcion.py` |

No divergent runtime implementation remained in the Hub dependency set. The
Hub's `sys.path` insertion therefore resolves either canonical files or the
same canonical owners through shims; it does not select a second semantic
implementation.

## Action

Replaced only `/home/mak/plataforma/hub.py` with a 1,044-byte compatibility
projection. It loads and registers the canonical module, aliases the normal
import to that object so assignments to globals such as `HOME` remain visible
to existing tests/callers, and forwards direct execution to `main`.

Current hashes:

```text
9a8b861d6065606fcef3c9c4ba13350cfe94f6e8c806ad07df7cfccdb96b0255  /home/mak/flujo/cultura/mak_plataforma/hub.py
8ac11ae6a15181b23905d67f2d8951be97c5e807bd28a31a0394ac1bb8a13abd  /home/mak/plataforma/hub.py
```

## Foreground validation

| Command | Exit | Result |
|---|---:|---|
| `python3 -m py_compile` canonical and projection | 0 | both parse |
| `/home/mak/research/.venv/bin/pytest -q tests/test_mak_hub_eventos.py tests/test_mak_hub_salud.py` | 0 | 24 tests pass |
| `PYTHONPATH=/home/mak/flujo ... pytest -q tests/test_hub_durable_writers.py` | 0 | 6 tests pass |
| root-path `import hub` | 0 | canonical module alias loaded |
| root-path global patch check | 0 | `hub.HOME` mutation remains visible |
| static CLI forwarding check | 0 | `main` forwarding present |
| `systemctl --user is-active mak-hub.service` | 3 | inactive; service not started |

An initial combined test command was not counted: it named a nonexistent test
file and lacked `PYTHONPATH` for one package-style test. The corrected commands
above are the accepted evidence. No service, worker, provider, POST route,
render route, database, WIN evidence or scheduler was touched.

## Rollback

The previous root bytes are recoverable from the pre-change hash above and
the canonical implementation. Restore only after an explicit rollback
decision. The Hub's data/output paths remain unchanged.

## Decision and next

`/home/mak/plataforma/hub.py` is now a compatibility projection, not junk.
The Hub is integrated at the owner/path level without starting it. The next
large step is the first genuinely divergent semantic family, beginning with
`salud.py` or `roles.py`: compare canonical behavior, runtime callers,
configuration/data paths and tests before deciding whether its existing shim
is correct or whether a contract repair is needed. Do not merge by line count.
