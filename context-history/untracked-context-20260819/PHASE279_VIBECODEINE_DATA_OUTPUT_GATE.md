# Phase 279 — vibecodeine data/output crosswalk

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Bounded data comparison

Compared small declarative files under `data`, `schemas`, `jobs`, `knowledge`,
`linea_editorial`, `context` and `out`. Context evidence was treated
separately from application data because the active MAK handoff/history has
grown beyond the snapshot.

```text
snapshot selected files: 118
active selected files:   835
common paths:            117
byte-identical:          111
divergent:               6
snapshot-only:           1 (context/README.md)
active-only:             718 (mostly current phase evidence/context)
snapshot JSON parsed:    53/53 valid
active JSON parsed:      64/64 valid
```

The six divergences are four generated context HTML/command manifests,
`linea_editorial/v4.1.md` and `out/works.json`. They are current-owner or
generated-state decisions, not missing snapshot features.

## Protected generated products

Both `/home/mak/vibecodeine/datadrops` and `/home/mak/flujo/datadrops` contain
19 files in the same named output families, including PDFs, PNGs, HTML, SVG,
Markdown, manifests and original inputs. This establishes shared product
provenance, not deletion authority. Generated products, source media and
manifests remain protected; no full-media comparison or copy was performed.

## Decision

The snapshot data/configuration is historical reference; active FLUJO owns
current context, catalogs and generated state. No data file, generated product,
schema, media, database or snapshot path was moved, overwritten or deleted.
The vibecodeine snapshot gate is now complete enough to block accidental
whole-tree fusion while preserving a future per-family provenance review.

No service, provider, worker, renderer, external system, WIN content or Git
state changed.

## Next concrete action

Audit `/home/mak/flujo-deploy` and `/home/mak/bin/mak_sync_safe.py` statically as
an external deployment surface. Verify its references and shell/Python syntax,
but do not deploy, sync, copy trees, use Git or start services.
