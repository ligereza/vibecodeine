Identity: LUNA principal

# Phase 31 — ISKVW SVG visualizer/index read-only gate

## Decision

The ISKVW SVG visualizer/index is already integrated in MAK as a read-only
consumer. The MAK hub exposes both `/api/list-svg-works` and its
`/api/svg-index` alias, and the static UI requests the primary route. The
existing `svg/` root contains 11 assets in two groups; the WIN archive has the
same 11 relative paths and the same content after normalizing Windows CRLF to
Linux LF. No SVG was copied, regenerated or edited.

`src/flujo/web/svg_preview.py` is a pure preview renderer used as a local
library boundary, not a reason to install a rasterizer. Its bounded fixture
rendered and parsed as XML in memory. The production SVG/artwork generators
remain outside this slice.

## Crosswalk and search coverage

```text
WIN/flujo/context/svg_visualizer.html
    -> MAK context/svg_visualizer.html
    -> MAK src/flujo/web/hub.py
       -> GET /api/list-svg-works
       -> GET /api/svg-index (same payload alias)
       -> read-only svg/ root listing
```

Static vocabulary covered both language variants and labels: `visualizer`,
`visualizador`, `index`, `indice`, `works`, `obras`, `SVG Studio`, `Portafolio`,
`Portfolio`, `Cultura`, `Culture`, `svg`, `preview` and `visualizacion`.

The relevant MAK and WIN hub/UI files differ in their broader bundles, so
whole-file equality is not used as the integration claim. The preview module
is byte-identical. The route tokens, allowlist and asset contract were checked
at the current MAK consumer.

## Static and fixture gate

Foreground command: AST parse/import of `src/flujo/web/hub.py` and
`src/flujo/web/svg_preview.py`; extraction of route tokens and UI labels from
`context/svg_visualizer.html`; allowlist inspection; in-memory preview fixture;
bounded listing of the existing MAK `svg/` root; and relative-path/hash
crosswalk against `/home/mak/WIN/flujo/svg`.

Observed exit code: `0`.

- AST parse/import: 2 modules, PASS.
- UI route tokens: `/api/list-svg-works` once; `/api/svg-index` absent from
  the HTML because it is a backend alias; `SVG Studio`, `Portafolio` and
  `Cultura` labels present, PASS.
- Static root allowlist includes `svg/` alongside the existing project/docs
  roots, PASS.
- `svg_preview.render_svg` fixture: 413-byte SVG parsed by XML, PASS; no
  filesystem output.
- MAK listing: groups `eventos_rd` and `suplementos_rd`, 11/11 assets found,
  PASS.
- WIN/MAK asset crosswalk: 11/11 relative paths equal. Raw hashes differ
  because WIN files use CRLF; all 11 hashes match after CRLF-to-LF
  normalization. This is line-ending provenance, not a missing or copied
  artwork discrepancy.

## Temporary HTTP result

After documenting the read-only boundary, a temporary in-process
`ThreadingHTTPServer` bound to `127.0.0.1:<ephemeral>` served exactly two GET
requests and was shut down, closed and joined in the same foreground command.

- `GET /api/list-svg-works`: HTTP 200, `count=11`, groups
  `eventos_rd`/`suplementos_rd`, PASS.
- `GET /api/svg-index`: HTTP 200, `count=11`, same payload as the primary
  route, PASS.
- Temporary server shutdown: PASS.
- Protected hub, preview module, visualizer HTML, SVG state file and all 11
  SVG sizes/mtimes: `writes_detected=0`.
- No POST, upload, render, permanent service or optional package install was
  used.

Final status: `INTEGRATED_READ_ONLY`.

## Mutation boundary and rollback

The listing route calls only filesystem reads and the declared SVG state
lookup. The preview fixture stays in memory. Rollback is temporary-server
shutdown; if any protected file changes, reject the gate and preserve the
existing resolver. The SVG artwork tree is evidence/runtime data, not a target
for normalization.

## Risks and next action

- The visualizer browser bundle is minified and broader than this route; a
  browser interaction test is not claimed here.
- Optional production rasterizers and generators remain unverified and are
  not needed for the read-only listing contract.
- The next unresolved ISKVW consumer is the portfolio catalog or show-kit
  surface. Select one only after checking its real MAK files, consumer and
  mutation boundary; do not batch both into this slice.
