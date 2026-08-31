# Phase 97 — contrato_archivo ownership merge

## Scope

Consolidate the exact duplicate implementation shared by the active canonical
MAK consumer and the historical direct `/home/mak/plataforma` entrypoints.
`/home/mak/WIN` and rollback snapshots are evidence and were not edited.

## Evidence before edit

- `/home/mak/plataforma/contrato_archivo.py`: 1,177 lines.
- `/home/mak/flujo/cultura/mak_plataforma/contrato_archivo.py`: 1,177 lines.
- `/home/mak/WIN/flujo/cultura/mak_plataforma/contrato_archivo.py`: byte-identical.
- Pre-edit SHA-256 for all three implementations:
  `0f582791fc41077b4c7ad93c76d9bf6aa8a8997d8ce6680f97d75805f442055c`.
- Active canonical consumers import from their local canonical directory.
  Root `hub.py` and `entregar_micelio.py` import the root module directly;
  rollback snapshots also retain direct historical imports.

## Action

Replaced only `/home/mak/plataforma/contrato_archivo.py` with a 35-line
compatibility projection that loads and re-exports the canonical implementation
from `/home/mak/flujo/cultura/mak_plataforma/contrato_archivo.py`.
The canonical 1,177-line source, WIN copy, rollback snapshots, data and logs
remain unchanged.

## Foreground validation

1. `python -m py_compile` on root shim and canonical source: exit 0.
2. Direct root import from `/home/mak/plataforma`: exit 0; schema and fixture
   entity returned as expected.
3. Canonical import and `convertir`/`desde_portfolio_item` fixture: exit 0;
   returned `piezas`, `vinculos` and `fixture-1`.
4. Root `hub` import only: exit 0 and exposed the canonical schema. No server
   was started.
5. Process check: no hub, worker, Blender or Ollama process remained.

One initial validation assertion incorrectly expected a `schema` key from
`convertir`; it returned the documented `piezas`/`vinculos` shape and was
corrected without changing code. The corrected check passed.

## Rollback and risk

Rollback is exact and local: restore the pre-edit root file from
`/home/mak/WIN/flujo/cultura/mak_plataforma/contrato_archivo.py` or the recorded
pre-edit SHA. Risk is limited to untested callers relying on module metadata
such as `__file__`; public constants, functions and private helpers are
re-exported. WIN and rollback evidence remain available.

## Result

Ownership is now single-source for the active root projection while historical
direct imports remain compatible. This is a verified consolidation, not a
whole-tree copy or deletion.
