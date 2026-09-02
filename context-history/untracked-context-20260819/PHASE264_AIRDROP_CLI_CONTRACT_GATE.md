# Phase 264 — airdrop/CLI/contract fixture gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Validate local contracts with temporary roots:

- `tests/test_airdrop.py`
- `tests/test_airdrop_signing.py`
- `tests/test_cli_smoke.py`
- `tests/test_cron_state_atomic.py`
- `tests/test_cultura_sin_automerge.py`
- `tests/test_contrato_archivo.py`
- `tests/test_gen_archivo_iskvw.py`
- `tests/test_index_db.py`

The airdrop tests simulate scan/sign/verify/apply/rollback only inside
`tmp_path`; they do not apply an airdrop to MAK. CLI smoke monkeypatches
subprocess, and the snapshot/index tests redirect all data to temporary roots.
The autonomy test group, including its historical SSH contract, was not run.

## Validation

```text
pytest -q --disable-warnings \
  tests/test_airdrop.py tests/test_airdrop_signing.py \
  tests/test_cli_smoke.py tests/test_cron_state_atomic.py \
  tests/test_cultura_sin_automerge.py tests/test_contrato_archivo.py \
  tests/test_gen_archivo_iskvw.py tests/test_index_db.py
exit 0; 68 tests passed
```

## Result

The local airdrop contracts, signed artifact gate, CLI smoke surface, atomic
state writes, shared file contract, micelio snapshot fallback and flyer index
pass in isolated fixtures. No active source, database, job, service, cron,
Git, SSH or external state changed.

## Risk and rollback

No persistent state changed; no rollback is needed. Airdrop application to the
real tree, autonomy execution and historical SSH surfaces remain deferred.

## Next concrete action

Continue with the remaining keyword/fixture candidates, prioritizing pure
source/configuration and temporary index/data tests; keep autonomy, workers,
providers, XIO, n8n and live mutators excluded.
