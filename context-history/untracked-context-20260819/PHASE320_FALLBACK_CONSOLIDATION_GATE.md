# Phase 320 — fallback utility consolidation gate

Date: 2026-08-15 (America/Santiago)
Scope: one equivalent pure utility family across Research and Codex.

## Paths and consumers

The same 6,100-byte implementation exists at:

- `/home/mak/flujo/cultura/mak_research/fallback_util.py`
- `/home/mak/research/fallback_util.py`
- `/home/mak/flujo/cultura/mak_codex/fallback_util.py`
- `/home/mak/codex/fallback_util.py`

Research's `expulsion.py` consumes `score_provider_health()` through its flat
`/home/mak/research` path. Codex's `codex_lib.py` consumes the same utility
through its flat `/home/mak/codex` deployment path. The cultural copies are
the authoring projections; the root copies satisfy direct-deployment imports.

## Foreground contract gate

Command:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/mak/flujo/cultura/mak_research:/home/mak/flujo/cultura/mak_codex:/home/mak/research:/home/mak/codex python3 - <<'PY'
... AST/SHA equality and pure fallback fixtures ...
PY
```

Result: exit code 0. All four files parse and have SHA-256
`011560a85400dc82738cc4b595c4c8ddde6777433ee0f8aebe307a10ca290aba`.
Fixtures passed timeout/HTTP error classification, failure aggregation,
provider scoring and chain reordering. The gate reported
`network_calls=False writes=False`; no provider, worker or service ran.

## Disposition

`CONSOLIDATE_SEMANTIC_OWNER_KEEP_FLAT_PROJECTIONS`.

This is a genuine equivalent-tool family, but physical deletion of three paths
would break direct flat deployment contracts and the existing drift ratchet.
The semantic owner should remain one reviewed implementation under the Codex
department contract, while the Research and root copies remain explicit,
hash-checked projections until a package/import-root migration is separately
validated. This phase therefore records the fusion decision without changing
files.

## Changes and risks

- Source/data changes: none.
- Network/providers/services/cron/Git/WIN: untouched.
- Risk: a future central import must update both root launchers and the mirror
  test together; uncoordinated deletion would cause `ImportError` in flat
  deployments.
- Rollback: no rollback needed because no file changed. Before a future edit,
  preserve the four hashes and add a foreground import test for both consumers.

