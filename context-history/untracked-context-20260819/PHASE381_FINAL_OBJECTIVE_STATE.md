# Phase 381 — final objective state after local cleanup

Date: 2026-08-15 (America/Santiago)

This matrix is a current-state closeout of the authorized local work. It does
not promote fixture success to live data ingestion, external-provider access,
or a Git operation.

| # | Objective | Current evidence | State | Next gate |
|---:|---|---|---|---|
| 1 | RD datos de terreno | `PHASE371_RD_FIELD_REVIEW_PACKET.md`; 42 events remain candidate evidence; live `data/rd_datos.db` has 0 rows and unchanged SHA | `OPEN_AUTHORITY_DATA_QUALITY` | Human review of dates, links, required fields and privacy before ingest |
| 2 | Fusion de bases RD | Canonical catalog/projections are merged; `data/rd_datos.db` remains a separate empty privacy/runtime store with integrity check green | `VERIFIED_SEPARATE_STORES` | Do not merge the empty privacy store without an approved schema/data decision |
| 3 | Rutas mutadoras RD | `PHASE373_RD_MUTATOR_STATIC_CONTINUITY_GATE.md`; 16 POST routes and 5 helpers parse and remain continuous | `STATIC_PASS_LIVE_OPEN` | Name one target mutation, fixture, rollback and authority before a foreground write |
| 4 | Automatización FLUJO | EVENTO issue/URL bridge confirmed by user; cron count 0; n8n path discarded and decoupled from active consumers | `PAUSED_CONFIRMED` | Only adapter-level maintenance if the issue/provider contract changes |
| 5 | Comandos sin serve | Health, doctor, read-only CLI, render-input and local import gates passed | `VERIFIED_LOCAL` | Keep bounded regression checks; no permanent service needed |
| 6 | Assets RD | Index, duplicate grouping, SVG, ZIP, catalog/config and rescale consumers passed local checks | `VERIFIED_LOCAL_EXTERNAL_EDGES` | Review only external render/provider edges if a real delivery requires them |
| 7 | Dependencias | Base `pip check` is green; optional provider/GPU/render edges remain explicitly gated | `BASE_VERIFIED_OPTIONAL_OPEN` | Resolve per slice, not from the Windows global pip-check snapshot |
| 8 | Arquitectura de carpetas MAK | `/home/mak/*` physical map and projection owner matrix are documented; no broad move was performed | `PROPOSED_NOT_MOVED` | Approve owner manifests/launchers before physical relocation |
| 9 | Documentos duplicados | Provenance/index ledger and separator-normalized grouping fix are in place; evidence, memories and products protected | `CLASSIFIED_NO_BROAD_DELETE` | Quarantine only an exact path with consumer/provenance proof |
| 10 | Tools equivalentes | Research, platform, Codex, Curatoria, Vigia and Lenguaje owner/parity gates passed; intentional wrappers retained | `OWNER_PARITY_VERIFIED` | Consolidate one consumer family at a time with inverse rollback |
| 11 | Auditoria completa MAK | Health, doctor, pip, active AST 371/371, SQLite, projection parity and cron safety pass | `LOCAL_PASS_EXTERNAL_OPEN` | Audit only intentionally excluded external boundaries when authorized |
| 12 | Basura confirmada / WIN | 6,060 regenerable pyc plus 13 mak_ops pyc removed; seven malformed generated scripts and one destructive sync repairer moved to reversible quarantine; WIN untouched | `LOCAL_CLEANUP_PASS` | Review remaining candidates path-by-path; preserve WIN and protected evidence |
| 13 | Sistema de ramas Git | `PHASE375_GIT_BRANCH_SYSTEM_REFRESH.md`; branch/write-set proposal and merge order documented | `PROPOSAL_ONLY` | User must authorize a worktree snapshot and branch creation |

## Physical and safety invariants

- `/home/mak/flujo` remains the authoring/integration baseline.
- `/home/mak/WIN` remains historical read-only evidence.
- `rd_datos.db` integrity is good and the database remains empty.
- No cron job, MAK service, SSH action, provider call, live mutator or Git
  mutation was started by Phase 381.
- Quarantined files are recoverable from
  `context/quarantine/phase376_malformed_generated_codex/` and
  `context/quarantine/phase379_legacy_sync_repair/`.

Disposition: `LOCAL_OBJECTIVES_CONSOLIDATED; AUTHORITY_GATES_EXPLICIT`.
