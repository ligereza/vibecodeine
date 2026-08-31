# Phase 18 — candidate history matrix

Identity: LUNA

## Objective

Cross the 33 LIVE/ADOPTABLE candidate rows from PHASE15 with the historical
orientation in historia git.odt. Deduplicate physical paths while preserving
how many source reports referenced each path. This matrix decides what deserves
the next contract review; it does not promote, merge, delete or revive code.

## Evidence

- Five phase-17 trace reports were validated.
- Trace input rows: 61.
- Unique physical paths: 32.
- The extra rows are intentional: source/runtime pairs and the duplicate
  ledger.py candidate from PHASE13 are preserved in trace_rows and source
  reports.
- History is inferred orientation only. Branch names, commit subjects and
  shared tips are not user decisions or proof of current runtime.
- PHASE16 explicitly overrides ledger.py and visual_index.py to NO_CHANGE.

## Consolidated decision

| Final decision | Unique paths | Meaning |
|---|---:|---|
| KEEP_CANDIDATE | 23 | Survives historical screening; still needs current contract review |
| DEFER | 5 | History or physical evidence requires fixture, dependency or owner clarification |
| NO_CHANGE | 4 | ledger.py and visual_index.py source/runtime paths after PHASE16 |
| **Total** | **32** | Deduplicated physical candidate paths |

The original 33 candidate rows therefore reduce to 23 paths worth a next
contract review, 5 deferred paths and 4 paths explicitly held at no_change.
This is not an integration count.

## Interpretation

- The platform core and flujo core mostly have broad historical touch across
  refs, but this means repeated development, not proof that every generation
  should survive.
- providers.py remains a candidate surface; tandas.py is deferred until an
  isolated fixture and Debian 12 contract exist.
- ledger.py and visual_index.py have real consumers but remain no_change:
  their write boundaries and visual dependencies are not safely verified.
- scripts/piezas_generar.py is deferred because its historical lineage and
  current operational contract are insufficient.
- Runtime paths with no exact historical path are not automatically obsolete;
  they require physical consumer and owner evidence.

## Next action

Choose the smallest KEEP_CANDIDATE group with high or medium history
confidence and a shared current owner/consumer. Verify its physical contract,
dependencies, side effects and rollback in foreground. A candidate can still
be downgraded to DEFER or NO_CHANGE. No Git branch operation is authorized.

## Validation

- CSV: 32 unique rows, 21 columns, exact derived fields.
- CSV SHA-256:
  d765e3b58783376a9b62a3b994b88150349b721ea1cf3ec1258a66be9d488316
- Source/runtime/WIN, Git state, services and artwork were not modified.

## Last checkpoint

2026-08-14 America/Santiago — all 33 candidate rows traced against historical
orientation; 23 unique paths remain for contract review.
