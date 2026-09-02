# Phase 276 — vibecodeine snapshot gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Finding

`/home/mak/vibecodeine` is not a single loose tool. It is a 440 MB historical
FLUJO repository/snapshot containing source, tests, docs, data, SVG, web,
department projections, scripts and its own `.venv`. Its README identifies
FLUJO as the main program and documents a Windows-first historical operating
model. No active canonical source, tool, test, data or department reference to
the absolute path `/home/mak/vibecodeine` was found.

## Crosswalk evidence

The bounded comparison covered matching relative files under `src`, `cultura`,
`tools`, `tests`, `scripts`, `data`, `svg`, `docs` and `web`. It excluded
`.git`, `.venv`, caches, `node_modules`, build and generated files over 2 MB.

```text
vibecodeine selected files: 844
flujo selected files:      998
same relative paths:       792
byte-identical paths:      635
divergent paths:           157
```

The identical sample includes canonical department files such as
`cultura/mak_lenguaje/*`, while divergent paths include Codex, Curatoria and
Platform workers, services, fallbacks, scripts and contracts. Therefore a
filename/hash scan cannot decide which snapshot path is the owner.

## Disposition

Keep `/home/mak/vibecodeine` intact as a historical/source snapshot for now.
It is not an active MAK runtime projection, not a dependency source and not
confirmed junk. Do not copy it into FLUJO, run its `start.sh`, launch its
server/creative tools, install its requirements, or delete it based on size or
overlap.

The correct future operation is a family-level crosswalk:

1. compare each divergent department/tool family with its active FLUJO owner;
2. classify historical-only, active replacement, missing feature and
   incompatible platform behavior;
3. promote only a named missing slice with a consumer and foreground fixture;
4. quarantine a historical duplicate only after all references, provenance,
   rollback and protected outputs are recorded.

## Safety

No file, service, environment, database, provider, WIN content or Git state
changed. No code from the snapshot was executed.

## Next concrete action

Build the first bounded divergence report for `vibecodeine/src` versus the
active `/home/mak/flujo/src`, prioritizing files with active MAK consumers and
keeping Windows launchers, workers, providers and XIO gated.
