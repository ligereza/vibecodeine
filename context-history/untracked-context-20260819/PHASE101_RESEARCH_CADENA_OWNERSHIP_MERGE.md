# Phase 101 — research cadena ownership merge

## Scope and evidence

The active MAK root `/home/mak/research/cadena.py` and canonical
`/home/mak/flujo/cultura/mak_research/cadena.py` were byte-identical (SHA-256
`94c4db127c15c5cc5067542eac9394545308065436fe4aece05f6a95e4641528`). The
WIN historical file is a distinct variant (SHA-256
`1c49c4f0527b33145a086acb5d032a4e593f5fca0eff062a25310232f1a7bd06`), so it
was preserved as provenance and was not used as the active source.
`worker.py` selects `cadena.py` as a real mode and the module has a direct
command entrypoint.

## Action

Replaced only `/home/mak/research/cadena.py` with a compatibility projection to
the canonical MAK implementation. The bridge re-exports the implementation
and forwards `main()` for `__main__`. No model/provider, notification, report,
checkpoint or job action ran.

## Foreground validation

- Root import from `/home/mak/research`: exit 0.
- Root `python cadena.py --help`: exit 0.
- Root bridge and canonical source compile: exit 0.
- No research, worker, hub, Blender or Ollama process remained.

## Rollback and risk

Rollback is local from the preserved pre-edit root content or the WIN
historical variant. The WIN divergence remains an explicit historical
comparison item. Public and private names are re-exported; module metadata
callers remain an untested edge. External-capable execution was not invoked.

## Result

MAK now has one active implementation owner for `cadena.py`; WIN remains an
unaltered historical variant requiring semantic review before any future
cross-platform reconciliation.
