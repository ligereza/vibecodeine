# Phase 298 — roles and scheduler projection gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none  
Status: `PROJECTIONS_VALIDATED_SCHEDULER_PAUSED_WITH_TEST_FIXTURE_OPEN`

## Scope and finding

- canonical policy: `/home/mak/flujo/cultura/mak_plataforma/roles.py`
- runtime policy projection: `/home/mak/plataforma/roles.py`
- canonical runner: `/home/mak/flujo/cultura/mak_plataforma/trabajo.py`
- runtime runner projection: `/home/mak/plataforma/trabajo.py`
- scheduler template: `/home/mak/flujo/cultura/mak_plataforma/crontab.mak`

Both root Python files are existing canonical shims. `roles.MODULOS` points at
the intentional runtime paths, and `trabajo.main` remains importable through
the projection. The template contains dormant declarations, but the installed
user crontab has zero active non-comment entries. All five MAK user units are
inactive and disabled/static as previously recorded. No scheduler was
re-enabled.

## Foreground validation

| Command | Exit | Result |
|---|---:|---|
| `python3 -m py_compile` roles/trabajo canonical and runtime | 0 | all parse |
| `PYTHONPATH=/home/mak/flujo ... pytest` backlog + maintenance | 0 | 75 tests pass |
| root import of `roles` and `trabajo` | 0 | policy and runner entrypoint pass |
| `crontab -l` active non-comment count | 0 | `active_cron_entries=0` |
| `systemctl --user is-active` five MAK units | 0 | all reported inactive |

The broader tanda batch exposed three existing test failures, not a scheduler
failure. Each expected `accepted` while strict evidence validation returned
`revise` for the nonexistent evidence path `tools/contexto_repo.py`:

- `test_run_external_batch_persists_raw_and_ingests`
- `test_run_external_batch_repairs_product_once`
- `test_product_repair_preserves_work_identity`

The safe behavior is to keep rejecting missing evidence. The next action is a
fixture/contract repair that supplies a real temporary evidence file or updates
the expected verdict; do not weaken `validate_evidence_paths`.

## Decision and next

Keep the roles/trabajo projections and leave scheduler declarations dormant.
The next executable slice is the bounded `tandas` strict-product fixture gate:
reproduce the three failures with temporary evidence only, decide whether the
tests or implementation contract is stale, and make the smallest test/source
repair with foreground validation. No external provider, worker, service,
cron, live issue bridge or mutating route is required.
