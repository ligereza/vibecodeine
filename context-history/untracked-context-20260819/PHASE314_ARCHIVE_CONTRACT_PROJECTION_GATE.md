# Phase 314 — archive contract projection fusion gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Status: `CONSOLIDATED_CANONICAL_WITH_COMPATIBILITY_PROJECTION`

## Candidate

The named exact-family candidate is:

```text
owner:      /home/mak/flujo/cultura/mak_plataforma/contrato_archivo.py
projection: /home/mak/plataforma/contrato_archivo.py
```

The owner is the 1177-line pure archive contract used by the FLUJO hub,
micelio delivery and laser/archive adapters. The root file is an intentional
35-line importlib projection that preserves historical direct entrypoints.
It is not a competing implementation and is not a deletion target.

## Foreground validation

```text
SHA comparison: divergent by design (full implementation vs 35-line wrapper)
root direct import with sys.path=/home/mak/plataforma: PASS
canonical/root symbol parity (schema, desde_portfolio_item, desde_laser,
  convertir, sustrato_publico): PASS
portfolio fixture on both paths: same faro-portfolio-entity-v1/demo result
laser fixture on both paths: equal result
AST/import side effects: none; PYTHONDONTWRITEBYTECODE=1
cron active entries: 0
matching service/provider processes: none
```

Active consumers include `cultura/mak_plataforma/hub.py`,
`entregar_micelio.py`, `flujo/src/flujo/laser.py` documentation and the root
direct-entrypoint surface. The contract is standard-library-only and pure for
the tested adapters; it does not write databases, assets, logs or outputs in
these fixtures.

## Decision

Mark this family `CONSOLIDATE` at the ownership level, already implemented:
canonical implementation stays in FLUJO, root projection stays as a bounded
compatibility surface. Do not replace it with a duplicate copy or remove the
projection until every direct root launcher has migrated.

## Rollback and impact

No file changed in this phase. Rollback is the current wrapper at
`/home/mak/plataforma/contrato_archivo.py`; if a legacy direct caller fails,
restore only that bounded wrapper from its recorded source/projection pair and
rerun the fixture. Databases, media, evidence, WIN and Git were untouched.

## Next action

Use the same gate on the next unresolved duplicate family with a real
consumer, starting with a bounded document/tool manifest rather than another
whole-tree scan. Keep exact evidence duplicates protected when provenance or
human output semantics differ.
