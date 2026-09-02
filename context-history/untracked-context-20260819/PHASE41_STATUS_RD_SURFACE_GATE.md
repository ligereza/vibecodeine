# Phase 41 — hub status and MAK-wide RD surface gate

Identity: LUNA principal
Status: PASS_READ_ONLY
Scope: validate the hub operational status and classify the separate MAK-wide
RD asset surface discovered by the required `/home/mak/*` search.

## Physical surface

- Hub target: `/home/mak/flujo`.
- Separate RD asset root: `/home/mak/RD`.
- Bounded metadata result for `/home/mak/RD`: 1,743 files and 192
  directories.
- Dominant formats are binary/creative assets: 1,043 PNG, 138 JPG, 104 BLEND,
  82 PDF, 53 AEP, 40 PSD, 39 AI and 30 SVG, plus video, archive and source
  formats.
- This is an asset/evidence surface, not the FLUJO hub's structured RD data
  source. No whole-tree copy, deduplication or artwork rewrite was attempted.
- Structured RD data remains under `/home/mak/flujo/data/`; the empty field DB
  and synthetic demo/evidence boundaries are documented in Phase 40.

## Status consumer validation

- Hub route: `GET /api/status`.
- Source: `/home/mak/flujo/src/flujo/web/hub.py`, `_get_status`.
- AST/import gate: `PASS`, exit 0.
- Direct response schema: `status`, `version`, `root`, `has_svg`,
  `has_projects`, `connected`, `time`.
- Direct response: `status=ok`, `version=0.56.1`, root
  `/home/mak/flujo`, `has_svg=true`, `has_projects=true`, `connected=true`.
- Temporary localhost GET-only server: HTTP `200`, schema valid, then clean
  shutdown.
- Protected hub/data/RD-asset snapshot: `writes_detected=false`.

## Decision

The status route is integrated read-only. The separate `/home/mak/RD` surface
is classified `EVIDENCE_ASSET_SURFACE`: it may contain reusable creative
assets, but no migration decision follows from file presence, extension or
volume alone. Any future asset slice needs a named hub consumer, provenance,
format/platform compatibility and a bounded visual validation.

