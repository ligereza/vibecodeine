# Phase 315 — curatoria diagnostic projection gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Status: `EXACT_PROJECTION_VERIFIED`

## Candidate

```text
canonical:  /home/mak/flujo/cultura/mak_curatoria/diagnostico_proyectos.py
projection: /home/mak/curatoria/diagnostico_proyectos.py
```

Both files are 47,621 bytes and byte-identical. The canonical module is
consumed by `mak_conductor/handler_registry.py`, `producer_catalog.py` and
platform coherence checks; the root path preserves direct department CLI use.
The module diagnoses creative project families and writes only when its
explicit SQLite/output entrypoint is invoked; the tested pure functions do
not write.

## Foreground validation

```text
cmp/hash source and projection: exit 0; exact parity
AST parse of both modules: exit 0
root direct CLI --help: exit 0; arguments rendered
normalize/dir_is_generated fixture parity: PASS
validate_organism_plan fixture parity: PASS
cron active entries: 0
matching provider/Blender/service processes: none
```

An exploratory check that asserted function object identity across two separate
module loads returned an assertion failure; that assertion was invalid because
distinct module loads necessarily create distinct Python objects. The
behavioral parity check above was rerun and passed. No source or runtime state
changed.

## Decision

Mark this family `CONSOLIDATE` as one canonical implementation plus a retained
exact compatibility projection. No move, delete or wrapper rewrite is needed.
The projection remains protected until direct department launchers are
retired or explicitly redirected.

## Rollback and next

No file changed; rollback is the unchanged root projection. Continue with the
next exact consumer-backed curatoria family (`triangular.py`) only after its
entrypoint and write set are independently checked. Keep database mutations,
creative outputs, providers, services, Git and WIN gated.
