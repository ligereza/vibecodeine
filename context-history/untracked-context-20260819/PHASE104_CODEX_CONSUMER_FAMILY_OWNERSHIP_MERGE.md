# Phase 104 — CODEX consumer family ownership merge

## Scope and evidence

`revisar.py`, `testear.py` and `worker_codex.py` were byte-identical across
active MAK root, canonical source and WIN. They have real consumers through
`interfaz_codex.py`, conductor handlers and the worker mode table. In
contrast, `agente_libre.py` differs between canonical MAK and root/WIN and was
not treated as a duplicate.

## Action

Replaced only the three active root files with compatibility projections to
the canonical implementations. Direct `revisar.py` and `testear.py`
entrypoints remain available; `worker_codex.py` remains import-oriented. No
review, test generation, worker, provider, model, sandbox, notification or
output action ran. `agente_libre.py`, WIN, generated pieces, logs and state
were untouched.

## Foreground validation

- Root imports for all three modules: exit 0.
- `revisar.py --help` and `testear.py --help`: exit 0.
- Root bridges and canonical sources compiled: exit 0.
- No CODEX worker, generator, provider, model, hub, Blender or Ollama process
  remained.

## Rollback and risk

Rollback is local from the pre-edit root files or WIN copies. `agente_libre.py`
requires a separate semantic comparison because canonical and root/WIN content
diverge. External-capable CODEX execution remains gated; module metadata
callers are an untested edge.

## Result

Three active CODEX consumers now have one implementation owner, while the
divergent free-agent tool remains explicitly open rather than being silently
replaced.
