# Phase 319 — consolidated architecture and objective matrix

Date: 2026-08-15 (America/Santiago)
Owner: LUNA principal
Status: `ACTIVE_BASELINE_WITH_OPEN_GATES`

This matrix consolidates evidence already produced from `/home/mak/*`; it is
not a completion claim and does not authorize moves, deletes, Git operations,
providers or services.

## Objective matrix

| # | Area | Current owner/evidence | State | Concrete remaining gate |
|---:|---|---|---|---|
| 1 | RD field data | `flujo/data/rd_datos.db`, test/fixture gates | Partial | human field/date/privacy authority before real ingest |
| 2 | RD catalog DB | `flujo/data/rd.db`, 20 tables/7,587 rows; backup exists | Complete for catalog | keep `rd_datos.db` separate; no privacy merge |
| 3 | RD mutating routes | `src/flujo/rd`, 16 POST paths classified | Partial | named live input/output/rollback authority |
| 4 | FLUJO automation | EVENTO issue/URL bridge confirmed; cron paused | Partial | explicit operational re-enable only if requested |
| 5 | Non-serve CLI | CLI matrix and read-only checks | Verified local | provider/mutator commands remain gated |
| 6 | RD assets | RD index/render/export/read-only gates | Verified fixture | live delivery only by explicit request |
| 7 | Slice dependencies | runtime matrix and dependency reports | Verified local | resolve only named consumer dependencies |
| 8 | Folder architecture | Phase 188/269 layered ownership map | Baseline | path-specific consumer decisions |
| 9 | Duplicate documents | Phase 203 ledger and bounded hash groups | Classified | one family at a time with consumer proof |
| 10 | Equivalent tools | Phase 302 plus 308/314/315/318 gates | Classified | preserve load-bearing projections; merge only with launcher proof |
| 11 | MAK operation | health rc=0; broad local gates; persistent processes absent | Partial | residual pure risk batches; gated live/provider surfaces |
| 12 | Cleanup/WIN | reversible quarantine and pyc cleanup; WIN untouched | Partial | only independently confirmed regenerable residue/candidates |
| 13 | Git branches | Phase 218 proposal | Proposal ready | Git action requires explicit user authorization |

## Final house layout (target, without broad moves)

```text
/home/mak/flujo          canonical source, tests, contracts and data
/home/mak/{research,
  codex,curatoria,
  plataforma,vigia,
  lenguaje}               runtime department projections with owners
/home/mak/RD              protected creative/source/delivery corpus
/home/mak/{labs,indexes,
  state}                  derived evidence and operational state
/home/mak/{renders,
  portfolio_media,trazos} generated/source delivery surfaces
/home/mak/{apps,src,models,
  venvs,blender,searxng}  external runtimes and configuration
/home/mak/{backups,rollback,
  quarantine}             recovery and reversible audit evidence
/home/mak/WIN             historical Windows archive, read-only
```

The design deliberately keeps source, runtime projections, generated output,
external runtimes and historical evidence separate. Folder similarity alone is
not a move criterion.

## Tool-fusion rule and currently confirmed outcomes

- `mak_*` cultural modules are semantic owners where a runtime projection has
  a proven consumer.
- Exact paired files with active consumers remain synchronized projections;
  `copilot.py`, `contrato_archivo.py`, `diagnostico_proyectos.py` and the
  language pair passed focused gates. They are not duplicate junk.
- Writer families such as `corpus_a_micelio.py` remain protected until their
  launcher, output snapshot and rollback are explicit.
- The platform matrix has 25 exact pairs, 21 compatibility shims, no
  source-divergent pairs and four runtime-only files already quarantined or
  separately classified by prior gates.
- RD catalog copies and generated/creative documents remain protected by
  provenance; the active catalog is not chosen by hash alone.

## Immediate sequence

1. Continue pure consumer-backed residual gates in Research/platform.
2. Close the remaining non-serve/dependency/health slices with foreground
   evidence.
3. Reconcile only named cleanup candidates using reversible quarantine.
4. Refresh the objective audit.
5. Only then, if authorized, implement the proposed branch system.

## Invariants

`WIN` remains historical; `rd.db` and `rd_datos.db` retain separate lifecycles;
no active cron entry, service, worker, provider, XIO or n8n process is running;
no Git operation, package installation or protected-data deletion occurred.

