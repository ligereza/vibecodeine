# Phase 75 — web build and lab output crosswalk

## Web outputs

`/home/mak/flujo/web/package.json` defines four build paths: context, plano,
RD and default Vite output. The copy scripts prove the ownership chain:

- `web/dist/index.html` → `context/flujo_hub.html`, `plano_demo.html`,
  `svg_visualizer.html` and `context/mapping.html`;
- `web/dist-plano/plano.html` → `dist_compartir/plano_rd.html`;
- `web/dist-rd/rd.html` → `dist_compartir/herramientas_rd.html`.

These are intentional build/share projections, not duplicate source files.
`web/node_modules` is a declared build dependency and `web/README.md`
explicitly excludes it and `web/dist` from source commits; neither is a safe
cleanup target in this physical audit. No build was run to avoid rewriting
outputs.

## Labs

`/home/mak/labs` contains dated indexes, SQLite/WAL evidence, Blender
companions, visual-index experiments and organism probes. They have no single
active FLUJO runtime consumer proven in this pass. SQLite `-wal`/`-shm`, GPU
locks, summaries and manifests are evidence of the experiment lifecycle, not
generic temporary files.

Classification: `LAB_EVIDENCE_OR_EXPERIMENT`; preserve and assign each lab an
owner before archive or deletion. The optional `/home/mak/src/ml-mobileclip`
source remains a separate external dependency candidate, not a FLUJO merge.

## Decision

No web output or lab file was changed. The remaining cleanup candidate set is
still empty beyond regenerable caches already removed in Phases 71–72.
