# Phase 72 — root projection cache cleanup

## Target

Removed only `__pycache__/*.pyc` from these explicit department roots:

`/home/mak/plataforma`, `/home/mak/research`, `/home/mak/codex`,
`/home/mak/curatoria`, `/home/mak/lenguaje` and `/home/mak/vigia`.

Virtual environments, `rollback`, logs, locks, JSONL state, documents,
creative assets, generated products and `/home/mak/WIN` were excluded.

## Result

- exact targets before: 250;
- exact targets after: 0;
- `python3 -m flujo health`: exit 0;
- no source, data, state, evidence, output or historical file was changed.

These were regenerable interpreter caches and are `CLEANED_REGENERABLE_CACHE`.
No other root-department artifact is automatically classified as junk.
