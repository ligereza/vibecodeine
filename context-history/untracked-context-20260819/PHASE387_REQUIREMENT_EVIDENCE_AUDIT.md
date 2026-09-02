# Phase 387 — 13-objective requirement-to-evidence audit

Date: 2026-08-15 (America/Santiago)

This is a completion audit against the original 13 objectives. A report or
fixture is counted only at the scope it actually verifies.

| # | Requirement | Evidence checked | Current verdict | Missing proof / next action |
|---:|---|---|---|---|
| 1 | RD datos de terreno | `PHASE371_RD_FIELD_REVIEW_PACKET.md`; 42 candidate events; `rd_datos.db` four tables, 0 rows | `INCOMPLETE` | Human date/required-field/privacy review and ingest authority |
| 2 | Fusion of `rd.db` | canonical `/home/mak/flujo/data/rd.db`, WIN/state table comparison, recoverable premerge copy | `VERIFIED_FOR_RD_DB_CATALOG` | Keep `rd_datos.db` physically separate unless a privacy/schema decision changes |
| 3 | RD mutating routes | 16 POST routes, 5 helpers, fixture gates and rollback evidence | `STATIC_AND_FIXTURE_PASS` | One named live mutation, rollback and authority remain unverified |
| 4 | FLUJO automation | user-confirmed EVENTO issue/URL behavior; active cron 0; n8n decoupled/discarded | `USER_CONFIRMED_PAUSED` | External replay/provider contract not executed in this environment |
| 5 | Non-serve `flujo` commands | CLI/read-only/health/help and bounded fixture reports | `VERIFIED_LOCAL` | Continue only if a newly discovered command lacks a contract |
| 6 | RD assets | index, SVG, ZIP, catalog/config and rescale fixture reports | `LOCAL_PASS_EXTERNAL_EDGES_OPEN` | External render/provider delivery remains untested |
| 7 | Slice dependencies | base `pip check=0`; Windows global conflicts intentionally not promoted | `BASE_PASS_OPTIONAL_OPEN` | Verify optional dependencies only with a named slice/provider |
| 8 | Final MAK folder architecture | physical owner map and Phase 386 Mermaid closeout | `DESIGN_VERIFIED_NOT_RELOCATED` | No broad relocation is justified without owner/consumer/rollback |
| 9 | Duplicate documents | 4,143-file bounded scan; 99 hash groups/334 paths; provenance/consumer classes | `CLASSIFIED_NOT_PHYSICALLY_FUSED` | Merge/quarantine only a path with editorial/consumer authority |
| 10 | Equivalent tools by consumer | six projection families and Platform parity/shim matrices | `OWNER_FUSION_VERIFIED; VARIANTS_OPEN` | Audit runtime-only variants; preserve intentional wrappers |
| 11 | Complete MAK audit | broad AST 550/550; operational AST 444/444; pip/SQLite/cron/process guards | `LOCAL_PASS_EXTERNAL_OPEN` | External providers, workers, live routes and optional runtimes remain |
| 12 | Confirmed junk/WIN | reversible quarantines; regenerable bytecode cleanup; WIN untouched | `LOCAL_CLEANUP_PASS` | Review only newly proven residue, never clean WIN as active data |
| 13 | Git branch proposal | `PHASE375_GIT_BRANCH_SYSTEM_REFRESH.md` with disjoint write sets/order | `PROPOSAL_VERIFIED` | Branch creation/merge/push still requires explicit Git operation request |

## Completion result

The objective is not complete: items 1, 3, 4, 6, 7, 9, 10 and 11 retain
scope-specific proof gaps. Items 2, 5, 8, 12 and 13 are locally verified at
their stated scope, but they do not promote the remaining gates.

Disposition: `REQUIREMENT_AUDIT_OPEN; NO_FALSE_COMPLETION`.
