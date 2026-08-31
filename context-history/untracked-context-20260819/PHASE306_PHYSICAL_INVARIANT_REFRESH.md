# Phase 306 — physical invariant refresh

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none  
Status: `LOCAL_SURFACE_RECONCILED_EXTERNAL_GATES_OPEN`

## Foreground invariants

| Check | Result |
|---|---|
| `/home/mak/flujo/data/rd.db` SQLite integrity | `ok`; 20 tables |
| `/home/mak/flujo/data/rd_datos.db` SQLite integrity | `ok`; 4 tables; `registros_testeo=0` |
| installed crontab active non-comment entries | `0` |
| MAK user units | research, queue, hub, codex and xio all inactive |
| matching persistent processes | none observed |
| selective quarantine files | 4 preserved with hashes in Phase 303/305 |

SQLite was checked with Python's standard `sqlite3` module because the
standalone `sqlite3` binary is not installed. No database was opened for
writing.

## Reconciled objective state

| # | Objective | Current state |
|---:|---|---|
| 1 | RD field data | dry-run verified; live privacy ingest authority open |
| 2 | RD DB fusion | catalog merged; privacy store correctly separate |
| 3 | RD mutating routes | fixtures pass; live input/output/rollback authority open |
| 4 | FLUJO automation | user-confirmed working bridge; scheduler intentionally paused |
| 5 | non-serve commands | local read/help/compile gates pass |
| 6 | RD assets | local fixture/read slices pass; live delivery optional |
| 7 | slice dependencies | local matrix pass; optional/provider promotion gated |
| 8 | folder architecture | layered owner/projection/quarantine baseline established |
| 9 | duplicate documents | classified; named unconsumed projections quarantined reversibly |
| 10 | equivalent tools | owner/shim/projection families fused selectively |
| 11 | full MAK operation | local slices and targeted tests pass; external/live risk families remain gated |
| 12 | junk/WIN | confirmed residue quarantined/removed selectively; WIN preserved |
| 13 | Git branches | branch system proposal ready; no Git operation authorized |

The old broad AST experiment is not used as an active baseline because it
included generated Python artifacts; the bounded 445/444 baseline remains the
reference, with its sole known syntax failure (`panel_directivo.py`) now
quarantined and the `material` import contract repaired in Phase 304.

## Next

Local duplicate/projection cleanup has reached a coherent checkpoint. The next
work should be a visual/objective closeout and then one explicitly authorized
external gate: real RD field input, one live mutator with rollback, optional
dependency promotion, automation re-enable, or Git branch creation. Do not
invent authority for any of them.
