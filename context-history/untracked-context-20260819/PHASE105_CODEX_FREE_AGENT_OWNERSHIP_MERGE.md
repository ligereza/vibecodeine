# Phase 105 — CODEX free-agent ownership merge

## Scope and evidence

`agente_libre.py` had three byte differences between canonical MAK and root/WIN,
all in comments; functions, constants and structure were identical. It has
real consumers in `capataz.py`, conductor handlers and the producer catalog,
but its pipeline can write CODEX pieces/jobs and call models.

## Action

Replaced only `/home/mak/codex/agente_libre.py` with a compatibility projection
to the canonical implementation. The behavioral content was unchanged; the
root direct entrypoint remains available. WIN, CODEX pieces, jobs, logs and
state were not changed.

## Foreground validation

- Root import and exported `_correr_unlocked`/`main` contract: exit 0.
- Root `agente_libre.py --help`: exit 0.
- Root bridge and canonical source compile: exit 0.
- No free-agent pipeline, model, provider, file write, worker, hub, Blender or
  Ollama process was started.

## Rollback and risk

Rollback is local from the pre-edit root file or WIN copy. The write and
external-model boundaries remain gated; only safe import/help validation ran.

## Result

CODEX now has one active owner for the free-agent harness. Historical WIN and
generated evidence remain preserved.
