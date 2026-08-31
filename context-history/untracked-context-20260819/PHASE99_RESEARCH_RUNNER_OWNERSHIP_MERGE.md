# Phase 99 — research runner ownership merge

## Scope and evidence

`/home/mak/research/research.py`, the canonical
`/home/mak/flujo/cultura/mak_research/research.py` and the WIN historical copy
were byte-identical (SHA-256
`6e4dd28f7e31273d83d7436c80ff7daf88179e02d167d4b359122d34d9dea0fe`). The
root runner has real department consumers through `worker.py`, `grafo.py`,
`interfaz.py` and direct human execution, so it remains a compatibility
entrypoint rather than being deleted.

## Action

Replaced only the root runner with a small projection that loads the canonical
implementation and forwards `main()` when invoked as `__main__`. No provider,
search, LLM, notification, report, checkpoint or job action was executed.

## Foreground validation

- Root import from `/home/mak/research`: exit 0.
- Root `python research.py --help`: exit 0.
- Root bridge and canonical source compile: exit 0.
- No research worker, hub, Blender or Ollama process remained.

## Rollback and risk

Rollback is local from the WIN historical copy or the pre-edit SHA. Public and
private names are re-exported; module metadata callers remain an untested low-
risk edge. External-capable execution was intentionally not invoked.

## Result

The active research runner has one implementation owner while preserving the
root department command contract.
