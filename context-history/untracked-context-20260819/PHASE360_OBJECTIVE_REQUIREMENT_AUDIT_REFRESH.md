# Phase 360 — 13-objective requirement audit refresh

Date: 2026-08-15 (America/Santiago)
Owner: LUNA principal

This matrix preserves the original scope. `VERIFIED` means the stated local
requirement has evidence; `OPEN` means the objective still has a named gate.

| # | Objective | Current evidence | Status | Remaining gate |
|---:|---|---|---|---|
| 1 | RD datos de terreno | Testeo 2025 candidate; real `rd-datos ingest` temporary dry-run: 762 accepted, 19 privacy rejects, 4,613 form rejects | `OPEN_AUTHORITY` | date/required-field/privacy review and strict ingest authority |
| 2 | Fusionar `rd.db` | active/WIN/state catalogs have identical 20-table/7,587-row content; premerge backup retained | `VERIFIED_CATALOG_MERGE` | keep `rd_datos.db` separate unless a privacy migration is explicitly defined |
| 3 | Rutas mutantes RD | all 16 POST paths classified; temporary symbol/logo/datadrop/review fixtures pass | `OPEN_LIVE_GATE` | one explicitly authorized live mutation with rollback |
| 4 | Automatizaciones FLUJO | EVENTO issue/URL bridge user-confirmed; crontab has zero active entries | `PAUSED_VERIFIED` | operational re-enable requires explicit authority |
| 5 | Comandos no-serve | help, health, version, read commands, job/knowledge/datadrop/render-format surfaces pass | `VERIFIED_LOCAL` | provider/mutator commands remain gated |
| 6 | Superficie de assets RD | index/duplicate, SVG, ZIP, catalog/config and rescale consumers pass locally | `VERIFIED_LOCAL_EXTERNAL_EDGES` | visual/external render and real export remain separate |
| 7 | Dependencias por slice | base venv `pip check` passes; optional laser/provider/editor/GPU edges classified | `VERIFIED_BASE_OPTIONAL_GATED` | promote only for a named consumer |
| 8 | Arquitectura final de carpetas MAK | physical architecture maps and Phase 358 vertical refresh exist; quarantines are reversible | `PROPOSED_NOT_FINAL` | path-specific move/fusion decisions with consumer proof |
| 9 | Documentos duplicados | bounded duplicate ledger classified 99 exact-hash groups/334 paths; protected evidence retained | `CLASSIFIED_NO_DELETE` | merge only a named family with inverse rollback |
| 10 | Herramientas equivalentes | canonical owners plus retained runtime projections; selected safe projections quarantined | `OWNER_FUSED_PROJECTIONS_RETAINED` | remove projection only with manifest/test proof |
| 11 | Auditoria completa MAK | health/import/CLI/SQLite/AST/local fixture gates pass; external-risk tests remain separated | `LOCAL_AUDIT_PASS_EXTERNAL_OPEN` | resolve or permanently classify external boundaries and truncated panel |
| 12 | Basura confirmada / WIN histórico | 92 `.DS_Store` and 7 shell-residue objects removed; other evidence quarantined reversibly; WIN untouched | `CONFIRMED_JUNK_ONLY` | no broad deletion; review remaining candidates path by path |
| 13 | Ramas Git | branch system proposal aligned with architecture; no Git mutation performed | `PROPOSAL_READY` | explicit request before creating/switching/merging/pushing |

## Audit conclusion

The local integration surface is materially wider than the original RD-only
slice, but the open states are real: field data, live mutators, automation
activation, optional promotion, final physical moves, external-risk coverage
and Git operations are not silently promoted by fixture results.

## Next concrete action

Reconcile the physical folder/disposition ledger against current top-level MAK
roots and identify one additional reversible cleanup or ownership decision
with an active-consumer proof. Do not delete protected evidence or touch WIN.
