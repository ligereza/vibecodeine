# Phase 167 — curatoria project diagnostic fixture gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Source, target and consumer

- Canonical: `/home/mak/flujo/cultura/mak_curatoria/diagnostico_proyectos.py`
- Runtime: `/home/mak/curatoria/diagnostico_proyectos.py`
- Input: derived SQLite `assets`/`jobs` tables
- Outputs: `diagnostic.json`, project/family/organism JSONL and HTML plan

## Result

Both source/runtime files compiled. A temporary SQLite fixture with one 3D
editable asset, one image and five render frames was processed through the
real `main()` contract. Both returned exit `0`, produced the same six output
files and byte-identical content, and classified one project, one family and
one representative with the editable-first strategy. No real curatoria SQLite,
media, ledger, provider, GPU process or persistent service was touched.

## Decision

The exact source/runtime files remain separate data-bound copies. The command
contract is healthy and is ready for a later real-data run only with an
explicit output/rollback boundary; this phase does not promote or rewrite real
diagnostic artifacts.
