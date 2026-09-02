# Phase 439 — sala3d HTML build gate

## Scope

The bounded slice is the conceptual 3D culture/portfolio gallery. Its owner
chain is `tools/sala3d/template.html` + `tools/sala3d/build.js`, the curated
SVG inputs under `projects/tapiz/piezas_curadas/`, and the demo projection
consumed from `tools/dist/system_status.json`. No RD, database, XIO, Git or
historical WIN surface was changed.

## Static owner validation

- `node --check tools/sala3d/build.js` exited 0.
- `python3 tools/compete_engine.py --help` exited 0.
- Focused assertions exited 0: all 10 artwork paths exist, all 10 source
  SVGs parse as XML, each artwork token occurs once, and the three runtime
  tokens (`__THREE__`, `__CSS3D__`, `__CALM_JSON__`) occur once.
- No stale token or output artifact was found before the build attempt.

## Bounded build attempt

The documented prerequisite was executed in the foreground:

```text
python3 tools/compete_engine.py --demo
exit 0 — wrote tools/dist/system_status.json (demo projection)

timeout --signal=TERM 20s node tools/sala3d/build.js
exit 124 — dependency fetch did not finish within the bounded window
```

The build cached `tools/sala3d/.cache/three.min.js` but did not cache
`CSS3DRenderer.mjs` and did not produce `tools/dist/sala3d.html`. The running
Node process was stopped after the bounded check; a process check found no
remaining `node tools/sala3d/build.js` or `compete_engine` process.

## Disposition

The source/consumer contract is valid, but the generated artifact is not
claimed integrated. The exact external dependency gate is the first-run
download in `tools/sala3d/build.js` from the pinned unpkg URLs. Recovery is to
rerun the same bounded build when that dependency endpoint is reachable or
provide the already-pinned cache through the normal dependency process; no
package installation or source rewrite is justified.

`tools/dist/system_status.json` is explicitly demo/evidence data, not a real
ecosystem data source. It remains classified and is not promoted to production
portfolio content. No evidence was deleted.

Disposition: `SALA3D_OWNER_STATIC_GREEN; DEMO_INPUT_GENERATED; EXTERNAL_ASSET_FETCH_GATED; ARTIFACT_NOT_BUILT`.

Next action: keep this gate open and inspect the next independent HTML
consumer, beginning with the generated RD quotation surface, without editing
minified bundles or conflating it with the portfolio 3D artifact.
