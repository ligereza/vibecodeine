# Phase 117 - objective reconciliation

This is the current closeout view of the 13 integration objectives. It
supersedes the older Phase 93 snapshot while preserving every open boundary.

## Verification snapshot

- `/home/mak/venvs/flujo/bin/flujo verify --no-pytest`: exit 0; compile/health,
  version checks and temporary hub smoke passed.
- The temporary hub smoke reported HTTP-ready startup and was cleaned up; no
  Flujo serve, worker, provider, Ollama or SSH process remains.
- Canonical venv probes: `pytest=False`, `qwen_agent=False`.
- Web runtime: Node `v18.20.4`; Vite declares `>=20.19`; native Rollup module
  is absent. No package installation was attempted.
- `/home/mak/flujo/src/flujo/plataforma/tandas.py` and
  `/home/mak/plataforma/tandas.py` are currently the same projection; the
  historical variant is `/home/mak/WIN/flujo/cultura/mak_plataforma/tandas.py`.

## Current objective matrix

| # | Objective | Evidence | Status | Next concrete action |
|---:|---|---|---|---|
| 1 | RD field data | `data/rd_datos.db` remains empty; truthful empty-data report | DEFERRED_EMPTY_DATA | Receive and authorize a real field dataset and acta |
| 2 | Merge `rd.db` | Additive merge, backup, integrity checks and read-only API gate | VERIFIED | Preserve provenance; no further merge without new source |
| 3 | RD mutating routes | Disposable fixtures, HTTP contracts and rollback gates | FIXTURE_VERIFIED_WITH_ROLLBACK | Authorized foreground production run only |
| 4 | FLUJO automation | `EVENTO ...` email -> issue -> URL -> processing contract; local dry-run | DRYRUN_VERIFIED_CONTRACT_ACCEPTED | Provider-backed run only with explicit authorization |
| 5 | Non-serve CLI | Venv launcher, readers, `verify --no-pytest`, autonomy local dry-run | RUNTIME_VERIFIED_PARTIAL | Re-run full test gate if pytest becomes available |
| 6 | RD assets | Crosswalk, route adapter and temporary indexer | CLASSIFIED_PARTIAL | Assign human deliverable/output ownership |
| 7 | Dependencies by slice | Core imports and pip check pass; web gate recorded | CORE_VERIFIED_WEB_BLOCKED | Use supported Node and native Rollup dependency |
| 8 | MAK folder architecture | Canonical ownership and projection policy | DESIGNED_PROJECTION_OWNERSHIP | Finish ownership map before moves |
| 9 | Duplicate documents | Exact-hash crosswalk; safe POST duplicate removed; evidence protected | PARTIAL_CONSOLIDATED | Inspect semantic candidates by consumer and provenance |
| 10 | Equivalent tools | Consumer-backed root projections across research, codex, curatoria and platform | PARTIAL_VERIFIED | Reconcile `tandas.py` evidence/payload fork |
| 11 | Full MAK audit | `/home/mak/*` department slices plus health/verify/static gates | RUNTIME_PARTIAL | Close remaining department and dependency gates |
| 12 | Cleanup with WIN historical | 485 cache files and one confirmed root duplicate removed; WIN untouched | PARTIAL_CONFIRMED | Re-audit only path-level confirmed junk |
| 13 | Git branch system | Branch proposal exists; no Git operation applied | PROPOSED_NOT_APPLIED | Apply after ownership and cleanup closure |

## Guardrails carried forward

`/home/mak/WIN` remains historical evidence. Empty databases, demo/evidence
fixtures, generated products, logs, ledgers, credentials, provider calls and
mutating routes remain protected. This phase changes only this reconciliation
report and its CSV companion.

## Next block

First reconcile `tandas.py` as a semantic fork: identify the active evidence
manifest owner and the external payload owner with pure fixtures only. Then
run the remaining read-only department gates, update the objective matrix and
only after that review path-level cleanup candidates. Do not install pytest,
qwen_agent or web dependencies without explicit authority.
