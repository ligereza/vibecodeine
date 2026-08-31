# Phase 148 — RD generated output promotion

Date: 2026-08-15

## Scope

Only the five derived files owned by the active RD generator were considered:

- job JSON: `jobs/2026-07-04_eventos-brief/packs_servicios_rd.json`;
- job dark/white SVGs;
- editable dark/white SVGs under `svg/eventos_rd`.

PDFs, human RD deliveries, databases, `WIN`, source documents and unrelated
assets were explicitly outside this promotion.

## Action

The old five derived files were moved as complete individual files to the
reversible quarantine directory
`context/quarantine/phase148_rd_precanonical_outputs/`. The generator was then
run with its live job and SVG destinations and a temporary scratch directory.
No tree was copied and no evidence was deleted.

## Validation

- generator promotion: exit 0;
- generated JSON contract: PASS;
  `Informativo`, `Testeo y Informativo (ambos)`, `Servicio Completo (masivo)`;
  prices `250000/300000/500000`; complete total `500000`;
- post-promotion `/home/mak/venvs/flujo/bin/flujo verify --no-pytest`: exit 0;
- post-promotion web `npm run typecheck`: exit 0;
- post-validation process gate: 0 matching persistent hub/serve/generator/Vite
  processes.

The quarantined files are rollback material, not junk. The PDFs and other
delivery variants remain in place because their provenance and human-delivery
role are not equivalent to the five regenerated consumers.

## Decision

The active generator outputs are now aligned with the canonical RD tariff. The
next slice is the objective/ownership refresh and then the next consumer-backed
tool family; do not expand this promotion to PDF or human-delivery variants by
hash alone.

