# Phase 108 — curatoria ingestion/report/orders ownership merge

## Scope and evidence

`ingesta_archivo.py`, `reporter.py` and `ordenes.py` were byte-identical across
active MAK root, canonical source and WIN. They have real consumers and direct
entrypoints. `extraccion_db.py` was deliberately excluded because canonical
MAK differs from root/WIN and requires semantic review.

## Action

Replaced only the three active root files with compatibility projections to
canonical MAK. WIN, fichas, curatoria databases, reports, logs and process
state were not changed. No ingestion, report generation, perception launch,
process kill, redeploy or database mutation ran.

## Foreground validation

- Root imports for all three modules: exit 0.
- `ingesta_archivo.py --help`: exit 0.
- Root bridges and canonical sources compile: exit 0.
- No perception, OCR, vision, reporter, watchdog, hub or child process
  remained.

## Rollback and risk

Rollback is local from the pre-edit root files or WIN copies. Ingestion,
report writing and `ordenes` process controls remain operational boundaries;
only safe import/help/compile checks ran. `extraccion_db.py` divergence is an
open semantic gate.

## Result

Three curatoria tools now have one active MAK implementation owner, with the
divergent candidate explicitly preserved for later review.
