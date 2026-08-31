# Phase 113 — platform council/backlog/revision ownership merge

## Scope and evidence

`junta.py`, `backlog.py` and `revision.py` were byte-identical across active
MAK root, canonical source and WIN. They have real consumers in capataz,
chat-agente, hub, trabajo and conductor. Their write/POST paths were not
executed.

## Action

Replaced only the three active root files with compatibility projections to
canonical MAK. WIN, backlog files, revision records, council reflections,
adjustments, logs and generated outputs were preserved.

## Foreground validation

- Root imports for all three modules: exit 0.
- Pure backlog parsing/validation and revision API read contract: exit 0.
- Root bridges and canonical sources compile: exit 0.
- No council model call, backlog write, revision POST, provider, worker, hub,
  Blender or Ollama process ran.

## Rollback and risk

Rollback is local from pre-edit root files or WIN copies. Council reflection,
backlog mutation and visual-review POST remain operational gates and were not
invoked.

## Result

Three platform tools now have one active MAK implementation owner while their
stateful writers and historical evidence remain protected.
