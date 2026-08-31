# Phase 299 — tandas evidence fixture gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none  
Status: `FIXTURE_CONTRACT_REPAIRED`

## Finding and action

The three failing `tool_archaeology` tests declared
`tools/contexto_repo.py` as evidence but never created or supplied that path
to `run_external_batch`. The production contract correctly rejects unknown
evidence when `strict_product=True`.

Changed only `/home/mak/flujo/tests/test_mak_tandas.py`: each affected test
now creates a temporary `contexto_repo.py` fixture and passes it through the
existing `paths` allow-list. `validate_evidence_paths` and all production
source remain unchanged.

## Validation

| Command | Exit | Result |
|---|---:|---|
| `PYTHONPATH=/home/mak/flujo ... pytest -q tests/test_mak_tandas.py` | 0 | 49 tests pass |
| previous failing strict evidence cases | 0 | accepted with real temporary evidence |

Writes are confined to pytest `tmp_path` fixtures and are automatically
cleaned by the test framework. No provider, network, database, service,
worker, scheduler, XIO, n8n, Git or WIN state was touched.

## Decision and next

Keep the strict evidence gate. The test/contract discrepancy is closed by
making the fixture truthful, not by allowing invented paths. Next, audit the
remaining runtime network monitor family beginning with
`/home/mak/flujo/cultura/mak_plataforma/vigilar_red.py` and its root consumer;
do not execute network actions or start the scheduler.
