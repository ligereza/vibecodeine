# Phase 438 — Rave gallery HTML owner gate

## Scope

The bounded slice is the cultural Rave icon gallery under
`docs/cultura/ensayos/rave`. It includes the editable SVG set, its manifest,
the essay anchors, the shared builder and the generated HTML consumer. No
portfolio, RD, Node/Vite, database or historical WIN surface is part of this
slice.

## Owner and dependency chain

- Source assets: `docs/cultura/ensayos/rave/iconos/*.svg` (16 files).
- Source manifest: `docs/cultura/ensayos/rave/iconos.json` (16 entries with
  `ancla` values).
- Human guide: `docs/cultura/ensayos/rave/GUIA-DE-EDICION.md`.
- Consumer/readme: `docs/cultura/ensayos/rave/LEEME.md` and
  `docs/cultura/ensayos/rave/ensayo.md`.
- Generator/validator: `tools/iconos_conjunto.py`, parameterized by
  `--raiz`; this is the single shared implementation for icon sets.
- Generated output: `docs/cultura/ensayos/rave/galeria.html`; it is not edited
  manually.
- Optional browser workshop dependency: `docs/cultura/lib/compilador.js` and
  `docs/cultura/lib/vocabulario.json`, loaded only by the generated workshop;
  the static gallery remains usable if that optional module is unavailable.

## Foreground validation

Commands and observed results:

```text
python3 -m py_compile tools/iconos_conjunto.py
exit 0

python3 tools/iconos_conjunto.py validar --raiz docs/cultura/ensayos/rave
exit 0 — 16 files, 0 errors, 0 warnings

python3 tools/iconos_conjunto.py construir --raiz docs/cultura/ensayos/rave --titulo "EL INFORME RAVE"
exit 0 — 16 icons, 60.2 KB
```

A focused Python assertion checked all 16 manifest files, all 16 essay
anchors, all 16 generated cards, the workshop marker and the `../../lib`
relative dependency. It exited 0. The generated HTML hash was identical
before and after the deterministic rebuild:

`ab80931ca879e5c9328ff78afc823f3b21b9d05446ec2a54eb1d5a0cc4a0154c`.

The repository pytest suite was not invoked because pytest is not installed;
no package was installed. The equivalent bounded assertions and the real
validator/build path passed.

## Consolidation performed

`GUIA-DE-EDICION.md` was corrected to point to the current shared builder and
the actual `iconos.json` location. References to the obsolete local
`herramientas/`, `datos/` and `exportar_png.py` copies were removed from the
guide. No SVG, manifest, essay or generated HTML was deleted or changed.

## Risks and disposition

- The gallery is a generated cultural artifact, not a Vite application.
  Keep it separate from the stale RD Vite bundle gate.
- Raster animation measurement requires the existing semantic rasterizer and
  an animation-capable backend; generated GIFs remain scratchpad evidence and
  are not added to the repo.
- The optional workshop is not a hidden network or service dependency; its
  failure is intentionally isolated by the page.
- Historical variants and WIN evidence were not touched.

Disposition: `RAVE_GALLERY_OWNER_CONFIRMED; SHARED_BUILDER_GREEN; GUIDE_DRIFT_REPAIRED; NO_EVIDENCE_DELETED`.

Next action: inspect the next independent HTML owner from the physical MAK
surface, prioritizing `tools/sala3d/template.html` and its existing build
contract, while keeping FRVR role projection, official reaction table, privacy
DB and stale generated bundle gates open.
