# Phase 198 — current MAK integration objective matrix

Status: `RECONCILED; WORK_REMAINS`

| # | Objective | Current state | Evidence/next gate |
|---:|---|---|---|
| 1 | RD field data | `DEFERRED_EMPTY_DATA` | `rd_datos.db` is valid but 0 rows; no real field ingest authority |
| 2 | RD database relation | `SEPARATED_BY_ROLE` | `rd.db` catalog and `rd_datos.db` field data must not be merged blindly |
| 3 | RD mutating routes | `DEFERRED_MUTATION` | Read-only catalog/summary and quote/plano gates pass; mutators need explicit bounded authority |
| 4 | FLUJO automations | `PAUSED_AND_CLASSIFIED` | Issue URL flow is user-confirmed; installed crontab is paused; no enablement |
| 5 | Non-serve FLUJO commands | `PARTIAL_PASS` | CLI/compile/fixture gates pass; remaining commands need consumer-specific checks |
| 6 | RD assets | `INDEX_GATE_PASS` | 1,742 regular files reconcile to local index; duplicate roles remain open |
| 7 | Dependencies | `SLICE_SCOPED` | Pillow declaration fixed; global pip conflicts not requirements; MobileCLIP external and GPU-deferred |
| 8 | Final folder architecture | `PROPOSED` | Phase 188 map recorded; no moves yet |
| 9 | Duplicate documents | `LEDGER_STARTED` | Research family ledger complete; platform/RD families remain |
| 10 | Equivalent tools | `OWNER_FUSED_PARTIAL` | Research/Codex canonical + runtime projections; platform extras remain classified |
| 11 | Full MAK audit | `IN_PROGRESS` | Top-level and major departments audited; no final cleanup sign-off |
| 12 | Remove confirmed junk | `NOT_STARTED_BY_DESIGN` | No deletion/quarantine without role/hash/consumer/rollback ledger |
| 13 | New Git branch system | `DEFERRED` | Must follow stable house architecture; no Git inventory/mutation yet |

## Completed evidence in this run

Phases 179–197 added RD asset crosswalk/reconciliation, RD index fixture,
apps/src consumer gate, Research wrapper path fix, optional qwen-agent gate,
platform extras/UI crosswalk, folder architecture proposal, Research/Codex
role matrices, coherence/roles/health projection gates and the current
top-level/launcher audits. Every write was a report or an explicitly scoped
runtime compatibility fix; no evidence tree was deleted.

## Remaining order

1. Finish duplicate-role ledgers for platform and selected RD/document family.
2. Pick one safe, reversible projection/quarantine candidate only after its
   launcher and consumer are proven.
3. Revalidate the full local command/fixture gate after any such change.
4. Review RD mutators and field-data authority separately; do not infer real
   data from demo/evidence.
5. Produce final folder cleanup ledger and visual progress summary.
6. Only then propose Git branch structure; do not create branches now.
