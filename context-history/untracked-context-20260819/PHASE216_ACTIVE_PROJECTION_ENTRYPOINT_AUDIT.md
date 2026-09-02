# Phase 216 — active projection entrypoint audit

Date: 2026-08-15 (America/Santiago)

## Results

Static AST parsing covered 110 Python files in the root Research, Codex,
Curatoria, Plataforma, Vigia and language projections:

- 109 files parsed successfully.
- 1 file failed: `/home/mak/plataforma/panel_directivo.py`,
  `SyntaxError: expected 'except' or 'finally' block` at line 145.

That file is already classified as incomplete historical evidence with no
active consumer. It was not repaired or promoted into a runtime path.

Safe foreground commands all exited 0:

- `python -m flujo health`
- `python -m flujo rd-db packs`
- `python -m flujo job status /home/mak/flujo/jobs/2026-07-04_eventos-brief`
- `python -m flujo datadrop list`

The CLI compatibility fix remains active and real RD job products/pending
items render correctly. No service, worker, cron, provider, GPU path, live
render, field ingest or mutator was run.

## Interpretation

The one syntax failure does not contradict the active architecture because the
file has no verified consumer and is explicitly preserved as evidence. It does
remain an unresolved historical artifact in the final audit, so the overall
MAK objective is not yet complete.

## Next concrete action

Create the final objective/cleanup status snapshot, then decide whether the
single platform UI candidate and empty staging directory have enough evidence
for reversible quarantine. Do not delete the incomplete panel, WIN, databases,
media or recovery surfaces.

