# Phase 138 - physical architecture surface map

This map records the remaining large MAK containers by role. Sizes are
orientation only; they are not deletion criteria.

| Surface | Observed size | Role | Status |
|---|---:|---|---|
| `/home/mak/flujo` | baseline | canonical source/runtime/data/jobs | ACTIVE_OWNER |
| `/home/mak/RD` | 57G | creative source, editable assets, deliveries and evidence | PROTECTED_LIVE_MEDIA |
| `/home/mak/curatoria_inbox` | 173G | inbound visual/audio/project material | PROTECTED_INBOUND |
| `/home/mak/portfolio_media` | 5.5G | portfolio media | PROTECTED_LIVE_OUTPUT |
| `/home/mak/renders` | 120K | rendered outputs | PROTECTED_OUTPUT |
| `/home/mak/trazos` | 4.9M | SVG/creative corpus | EVIDENCE_OR_SOURCE |
| `/home/mak/models` | 206M | `mobileclip_s0.pt` model artifact | OPTIONAL_MODEL_PROTECTED |
| `/home/mak/state` | 301M | Windows dependency probe metadata | EVIDENCE |
| `/home/mak/indexes` | 113M | SQLite/JSON derived indexes and reconciliation reports | DERIVED_INDEX_PROTECTED |
| `/home/mak/backups` | 166M | dated tar/dump backups | RECOVERY_PROTECTED |
| `/home/mak/quarantine` | 185M | prior quarantine and recovery evidence | RECOVERY_PROTECTED |
| `/home/mak/rollback` | 240M | rollback snapshots | RECOVERY_PROTECTED |
| `/home/mak/tmp` | 872K | temporary test/conductor artifacts | REVIEW_BY_PATH |

No large surface is a cleanup candidate by size. `curatoria_inbox`, RD,
portfolio media, models, indexes, backups, quarantine and rollback require
separate ownership/provenance gates before any move. WIN remains a separate
read-only historical surface.

## Foreground validation

The bounded inventory read directory sizes and up to two directory levels of
file names, exiting 0. It did not open media, model weights, credentials,
backups, indexes, rollback trees or WIN. No file was changed.

## Next action

Use this map to finish the folder architecture matrix and select only small,
path-specific cleanup candidates. Do not copy or recursively reorganize the
large media/evidence surfaces.
