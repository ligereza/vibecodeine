# Phase 120 - research sources projection merge

## Scope and ownership

`/home/mak/flujo/cultura/mak_research/fuentes.py` is the semantic owner of
the primary-source quality gate. It is consumed by the RD/research path and
the refutation tests. `/home/mak/research/fuentes.py` differed only in a
comment and had no separate active contract.

## Change

Replaced only `/home/mak/research/fuentes.py` with a compatibility projection
to the canonical source-quality gate. WIN and all research corpus/evidence
trees were untouched. No network lookup, report generation, database write or
provider call ran.

## Foreground validation

The canonical venv ran pure isolated imports for both paths and compiled both
files with exit 0. For the same fixtures, both variants returned:

- primary `bcn.cl` URL for `cl_legal`: `hay_primaria=True`, domain `cl_legal`;
- non-primary `example.com` URL: `hay_primaria=False`, domain `cl_legal`.

The root projection and canonical module exposed the same `__all__` symbols.

## Decision and risk

`MERGE_NOW`: yes. One semantic owner now serves both active MAK paths. The
bridge intentionally does not fetch sources or alter the quality policy. Any
future legal/research policy change must be made in the canonical module and
then validated through its consumers.

## Next action

Audit the remaining root/canonical differences, prioritizing pure modules with
confirmed consumers. Keep `entregar_micelio.py` separate because its command
can use network, write logs/data and invoke Git; do not run it in this phase.
