# Phase 165 — research derived reads gate

Date: 2026-08-15
Owner: LUNA-PRINCIPAL

## Scope

The next data-bound research consumers were selected:

- `/home/mak/research/indice.py` -> `informes/INDEX.md` and `paneles/INDEX.md`
- `/home/mak/research/digest.py` -> `informes/DIGEST.md`

Their canonical files live under `/home/mak/flujo/cultura/mak_research/` and
are byte-identical to the runtime files.

## Result

Both source/runtime pairs compiled. Independent temporary fixtures produced
exit `0` and byte-identical index/digest outputs for source and runtime. The
real research folders and derived documents were not rewritten. No provider,
network, service or persistent process was used.

## Decision

Keep these exact copies separate for now: each binds its `ROOT` to its owning
department data. A wrapper would silently redirect output to the canonical
tree and violate the data-owner contract. The next candidate must be a
consumer with a path-independent contract or an explicitly designed data-root
parameter.
