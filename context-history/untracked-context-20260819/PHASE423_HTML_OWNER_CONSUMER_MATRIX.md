# Phase 423 - active HTML owner and consumer matrix

Date: 2026-08-15
Agent: LUNA principal
Scope: classify the canonical HTML candidates by source, consumer and
disposition. This phase is static/read-only; no browser, hub, POST, render or
external service was started.

## Matrix

| HTML surface | owner/source evidence | consumer | disposition |
|---|---|---|---|
| `context/flujo_hub.html` | generated from `web/dist/index.html` by `web/scripts/copy-context.mjs`; route handled by `src/flujo/web/hub.py` | `/`, `/hub`, `/index.html`, hub operation | active generated alias; protected |
| `context/plano_demo.html` | same single-file React build and copy script | `/plano`, RD plano/rider workflow | active generated alias; protected |
| `context/svg_visualizer.html` | same single-file React build and copy script | `/visualizer`, SVG visualizer workflow | active generated alias; protected |
| `web/dist/index.html` | Vite build output consumed by copy script | source for the three context aliases | generated source candidate; rebuild/copy gate required |
| `web/index.html` | Vite entry shell references `/src/main.tsx` | Node/Vite development build | source entry; not a served hub owner |
| `web/dist-rd/rd.html` | static RD distribution surface; exact parity with `dist_compartir/herramientas_rd.html` and WIN copy | RD tools/projection | generated/projection candidate; owner check required |
| `web/dist-plano/plano.html` | static plano distribution surface; paired with `dist_compartir/plano_rd.html` | RD/VJ plano projection | generated/projection candidate; owner check required |
| `web/venues/index.html` | canonical `web` venue surface | venue catalogue / cross-domain projection | active candidate; crosswalk validation required |
| `iskvw/piel/**`, `iskvw/editor.html` | portfolio skin and editor | public portfolio and authoring | portfolio surface; separate publish gate |
| `datadrops/cotizacion_general_eventos/*.html` | generated RD deliverables | quote handoff to producer/client | protected product output; preserve variants |
| `projects/plano/plano_editor.html` | file itself declares legacy/deprecated and points to `context/plano_demo.html` | historical plano editor | legacy evidence; do not promote |
| `docs/rd/**`, `docs/recovered/**`, `docs/cultura/**` | documentation/recovered sources | human reading, dossiers and evidence | preserve as docs/evidence; not runtime owner |
| `tools/sala3d/template.html`, cultural pages | tool/project-specific prototypes | visual experiments / demos | prototype; consumer proof required |
| `cultura/xio-concept.html`, `xio/**` | XIO surface | user explicitly removed XIO from current list | excluded/gated; no work in this phase |

## Important parity finding

The three context files are byte-identical to one another and intentionally
select their view by pathname. They are not three independent tools. However,
they are not byte-identical to the current `web/dist/index.html`: the source
build is 719,757 bytes while each context alias is 719,685 bytes. The static
diff is exit 1. This is a stale/generated parity gate, not permission to copy
or overwrite the aliases now.

## Verification

- HTML metadata parser for 19 canonical candidates: exit 0.
- `hub.py`, `web/README.md` and `copy-context.mjs` static reference check: exit
  0; route and copy ownership are explicit.
- `diff -q web/dist/index.html context/flujo_hub.html`: exit 1, expected
  evidence of generated parity drift; no files changed.
- No database, source, HTML, service, external provider or Git state changed.

## Next concrete action

Resolve the generated parity gate statically: compare the source build command,
timestamps and expected route behavior, then run only a bounded local build or
fixture if the existing Node environment is available. Do not overwrite
`context/*.html` until the build output and consumer contract are validated.
Keep RD/plano/venue/portfolio projections separate until their owners are
proven.
