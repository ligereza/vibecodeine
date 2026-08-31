# Phase 442 — laser toolchain owner gate

## Scope

This slice connects the laser reference HTML, the shared CLI and the pure
Python ILDA route. It belongs to the VJ/technical department and feeds
portfolio laser material; it is separate from RD venues, the portfolio venue
viewer and the sala3d portfolio artifact.

## Owner chain

- Human-facing reference: `docs/laser/toolkit.html`.
- Routing/index document: `docs/laser/TOOLKIT_INDICE.md`.
- Runtime module: `src/flujo/laser.py`.
- CLI group: `python3 -m flujo laser`, registered in `src/flujo/cli.py`.
- Portfolio archive join: `cultura/mak_plataforma/contrato_archivo.py` via
  media-id links in `laser.lote`.
- Optional external path: `vpype`, `hatched` and `flow_img`; not required for
  measurement or direct ILDA export.

## Consolidation performed

`docs/laser/TOOLKIT_INDICE.md` had a stale filename reference
(`laser-toolkit.html`). It now points to the real owner
`docs/laser/toolkit.html`. No laser HTML, SVG, ILDA, database or historical
copy was deleted or rewritten.

## Foreground validation

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile src/flujo/laser.py src/flujo/cli.py
exit 0

PYTHONPATH=src python3 -m flujo laser --help
exit 0 — states, hatched, flow, lote, medir and ild are registered

Focused pure-Python runtime check in a temporary directory
exit 0 — 5 SVG vertices measured across 2 strokes; ILDA Type 5 RGB written,
read back, color order verified, blanking/dwell verified and bytes deterministic
```

The optional dependency probe returned
`{'vpype': False, 'hatched': False, 'flow': False}`. This is not a blocker for
the direct `medir` and `ild` paths, but it gates image-to-vector `hatched`,
`flow` and `lote` modes until the declared external tools are deliberately
installed. No package was installed and no real material folder was processed.

## Disposition

The native ILDA route is integrated at the source/CLI contract level: it emits
format 5 true-color records, re-reads the file and reports its point budget.
The portfolio join exists but remains unexecuted against real media in this
phase. The laser reference remains a human-facing dossier with external links,
not a dependency manifest or proof that every external tool is installed.

Disposition: `LASER_ILDA_NATIVE_ROUTE_GREEN; CLI_OWNER_CONFIRMED; VPIPE_OPTIONAL_UNAVAILABLE; NO_REAL_MEDIA_MUTATION`.

Next action: inspect the next active tool/HTML owner from the physical MAK
surface, prioritizing unresolved RD/Plano projections while keeping laser,
venue and portfolio data contracts distinct.
