# Phase 251 — active documentation projection and safe-suite closure

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Objective

Repair only the active documentation/test contracts exposed by the bounded
post-cleanup test run. Do not change runtime routes, databases, providers,
WIN evidence or permanent services.

## Physical evidence and changes

- `/home/mak/flujo/MAPA.md` was adopted as one selected document from
  `/home/mak/WIN/flujo/MAPA.md`; its active projection now describes local
  dry-run execution and does not instruct SSH access.
- `/home/mak/flujo/CAPACIDADES.md` was adopted as one selected document from
  `/home/mak/WIN/flujo/CAPACIDADES.md`; historical remote verification is
  labeled as evidence only and does not instruct SSH access.
- `/home/mak/WIN/flujo/MAPA.md` and `/home/mak/WIN/flujo/CAPACIDADES.md` were
  not modified. The active hashes differ from WIN only because of the two
  stale-access wording corrections.
- No active repository copy of `cultura/mak_plataforma/RELEVO_MAK.md` was
  manufactured. The box-level projection exists at `/home/mak/plataforma/`
  and remains outside the canonical authoring tree; the operational test now
  treats that projection as optional rather than creating a stale duplicate.
- `tests/test_delegate_creative_director.py` accepts the current equivalent
  Spanish wording (`revisar outputs` / `revisa los outputs`).
- `tests/test_tarifa_una_sola_fuente.py` now verifies the current architecture:
  `web/src/rdBrand.ts` imports `data/rd_packs.json` and exposes
  `TARIFF.packs`; it no longer expects a removed hardcoded price fallback.
- `web/src/rdBrand.ts` itself was not changed. `data/rd_packs.json` remains the
  tariff source of truth.

## Validation

1. Targeted contract set:

   ```text
   /home/mak/research/.venv/bin/python -m pytest -q --disable-warnings \
     tests/test_delegate_creative_director.py \
     tests/test_operational_entrypoints.py \
     tests/test_tarifa_una_sola_fuente.py \
     tests/test_thing_registro.py
   ```

   Exit `0`; 28 tests passed.

2. Conservative safe suite, excluding files whose source statically mentions
   subprocess/network/systemd/cron/provider/GPU/desktop/OSC/IMAP/Instagram/
   Canva/WiFi/Resolume/pywebview and two explicitly high-risk test files:

   ```text
   SAFE_TEST_FILES=93
   SAFE_TESTS=754
   pytest -q --disable-warnings ...
   ```

   Exit `0`; all collected tests passed.

3. Active documentation check:

   ```text
   grep -nE 'SSH|ssh |192\.168\.50\.2' MAPA.md CAPACIDADES.md
   ```

   Exit `0` with no matching active-document lines. Historical WIN and other
   evidence were not rewritten.

## Risk and rollback

No runtime, database, provider, job, generated product or permanent process
was changed. The selected documents remain individually recoverable from WIN;
the test edits are reversible with a narrow inverse patch. Any removal of the
new active projections must be separately authorized and moved reversibly,
not deleted.

## Result

The safe local health gate is green. This closes the local documentation/test
contract defect without claiming the full 2,713-test inventory or any live
mutation authority.

## Next concrete action

Continue the remaining local inventory gates: identify the next active
consumer slice and verify its static/isolated behavior. Keep live RD field
ingest, live mutator POST routes, optional provider/GPU promotion and Git
branch creation deferred until explicit authority and a named rollback exist.
