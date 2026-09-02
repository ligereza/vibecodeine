# Phase 200 — RD delivery family crosswalk

Status: `NUMERIC_CONTRACT_ALIGNED; VARIANT_OUTPUTS_PRESERVED`

## Authority and consumers

| Path/family | Role | Result |
|---|---|---|
| `/home/mak/flujo/data/rd_packs.json` + `src/flujo/plano/packs.py` | Canonical tariff source read by quote/plano/RD DB consumers | Operational owner |
| `/home/mak/RD/packs_servicios_rd.json` | Human delivery snapshot | Exact duplicate of `RD/New Folder/assets/...`; numeric pack contract aligned, wording/delivery context retained |
| `/home/mak/flujo/jobs/2026-07-04_eventos-brief/packs_servicios_rd.json` | Job output snapshot | Different wording/schema details, same numeric pack contract; preserve as job evidence |
| `/home/mak/RD/*/packs_servicios_rd*.pdf` and `plano_rider*.pdf` | RD delivery artifacts | Preserve by delivery role; exact hash is not deletion authority |
| `/home/mak/flujo/jobs/...` and `/home/mak/flujo/svg/eventos_rd/*editable.svg` | Generated/editable outputs served by FLUJO | Preserve and keep consumer paths explicit |

## Numeric contract

All four JSON surfaces agree on the three numeric pack values:

```text
Pack 1 / INFO:     250000 CLP, 6 volunteers, 9 m2, 1 stand
Pack 2 / TESTEO:   300000 CLP, 6 volunteers, 18 m2, 2 stands
Pack 3 / COMPLETO: 500000 CLP, 15 volunteers, 27 m2, 2 stands
```

The job JSON and canonical catalog differ in labels, accents and inclusion
wording, while preserving the numeric contract. This is a semantic/document
variant, not an exact duplicate to delete.

## Exact relations observed

- `/home/mak/RD/packs_servicios_rd.json` ↔ `/home/mak/RD/New Folder/assets/packs_servicios_rd.json`.
- RD gray PDFs and their New Folder/assets copies are exact matches.
- `plano_rider_dark.pdf` is exact across RD, New Folder/assets and the job.
- Job editable SVGs are exact with each other but are not the same byte form as
  the larger RD dark SVG snapshot.
- Job JSON is not byte-identical to RD JSON; preserve both roles.

## Decision

No merge or deletion. The correct fusion is already semantic: all live
tariff/quote/plano code reads the canonical data source, while RD/job files
remain delivery and evidence variants. A future cleanup may quarantine the
duplicate RD JSON only after confirming no human delivery workflow references
the historical path and after recording a rollback hash.

## Validation

- Read-only file/hash/JSON comparison: exit `0`.
- Existing quote/plano and RD catalog gates already pass.
- No media/database/provider/service/cron/package/WIN/Git mutation.

Next: use this crosswalk in the final visual/progress report and continue with
the remaining open RD mutation/field-data authority gate, not another duplicate
scan of this family.
