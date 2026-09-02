# Phase 179 — RD asset metadata and duplicate crosswalk

Status: `OBSERVED_WITH_RECONCILIATION_REQUIRED`

Scope: read-only comparison beginning at `/home/mak/*`. No media was copied,
hashed again, deleted, or merged. No SQLite file was opened for writing.

## Physical roots and roles

| Path | Observed role | Evidence | Decision |
|---|---|---|---|
| `/home/mak/RD` | Active RD creative corpus and delivery workspace | 1,742 files; 60,865,045,370 bytes; top-level families include `AUTOMATIZACION`, `FLYER`, `suplementos`, `desde_issues`, `assets`, and dated workspaces | Keep as active evidence/assets. Do not flatten before consumer mapping. |
| `/home/mak/flujo/data/rd.db` | Regenerable RD catalog projection | 20 tables; integrity `ok`; 20 productoras, 3 venues, 7 real producer events, 3 packs, 8 supplements | Keep as canonical operational catalog projection. Readers open it read-only. |
| `/home/mak/flujo/data/rd_datos.db` | Privacy-first field-data store | 3 tables; all 0 rows; integrity `ok` | Keep separate. It is not a replacement or merge target for `rd.db`. |
| `/home/mak/labs/rd-auto-index-20260813/archivo_index.sqlite` | Derived metadata/index evidence for `/home/mak/RD` | Current rows: 1,749 assets; 1,585 full hashes; 164 pending; 49 exact-duplicate relations; source root metadata points to `/home/mak/GoogleDrive/RD/renders` while the run root is `/home/mak/RD` | Preserve as lab evidence. Reconcile before using as cleanup authority. |

## Current physical surface

The active RD tree reports 1,742 files and 60,865,045,370 bytes. Extension
counts are led by PNG (1,043), JPG (138), BLEND (103), PDF (82), AEP (53),
TIF (50), PSD (40), AI (39), and SVG (30). This is a mixed production corpus,
not a single duplicate family: source projects, renders, editable files,
exports, temporary workspaces, and recovery/automatic-storage folders coexist.

The latest embedded lab summary reports 1,742 assets and 47 exact duplicates,
but the current read-only SQLite rows report 1,749 assets and 49 exact
duplicate relations. It also reports 1,585 full hashes and 164 pending hashes.
The summary and the current rows therefore cannot be combined as if they were
one snapshot. The difference is a reconciliation task, not permission to
delete seven files or two relations.

Representative exact-duplicate relations observed in the derived index:

- `suplementos/etiquetas/magnesio gris.jpg` ↔ `suplementos/magnesio gris.jpg`
- `New Folder/assets/packs_servicios_rd_dark.svg` ↔ `referenciaprecios.svg`
- `New Folder/assets/packs_servicios_rd.json` ↔ `packs_servicios_rd.json`
- `suplementos/.../04_pre_fiesta.svg` ↔ its `flyers_vector_2800x2000` export
- `RESULTADOS_MANUAL/render_output.png` ↔ `render_output.png`

These are exact byte duplicates, but their destination/role may differ. They
are candidates for a later selective merge only after consumer and delivery
path checks. Exact hash equality alone is not a deletion rule.

## Reader crosswalk

`src/flujo/rd/database.py` declares source-of-truth inputs for the catalog
(reactivos, packs, supplements, productoras, venues/logos, event JSON, and
historical test evidence) and describes `rd.db` as their projection.

`cultura/mak_curatoria/ingesta_archivo.py` reads `rd.db` through
`_rd_primary_catalog_snapshot()` in SQLite read-only mode to resolve productora,
venue, and event candidates. A direct foreground check returned:

```text
CATALOG_STATUS OBSERVED
CATALOG_PRODUCTORAS 20
CATALOG_VENUES 3
CATALOG_EVENTS 7
READONLY_CONSUMER_RC=0
```

`src/flujo/rd/informe.py` reads `rd_datos.db` without creating it for the GET
summary path. A direct foreground check returned zero field records and the
mandatory presumptive/demo disclaimer. No real field data was present.

The lab index is not a runtime substitute for either database: it stores
asset paths, hashes, jobs, candidate observations, and relations. Its current
source-root metadata also requires correction/reconciliation before any
automatic downstream action.

## Validation record

Commands were read-only unless stated otherwise:

1. Python SQLite URI `mode=ro` inspection of `rd.db`, `rd_datos.db`, and
   `archivo_index.sqlite`: exit `0`; all three integrity checks returned
   `ok`.
2. `find`/`du` inventory of `/home/mak/RD`: exit `0`; 1,742 files and
   60,865,045,370 bytes observed.
3. Direct catalog and field-summary consumer smoke with the MAK venv:
   exit `0`; no persistent process remained.
4. Attempted `/home/mak/venvs/flujo/bin/pytest`: exit `127` because this venv
   has no pytest executable/module. This is an environment limitation, not a
   source failure; the available `flujo` CLI remains present.

## Risks and next action

- Do not merge `rd.db` with `rd_datos.db`; they have different authorities and
  privacy roles.
- Do not use the lab summary as the current row count until its snapshot
  provenance is reconciled.
- Do not delete exact duplicates until each path is classified as source,
  editable, delivery, cache, or historical evidence.

Next: reconcile the 1,742-file physical walk against the 1,749 lab rows using
relative paths and metadata only, then validate the existing RD asset/index
consumer (`ingesta_archivo.py` and its `archivo_index.sqlite` read path) on a
small temporary fixture. The reconciliation must output candidates only; it
must not modify the live corpus or SQLite databases.
