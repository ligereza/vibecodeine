# Phase 114 — platform work/backlog automation ownership merge

## Scope and evidence

`trabajo.py` and `backlog_codex.py` were byte-identical across active MAK root,
canonical source and WIN. They are real automation consumers, but their direct
entrypoints can write state/backlog and dispatch work.

## Action

Replaced only the two active root files with compatibility projections to
canonical MAK. WIN, work state, logs, backlog text, ledgers, jobs and generated
outputs were not changed. No entrypoint was executed.

## Foreground validation

- Root imports for both modules and callable main contracts: exit 0.
- Root bridges and canonical sources compile: exit 0.
- No work tick, backlog refill, provider, queue, worker, hub, Blender or
  Ollama process ran.

## Rollback and risk

Rollback is local from pre-edit root files or WIN copies. The entrypoints remain
stateful automation boundaries and require a separate foreground dry-run gate.
`capataz.py` and `chat_agente.py` remain separate due WIN variants.

## Result

The active platform work/backlog automation now has one MAK implementation
owner without triggering its writers or dispatchers.
