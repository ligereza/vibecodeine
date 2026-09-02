# Phase 295 — research router owner/projection gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none  
Status: `FUSED_CANONICAL_WITH_COMPATIBILITY_PROJECTION`

## Scope and consumer proof

The family was:

- canonical implementation: `/home/mak/flujo/cultura/mak_plataforma/research_router.py`
- runtime projection: `/home/mak/plataforma/research_router.py`

The files were byte-identical before the phase, SHA-256
`7abe2882a1ca3732da4553d8cf21076d2df33184dbef97b53cf5e93d18c6b107`.
`trabajo.py`, `benchmark.py` and `tandas.py` consume the router; the active
test suite exercises route selection, profiles and result validation. The
module is pure deterministic routing: no file writes, network, provider,
database, worker or service entrypoint were found.

## Action

Replaced only the root duplicate with a 1,013-byte compatibility projection
that loads the canonical module, registers it in `sys.modules` for its
`dataclass` definitions, and re-exports its route API. The registration fix
was required after the first isolated import exposed the dataclass loader
error; it was corrected before the phase was accepted.

Current hashes:

```text
7abe2882a1ca3732da4553d8cf21076d2df33184dbef97b53cf5e93d18c6b107  /home/mak/flujo/cultura/mak_plataforma/research_router.py
34b47a4eb15424f56f3c3f686aff9f32c3a57fa69cab0e3f89a097eb284ba561  /home/mak/plataforma/research_router.py
```

## Foreground validation

| Command | Exit | Result |
|---|---:|---|
| `python3 -m py_compile` on canonical and projection | 0 | both parse |
| `/home/mak/research/.venv/bin/pytest -q tests/test_mak_research_router.py` | 0 | 21 tests pass |
| root-path import through `/home/mak/plataforma` | 0 | dataclass loader and import pass |
| route contract for RD factual event | 0 | `domain=rd`, `epistemic_mode=evidencia` |
| process invariant check from Phase 294 | 0 | no matching persistent MAK process |

The failed first shim import returned code 1 with a dataclass
`sys.modules` error. No state was changed by that failed import; the loader
was corrected and the final validation above passed.

## Rollback

Restore the pre-Phase-295 root bytes from the canonical preimage hash only
after an explicit rollback decision. The canonical source remains untouched;
no data, databases, WIN evidence, services or scheduler entries changed.

## Decision and next

`/home/mak/plataforma/research_router.py` is `COMPATIBILITY_PROJECTION`, not
junk. Keep it because direct runtime consumers require the path. The safe
exact projection queue is now exhausted for the simple pure families. `hub.py`
must be handled as a dependency crosswalk, not a blind shim, because its
canonical loader changes import precedence for divergent platform modules.
