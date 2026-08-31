# Phase 333 — architecture/objective refresh

Date: 2026-08-15 (America/Santiago)

| # | Objective | Evidence after latest gates | Verdict |
|---:|---|---|---|
| 1 | RD field data | temp ingest/report/privacy pass; real store untouched | implementation verified; authority open |
| 2 | rd.db fusion | canonical catalog stable; temp rebuild 20 tables/7,587 rows | catalog complete; privacy store separate |
| 3 | RD mutating routes | 16 POST paths/write sets and temp fixtures | contract verified; live authority open |
| 4 | FLUJO automation | EVENTO bridge confirmed; cron paused | locally confirmed; re-enable open |
| 5 | non-serve commands | readers and diagnostics pass; writers isolated | readers verified; writer gates open |
| 6 | RD assets | read/render/export/tracing fixtures | fixture verified; live delivery open |
| 7 | dependencies | base pip-check pass; Pillow/plano pass; optional matrix | base verified; optional gated |
| 8 | folder architecture | layered ownership and runtime provenance matrix | baseline verified; selective moves only |
| 9 | document duplicates | provenance/hash ledgers | classified; no hash-only deletion |
| 10 | equivalent tools | fallback logical fusion with deployment projections | consumer fusion partial; import migration open |
| 11 | full MAK audit | health/doctor pass; 188 bounded tests plus current fixtures | local evidence expanded; external boundaries open |
| 12 | cleanup/WIN | 278 pyc removed, reversible quarantines, Blender review | confirmed residue cleaned; candidates gated |
| 13 | Git branches | branch proposal ready, no Git mutation | proposal only; authorization open |

## Architecture decision

Keep the layered house from Phase 319. Preserve external runtimes and RD
creative projects separately from `/home/mak/flujo`; keep `/home/mak/WIN`
historical. Do not convert unresolved external or authority gates into cleanup
just because they are large or old.

## Next execution target

Select one remaining active non-external consumer or pure residual test family,
validate it in foreground, and update the handoff. The branch proposal remains
the final step after open gates are resolved or explicitly accepted.

