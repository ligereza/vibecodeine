# Phase 67 — contrato_archivo projection parity gate

## Slice

`/home/mak/flujo/cultura/mak_plataforma/contrato_archivo.py` is the canonical
pure contract layer and `/home/mak/plataforma/contrato_archivo.py` is an exact
projection. The hub calls its portfolio metadata, identity graph, scene,
portfolio item and public substrate functions; `entregar_micelio.py` calls its
graph conversion.

## Validation

- `cmp -s` source/projection: exit 0.
- AST parsing of both files: exit 0.
- Fixture `desde_portfolio_item` returned schema `faro-portfolio-entity-v1`,
  next action `triangulate` and a true human publication gate for a private
  candidate.
- Empty and missing IDs raised `ValueError` without filesystem or network
  access.
- Consumer references were found in the FLUJO hub, laser adapter and micelio
  delivery path.

## Decision

This slice is `PROJECTION_PARITY_VERIFIED`; no merge edit is required. Keep
the source as canonical and the root file as a protected projection until the
global projection mechanism is replaced by a bounded ownership contract.
Generated malformed Codex pieces and the unrelated incomplete panel remain
separate audit items.
