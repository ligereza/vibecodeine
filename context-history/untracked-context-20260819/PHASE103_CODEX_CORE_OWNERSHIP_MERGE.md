# Phase 103 — CODEX core ownership merge

## Scope and evidence

The active MAK root and canonical copies of `codex_lib.py` and `generar.py`
were byte-identical. WIN `generar.py` also matched; WIN `codex_lib.py` was a
distinct historical variant. CODEX consumers import `codex_lib` from the
generator, review/debug/test tools, conductor handlers and icon pipeline.

## Action

Replaced only `/home/mak/codex/codex_lib.py` and
`/home/mak/codex/generar.py` with compatibility projections to the canonical
MAK implementations. Direct generator execution remains available through
`__main__`; the library remains import-oriented. WIN, generated CODEX pieces,
logs, state and sandbox outputs were not changed.

## Foreground validation

- Root `codex_lib` import: exit 0; exported library contract available.
- Root `generar.py --help`: exit 0.
- Root bridges and canonical sources compiled: exit 0.
- No generator, sandbox, provider, model, worker, hub, Blender or Ollama
  process was started.

## Rollback and risk

Rollback is local from the pre-edit root files or preserved WIN copies. WIN
`codex_lib.py` divergence remains a semantic review item. Public/private names
are re-exported; module metadata callers remain an untested edge. External
CODEX execution remains gated.

## Result

MAK CODEX core and generator now have one active implementation owner while
historical WIN behavior and generated evidence remain preserved.
