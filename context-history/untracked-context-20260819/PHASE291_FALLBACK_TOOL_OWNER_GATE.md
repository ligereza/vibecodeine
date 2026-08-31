# Phase 291 — fallback tool owner and projection gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Status: `LOGICALLY_FUSED; PROJECTIONS_REQUIRED`

## Crosswalk

The same fallback helper is present at four load-bearing paths:

```text
/home/mak/flujo/cultura/mak_codex/fallback_util.py
/home/mak/flujo/cultura/mak_research/fallback_util.py
/home/mak/codex/fallback_util.py
/home/mak/research/fallback_util.py
```

All four have identical SHA-256:

```text
011560a85400dc82738cc4b595c4c8ddde6777433ee0f8aebe307a10ca290aba
```

The canonical test contract declares `cultura/mak_codex/fallback_util.py` the
source of truth and requires the Research copy to remain byte-identical. The
runtime projections are load-bearing because Codex and Research import the
helper from their department paths. The historical vibecodeine copy differs
and is not a promotion source.

## Validation

```text
tests/test_mak_salud_proveedores.py: 17 tests
tests/test_mak_fallback.py:          27 tests
result: 44 passed, PYTEST_RC=0
```

The tests cover parsing, aggregation, provider scoring, chain ordering and the
byte-identical mirror contract without making provider calls.

## Decision

This tool is fused by consumer contract: one semantic owner, one exact
department mirror, and two required runtime projections. Removing any copy by
hash alone would break hardcoded Linux runtime import paths. No file was moved,
deleted or rewritten.

## Rollback

No mutation occurred. All four original paths remain available; the existing
mirror test is the drift alarm.

## Next concrete action

Apply the same owner/projection check to the next shared tool only when its
consumer paths are explicit. Do not consolidate divergent provider or worker
variants by filename similarity.
