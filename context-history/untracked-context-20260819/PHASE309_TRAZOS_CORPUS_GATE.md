# Phase 309 — trazo corpus and laser consumer gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Status: `VALID_GENERATED_CORPUS_UNRESOLVED_CONSUMER`

## Scope

The physical search began at `/home/mak/*` and narrowed to
`/home/mak/trazos`, the active FLUJO laser/trazador consumers and the known
output surfaces. No Git inventory, WIN mutation, service, renderer or
external tool was used.

## Physical findings

| Measure | Result |
|---|---:|
| SVG files in `/home/mak/trazos` | 649 |
| subdirectories | 0 |
| file type | SVG only |
| exact duplicate groups | 29 |
| files in exact duplicate groups | 59 |
| SVG structural tag failures | 0 |
| files with metadata/title/description | 0 |
| files with curve commands | 0 |
| same-basename matches in known active output surfaces | 0 |
| direct active references to `/home/mak/trazos` or `trazos/` | 0 |
| physical mtime window | 2026-07-27 10:01:47–10:02:57 |

The files are simple one-path, `currentColor` SVGs with opaque hash-like
names. Exact hash collisions are internal repetitions, not proof that one
path can be deleted: there is no manifest, title, job ID or consumer link to
choose a canonical filename.

## Consumer crosswalk

The active FLUJO laser module is `/home/mak/flujo/src/flujo/laser.py`; its
`lote()` consumer writes new work to a caller-provided destination under the
FLUJO repository (the CLI default is an ISKVW laser surface), not to
`/home/mak/trazos`. `plano/trazador.py` is a separate image-to-SVG producer
using Pillow. Neither module references the root trazo directory directly.

Therefore `/home/mak/trazos` is classified as `GENERATED_OR_HISTORICAL_SVG`
with an unresolved human/creative consumer. It must remain outside the
canonical source tree until a manifest or job establishes provenance.

## Foreground validation

```text
PYTHONPATH=/home/mak/flujo/src python3 -> flujo.laser.medir() on all 649 SVGs
result: 649 pass, 0 fail; representative geometry metrics emitted
static direct-reference scan of active source/departments
result: 0 references to /home/mak/trazos or trazos/
SHA-256 inventory of root SVGs
result: 29 exact groups / 59 files
```

No `/home/mak` file changed. No SVG was moved, deleted, rewritten or
re-rendered. No database, asset manifest, job, provider, service or output
was touched.

## Decision, risk and rollback

Do not merge this corpus into `flujo/assets`, `RD` or `flujo/iskvw/piel/laser`
by extension or hash. The safe future action is to create a path-level
manifest with source/job/owner and then compare visual variants. Until then,
the rollback is the unchanged directory at `/home/mak/trazos`; there is no
safe canonical survivor for any duplicate group.

## Next action

Continue with `/home/mak/bucle` as the next preserved cultural/source surface.
Map Spanish/English consumers and provenance statically before considering
any merge. Keep generated SVGs, creative evidence, WIN and all external or
mutating paths protected.
