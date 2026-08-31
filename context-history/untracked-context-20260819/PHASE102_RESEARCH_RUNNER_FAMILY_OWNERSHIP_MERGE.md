# Phase 102 — research runner family ownership merge

## Scope and evidence

The active MAK root and canonical files for `refutar.py`, `grafo.py`, `cola.py`
and `worker.py` were byte-identical. WIN also matched `refutar.py`, `cola.py`
and `worker.py`; WIN `grafo.py` was a distinct historical variant and was
preserved. All four have real consumers through the research worker, queue,
interface and direct command paths.

## Action

Replaced only the four active root files under `/home/mak/research` with
compatibility projections to the canonical MAK implementations. Direct
`__main__` behavior is preserved for `refutar`, `grafo` and `cola`; `worker`
remains import-oriented. No queue, worker, model/provider, notification,
report, checkpoint or job action was executed. WIN and all research state were
left unchanged.

## Foreground validation

- Root imports for all four modules: exit 0.
- `refutar.py --help` and `grafo.py --help`: exit 0.
- `cola.py` was not started because it is a permanent network loop; its bridge
  was compile-checked only.
- All four bridges and canonical sources compiled: exit 0.
- No research, worker, hub, Blender or Ollama process remained.

## Rollback and risk

Rollback is local from each pre-edit root file or the preserved WIN copies.
WIN grafo divergence remains a semantic review item. The bridges re-export
public/private names; module metadata callers remain an untested edge. Queue
and external-capable execution remain explicitly gated.

## Result

The active MAK research runner family now has one implementation owner, while
historical variants and stateful service boundaries remain preserved.
