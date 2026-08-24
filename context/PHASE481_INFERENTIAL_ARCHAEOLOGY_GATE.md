# Phase 481 — Inferential archaeology read-only gate

## Decision

Promote the existing archaeology tool as a local read-only utility. Do not
scan real Codex/Claude session roots during integration and do not use its
default output directory against live state.

## Physical source and target

- Source: /home/mak/WIN/flujo/tools/inferential_archaeology.py
- Source tests: /home/mak/WIN/flujo/tests/test_inferential_archaeology.py
- Target: /home/mak/flujo/tools/inferential_archaeology.py
- Target tests: /home/mak/flujo/tests/test_inferential_archaeology.py

The two target files are byte-identical to their physical WIN sources:

- tools/inferential_archaeology.py SHA-256
  806ac9116f27a754cfd547d7047de9abfb1e74bcdd29db3a09dc7f45ebf5d08c
- tests/test_inferential_archaeology.py SHA-256
  c21d48d12ddd4449bb5633194dfafcee30c4419d2502306761a9845b4f0737a8

## Foreground evidence

The command paths below are normalized to the current canonical checkout;
the pass counts and exit codes are historical evidence from this phase.

1. Offline physical-source gate:

   PYTHONPATH=/home/mak/WIN/flujo /home/mak/flujo/.venv/bin/pytest -q /home/mak/WIN/flujo/tests/test_inferential_archaeology.py

   Result: 27 passed, exit 0.

2. Active-tree focused regression:

   PYTHONPATH=src:. /home/mak/flujo/.venv/bin/pytest -q tests/test_inferential_archaeology.py tests/test_source_pipeline.py tests/test_three_plane_manifest.py tests/test_knowledge_reconciliation.py

   Result: 67 passed, exit 0.

3. Syntax gate:

   python3 -m py_compile tools/inferential_archaeology.py src/flujo/knowledge/three_plane.py src/flujo/knowledge/reconciliation.py cultura/mak_research/fondart_corpus.py cultura/mak_research/source_pipeline.py

   Result: exit 0.

## Consumer and dependencies

The tool consumes explicitly supplied evidence roots and can index structured
events, source text and proposal/idea queues. Its imports are standard Python
library modules; DuckDB remains optional and is not made a required runtime
dependency by this promotion. The immediate consumer is MAK research/context
reconciliation, not the FLUJO HTTP hub.

## Safety boundary

The CLI defaults reference real session roots and a live output location.
Those defaults were not executed. No network, external provider, session store,
SQLite source database, or runtime service was touched. sync_mak_safe.py remains
archived because it has an explicit apply/mutator path; postgres_* remains
archived because MAK's verified authority is SQLite and no writer was
authorized.

## Rollback

Rollback is a Git revert of the bounded archaeology commit or removal of the
two added files from the active tree; the exact WIN source and remote archive
tags remain untouched.
