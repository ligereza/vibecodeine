# Phase 292 — archive contract owner/projection gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Status: `OWNER_FUSED; COMPATIBILITY_SHIM_REQUIRED`

## Crosswalk

The implementation owner is:

```text
/home/mak/flujo/cultura/mak_plataforma/contrato_archivo.py
```

The historical runtime path is a 1,132-byte compatibility shim:

```text
/home/mak/plataforma/contrato_archivo.py
```

It dynamically loads and re-exports the canonical implementation rather than
maintaining a second 1,177-line copy. Its SHA differs by design from the
canonical file. Active consumers include the Platform hub, ISKVW archive
generator/validator, Curatoria roundtrip and laser manifest bridge.

## Validation

```text
tests/test_contrato_archivo.py:       4
tests/test_curaduria.py:              7
tests/test_curaduria_roundtrip.py:    3
tests/test_validar_curaduria.py:     15
result: 29 passed, PYTEST_RC=0
```

The test boundary is local/fixture-based; no service, provider, database,
laser hardware or external system was called.

## Decision

This is the desired tool fusion model: one semantic owner plus a thin runtime
projection that preserves a historical absolute path. Do not delete or move
the shim until every direct `/home/mak/plataforma` caller has been migrated and
the foreground compatibility gate is no longer needed.

## Rollback

No mutation occurred. The canonical implementation and compatibility shim
remain at their original paths.

## Next concrete action

Use this owner/shim pattern as the reference when reviewing the next
equivalent-tool family; prioritize a family with a thin projection rather than
divergent implementations.
