# Phase 293 — filtro de entrada owner/projection gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none  
Status: `FUSED_CANONICAL_WITH_COMPATIBILITY_PROJECTION`

## Scope and consumer proof

The bounded family was:

- canonical implementation: `/home/mak/flujo/cultura/mak_plataforma/filtro_entrada.py`
- active runtime projection: `/home/mak/plataforma/filtro_entrada.py`

The old root file was byte-identical to the canonical implementation
(`805acada2eb9706807eae53063ea9841f47e19bc49386995990d686f48662c83`); its
direct path is load-bearing. Research and Codex call `import filtro_entrada`
after placing `/home/mak/plataforma` on `sys.path`, and `roles.py` lists the
root path in the active module rotation. The canonical module remains the
semantic owner.

## Action

Replaced only the root duplicate with a 1,499-byte compatibility projection
that loads the canonical file by absolute physical path, re-exports public and
private compatibility symbols, and preserves the historical CLI behavior.
No canonical source, data, WIN evidence, service, provider or scheduler was
changed.

Current hashes measured in the foreground are:

```text
805acada2eb9706807eae53063ea9841f47e19bc49386995990d686f48662c83  /home/mak/flujo/cultura/mak_plataforma/filtro_entrada.py
f183a515dd5783c5a1ecc3edede67c426cb1df64d623214ec288c349489b608f  /home/mak/plataforma/filtro_entrada.py
```

The projection is intentionally different because it is now a shim, not a
second implementation. The preimage hash of the old root duplicate was the
same canonical hash above.

## Foreground validation

| Command | Exit | Result |
|---|---:|---|
| `python3 -m py_compile` on canonical and projection | 0 | both parse |
| isolated import of root projection | 0 | `projection_import=ok` |
| `clasificar(..., usar_modelo=False)` | 0 | BYPASS and DESCRIPTIVO contracts pass |
| direct CLI with bypass input | 0 | `BYPASS ... -> BLOQUEADO` |
| `/home/mak/research/.venv/bin/pytest -q tests/test_mak_research_router.py tests/test_mak_gpu_activity.py` | 0 | 24 tests pass |
| `python3 tests/test_mak_research_lib.py` | 0 | 5 tests pass |
| direct `sys.path=/home/mak/plataforma; import filtro_entrada` | 0 | path consumer pass |
| process invariant check | 0 | no matching persistent MAK process |

The system Python has no pytest module (code 1 when attempted); the existing
`/home/mak/research/.venv/bin/pytest` executed the pytest-style cases without
installation. The Research library unittest file ran with system Python.

## Rollback

Restore the pre-Phase-293 root bytes from the recorded preimage hash
`805acada2eb9706807eae53063ea9841f47e19bc49386995990d686f48662c83` only
after an explicit rollback decision; the canonical source remains untouched
and is the recovery source. The current shim is recoverable as this phase
artifact. WIN remains read-only.

## Decision and next

`/home/mak/plataforma/filtro_entrada.py` is `COMPATIBILITY_PROJECTION`, not
junk and not a second owner. Keep it because direct callers require the path.
Next, audit the remaining exact platform projection family (`hub.py`,
`actividad.py`, or `research_router.py`) one consumer at a time. Prefer a shim
only if direct entrypoint behavior and all consumers can be proven; do not
merge divergent `backlog.py`, `capataz.py`, `salud.py`, `vigilar_red.py`,
`roles.py` or `trabajo.py` by filename.
