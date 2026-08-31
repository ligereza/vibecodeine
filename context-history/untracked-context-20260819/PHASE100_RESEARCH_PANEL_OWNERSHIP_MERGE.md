# Phase 100 — research panel ownership merge

## Scope and evidence

The active root `/home/mak/research/panel.py`, canonical
`/home/mak/flujo/cultura/mak_research/panel.py` and WIN historical copy were
byte-identical (SHA-256
`6b83de6b56a8585cec7ffb1a67a1f2a9c8357382a7a4dd4c1bddeb2378850650`). The
research worker selects `panel.py` as a real mode, and direct execution is
documented, so the root path remains a compatibility entrypoint.

## Action

Replaced only `/home/mak/research/panel.py` with a compatibility projection to
the canonical implementation. The bridge re-exports the module and forwards
`main()` for `__main__`. No panel run, model/provider call, notification,
report, checkpoint or job mutation was executed.

## Foreground validation

- Root import from `/home/mak/research`: exit 0.
- Root `python panel.py --help`: exit 0.
- Root bridge and canonical source compile: exit 0.
- No research, worker, hub, Blender or Ollama process remained.

## Rollback and risk

Rollback is local from the WIN historical copy or pre-edit SHA. Public and
private names are re-exported; module metadata callers remain an untested
edge. The external-capable panel itself remains gated and was not run.

## Result

The active panel implementation now has one owner while worker and historical
direct entrypoints remain functional.
