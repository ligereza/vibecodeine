# Phase 162 — objective reconciliation after platform projections

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

The platform projection family was reconciled after Phases 156–161. The
physical source remains `/home/mak/flujo/cultura/mak_plataforma`; runtime
projections under `/home/mak/plataforma` now point to it for material, latido,
vigilar_red, backup and watchdog. Each previous exact runtime file has a
separate quarantine rollback. No cron entry was enabled.

| Objective | Current status | Evidence / open gate |
|---|---|---|
| RD field data | DEFERRED_EMPTY_DATA | `rd_datos.db` remains empty; no invented records |
| RD database | VERIFIED_READONLY_SOURCE_RECONCILED | `rd.db` read paths and metadata preserved |
| RD mutators | DEFERRED_AUTHORITY | no upload/provider/write route called |
| FLUJO automation | FIXTURE_VERIFIED | local EVENTO fixture passed; external bridge gated |
| Non-serve CLI | VERIFIED_READONLY | version/health/doctor/RD commands passed |
| RD assets | CANONICAL_GENERATOR_VERIFIED_PARTIAL | JSON/SVG promoted; PDF renderer unavailable |
| Dependencies | RUNTIME_PARTIAL | global Windows conflicts not copied to requirements |
| Folder architecture | PARTIAL_CLASSIFIED | platform projections consolidated; other departments open |
| Duplicate documents | PARTIAL_CLASSIFIED | exact hashes classified by role; no evidence deletion |
| Equivalent tools | PARTIAL_CONSOLIDATED | tariff, issue bridge and platform wrappers merged |
| MAK audit | IN_PROGRESS | research/curatoria/codex/vigia surfaces remain |
| Junk removal | REVERSIBLE_ONLY | stale generated outputs quarantined; WIN/evidence preserved |
| Git branches | PROPOSED_NOT_APPLIED | branch system waits for physical integration gates |

## Next action

Move to the next active department, starting with the physical research pair.
Verify the existing `/home/mak/research/research.py` projection and its real
`--help` contract without starting the research service or making provider
calls. Then select the smallest unresolved research consumer.
