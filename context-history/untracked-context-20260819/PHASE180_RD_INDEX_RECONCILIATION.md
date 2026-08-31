# Phase 180 — RD physical/index reconciliation

Status: `RECONCILED_WITH_EXTERNAL_RENDER_ORPHANS`

The comparison used relative paths, byte sizes, and nanosecond mtimes only.
It did not recalculate hashes, open SQLite for writing, copy media, or follow
the external mounted render root.

## Result

| Check | Result |
|---|---:|
| Regular files under `/home/mak/RD` | 1,742 |
| Symlinks under `/home/mak/RD` | 1 |
| RD rows in lab index (`source_key=813a1a4d33191f7fd2b6`) | 1,742 |
| Regular files absent from RD index | 0 |
| RD index rows absent from regular filesystem | 0 |
| RD byte-size mismatches | 0 |
| RD mtime mismatches | 0 |
| Symlink indexed as regular asset | 0 |

The one symlink is
`AUTOMATIZACION/cartelera.blend -> AUTOMATIZACION/RD.blend`. It is not an
unindexed regular asset and must not be removed as a duplicate without an
explicit symlink/consumer decision.

## Why the index has 1,749 rows

The remaining seven rows belong to a different source key
`e2d8a9f6717301c33674`, whose metadata declares the root
`/home/mak/GoogleDrive/RD/renders` and role `rd_issue_render`. That root is not
the active `/home/mak/RD` corpus used for this reconciliation. The seven rows
are therefore external-render evidence/orphans relative to this local walk,
not missing files to recreate and not files to delete from RD.

The index's embedded summary still says 1,742 assets and 47 exact-duplicate
relations, while its current tables contain 1,749 rows and 49 exact-duplicate
relations. The local RD subset is internally path/size/mtime complete; the
summary discrepancy belongs to the mixed snapshot/provenance layer.

## Consequence for cleanup and integration

No physical duplicate is authorized for deletion. Exact duplicate relations
remain candidates only after classifying source/editable/delivery/cache and
historical roles. The next useful slice is a temporary-fixture validation of
the existing `ingesta_archivo.py` index reader/writer boundary, with the live
RD corpus and lab database untouched.

## Validation

The reconciliation Python command exited `0` and left no process. All SQLite
reads used `file:...?...mode=ro`. No package, service, cron, provider, GPU,
WIN, or Git action was used.
