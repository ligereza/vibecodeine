# Phase 414 — theater seating primitive genealogy

Date: 2026-08-15
Agent: LUNA principal
Scope: locate the original Python primitive behind the SCD venue geometry.
Read-only inspection; no GUI, export, source or data mutation was performed.

## Primitive found

Canonical path:

`/home/mak/flujo/projects/plano/referencia_plano_teatro.py`

This is the original interactive Python model, titled `PLANO ARQUITECTONICO
PRO v3.4 - Teatro SCD Plaza Egana`. It defines and renders:

- radial theater geometry from stage chord/sagitta;
- main-floor seating blocks with center and lateral seat counts per row;
- aisle width and row footprint;
- configurable balcony and balcony rows;
- backstage corridors and wall margins;
- architectural grid, labels and dimensions;
- PNG, PDF and SVG export;
- outline-only SVG/PDF intended for Blender extrusion.

Its default model explicitly contains `butacas`, `filas`, `balcon`, `pasillos`
and a `Total butacas` counter. It is the primitive the user remembered.

## Headless derivative

`/home/mak/flujo/tools/venue_geometria_scd.py` is the non-GUI derivative. It
reuses the v3.4 defaults (10 m stage chord, 0.9 m sagitta, radial seating,
7 main rows and 3 balcony rows), converts the model into 3D polylines and
writes or prints the SCD venue JSON. It preserves confidence per geometry
layer: stage reference, adjusted seating, and unverified heights.

The derivative feeds:

- `/home/mak/flujo/data/venues/scd-plaza-egana.json`;
- `/home/mak/flujo/iskvw/piel/venue/`;
- `/home/mak/flujo/tools/venue3d_smoke.mjs`.

## Provenance/parity

The primitive SHA-256 is identical in the canonical, deploy, vibecodeine and
WIN copies:

`5cf919a27729c705edfa4031b1c21b6706fe84472a74788e8a36285d5114a879`

The SCD derivative is also byte-identical in those four surfaces:

`f742317c29afd79d65919121aaa85f240d1d710e0e4e0e32c47c5fc4de35bf95`

This establishes one preserved genealogy, not four independent tools. The
canonical authoring owner remains `/home/mak/flujo`.

## Foreground validation

- AST parse of the primitive, derivative and current plano engine: exit 0.
- JSON parse of the SCD venue record, venue schema and portfolio catalogue:
  exit 0.
- `python3 tools/venue_geometria_scd.py --stdout`: read-only generator path;
  exit 0 when used as the existing SCD validation path.
- `node tools/venue3d_smoke.mjs`: exit 0; `503` edges, `120/800` drawn under
  the cap test, `0` out-of-cap geometry errors.
- No GUI was opened, no export was written and no persistent process started.

## Integration meaning

The product genealogy is now explicit:

```text
referencia_plano_teatro.py
  -> venue_geometria_scd.py
  -> data/venues/scd-plaza-egana.json
  -> venue 3D skin / client visualization
  -> future measured venue + RD/VJ layout/rider
```

The next safe evolution is to extract shared geometry into a parameterized
headless engine while preserving the GUI as a reference/client tool. Do not
rewrite the primitive or replace contributed dimensions with certified claims.
