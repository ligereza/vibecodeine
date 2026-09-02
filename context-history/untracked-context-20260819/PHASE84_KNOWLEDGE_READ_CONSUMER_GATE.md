# Phase 84 — knowledge read consumers

## Scope

Validated the repaired repo-level namespace through three real read-only
knowledge consumers using `/home/mak/venvs/flujo/bin/flujo`.

## Foreground validation

- `flujo knowledge classify 'Evento Creamfields en Espacio Riesco, evento masivo'`
  -> exit `0`; resolved producer `creamfields`, venue `espacio_riesco`,
  mainstream preset and confidence `0.75`.
- `flujo knowledge show productora creamfields` -> exit `0`; loaded YAML
  entity with RD presence and service mode.
- `flujo knowledge show venue espacio_riesco` -> exit `0`; loaded operational
  defaults including volunteer/table/chair requirements.

## Decision

The knowledge slice is integrated for list, classify and show. It reads the
canonical local YAML base; no writes, external provider, image operation or
production delivery ran.

## Next

Continue with the remaining static dependency/entrypoint audit and preserve
the distinction between read contracts and mutating ingestion/delivery.
