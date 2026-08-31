# Phase 211 — review-surface consumer audit

Date: 2026-08-15 (America/Santiago)

## Findings

| Surface | Evidence | Decision |
|---|---|---|
| `/home/mak/flujo-deploy` | Bounded filesystem `diff -qr` against `/home/mak/flujo` returned exit 1 with 498 difference records. `/home/mak/bin/mak_sync_safe.py` explicitly consumes it as the disposable deploy origin and synchronizes projections from it. | `KEEP_EXTERNAL_DEPLOY_OWNER`; not duplicate junk and not safe to merge with the human checkout. No Git command was used as inventory and the sync script was not executed. |
| `/home/mak/lenguaje` | Active references in `cultura/mak_plataforma/crontab.mak`, `cultura/mak_plataforma/roles.py` and `cultura/mak_lenguaje/*`; executable `cron_lexicon.sh`, `hook_barrido.py` and `lenguaje_lib.py` plus dictionaries exist. | `KEEP_DEPARTMENT_SURFACE`; it is a real Spanish-language consumer, even though the documented cron lines are paused. Do not fold it into a generic tools folder. |
| `/home/mak/bucle` | No bounded active-code/launcher reference found. It has its own `.git` directory and artwork (`ALLTO.svg`, PNGs, license), so it is a cultural source/project, not an unowned cache. | `KEEP_SOURCE_UNRESOLVED`; preserve provenance and leave outside runtime fusion. |
| `/home/mak/workspace` | Contains `tools/doc_parser` and `tools/simple_doc_parser`; no bounded active-code/launcher reference found. | `REVIEW_SOURCE_TOOLS`; do not delete or merge until their intended document consumers are mapped. |
| `/home/mak/curatoria_encolado` | Empty at depth 1; no bounded consumer reference found. | `EMPTY_STAGING_CANDIDATE`; path-specific quarantine/removal may be considered later, but no action without explicit cleanup gate. |
| `/home/mak/plataforma` | Numerous active Research/platform references target its ledgers, ideas, memory and state paths; only `interfaz.py` was isolated as a legacy UI candidate. | `KEEP_MIXED_SURFACE`; never quarantine the directory as a whole. |

## Validation record

- Reference searches were bounded to canonical source, culture, units,
  launchers, language and selected scripts; no whole-tree copy occurred.
- The deploy comparison used filesystem `diff -qr`, not Git inventory. Exit 1
  means content/name differences were found; the output contained 498 records.
- `workspace` and `curatoria_encolado` were inspected without writing them;
  `curatoria_encolado` has zero entries at depth 1.
- No cron, deploy sync, provider, service or external automation was run.

## Decision

No additional root surface qualifies as confirmed junk. The one empty staging
directory and the old platform UI remain path-specific candidates, but the
cleanup gate is not yet satisfied for either. The architecture is now grounded
in consumers rather than names or sizes.

## Next concrete action

Close the remaining functional gates: static dependency/runtime matrix for the
language and deploy consumers, then a read-only route audit for RD field-data
and mutation boundaries. Keep field data empty, mutators deferred, and all
protected/history surfaces untouched.

