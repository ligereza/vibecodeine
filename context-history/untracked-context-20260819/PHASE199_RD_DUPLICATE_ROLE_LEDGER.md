# Phase 199 — RD exact-duplicate role ledger

Status: `LEDGER_ONLY; NO_MEDIA_MUTATION`

Scope: the 49 current `exact_duplicate` relations in
`/home/mak/labs/rd-auto-index-20260813/archivo_index.sqlite`, joined back to
relative paths under the RD source-key subset. No media was copied, opened for
writing, moved, deleted or rehashed.

## Role grouping (path heuristic, candidate only)

| Role grouping | Relations | Meaning |
|---|---:|---|
| Delivery/label ↔ delivery/label | 13 | Export/label variants; often multiple numbered export folders |
| Named source/other ↔ named source/other | 11 | Same bytes in dated/working folders; semantic role unresolved |
| Asset library ↔ named source/other | 10 | Library snapshots versus named delivery/source files |
| Workspace/export ↔ workspace/export | 7 | Workspace and flyer export copies |
| Render output ↔ render output | 3 | Render cache/output copies |
| Delivery/label ↔ named source/other | 3 | Delivery and source naming overlap |
| Asset library ↔ asset library | 2 | Shared 3D/material library copies |

These labels are navigation aids, not deletion decisions. The strongest next
consumer candidate is the `packs_servicios_rd*`, `plano_rider*` and related RD
delivery family, because active FLUJO tariff/plano consumers already have
canonical sources and prior delivery gates. The exact duplicate is still a
delivery/evidence relationship, not proof that the RD asset can be removed.

## Crosswalk conclusions

- `rd.db`/`src/flujo/plano/packs.py` and the job/RD delivery files have different
  authority roles; do not replace the source catalog with an artwork snapshot.
- Render-output duplicates stay evidence until the delivery consumer confirms
  the canonical output path.
- Workspace/material duplicates stay with their editable project until a
  Blender/asset consumer gate exists.
- Named-source pairs such as event flyers require semantic review even when
  their bytes match.

## Validation

- Read-only SQLite relation query and path-role grouping: exit `0`.
- Consumer reference scan was bounded to active FLUJO/RD paths; prior canonical
  RD tariff/asset gates remain the authority.
- No media/database/provider/service/cron/package/WIN/Git mutation.

Next: build a focused delivery-family crosswalk for `packs_servicios_rd*` and
`plano_rider*`, mapping canonical tariff/plano readers to job/RD outputs. It
must end in preserve/no-change or a reversible candidate, not deletion.
