# Phase 42 — CULTURA tapiz static gate

Identity: LUNA principal
Status: PASS_READ_ONLY
Scope: validate the CULTURA static surface that the FLUJO hub explicitly
allows, without exposing the whole cultural archive or changing artwork.

## Consumer and provenance

- Hub allowlist: `projects/tapiz/` in
  `/home/mak/flujo/src/flujo/web/hub.py`.
- MAK target: `/home/mak/flujo/projects/tapiz/`.
- WIN source: `/home/mak/WIN/flujo/projects/tapiz/`.
- Bounded crosswalk: max depth 3, 66 files in MAK and 66 in WIN; all 66
  relative paths are common, with no MAK-only or WIN-only path.
- Raw SHA-256 equality: 39/66 files. The remaining raw differences are
  preserved as evidence; no line-ending normalization, artwork rewrite or
  generator execution was performed.
- `projects/cultura/` is a broader cultural source tree and is not in the
  static allowlist; it must not be inferred as publicly exposed by presence
  on disk.
- Search vocabulary used: `cultura`, `culture`, `tapiz`, `weaving`, `obra`,
  `artwork`, `svg`, `dossier`, `pieza`, `static`, `allowlist`, `public`,
  `expose`, `exponer`. Residual risk is limited to deeper files beyond the
  bounded max-depth crosswalk and to semantic artwork differences not
  evaluated by raw hashes.

## Foreground validation

Foreground command (exit 0):

```text
PYTHONPATH=/home/mak/flujo/src /home/mak/venvs/flujo/bin/python - <<'PY'
  ast.parse(src/flujo/web/hub.py)
  import flujo.web.hub
  start temporary ThreadingHTTPServer
  GET /projects/tapiz/README.md
  GET /projects/tapiz/piezas_curadas/border_dossier_tapiz.svg
  GET /projects/cultura/README.md
  shutdown server
PY
```

Observed:

- AST/import: `PASS`.
- Allowed README: HTTP `200`, 2,962 bytes.
- Allowed SVG: HTTP `200`, 105,253 bytes.
- Non-allowlisted `projects/cultura/README.md`: HTTP `404`.
- Protected tapiz/hub snapshot: `writes_detected=false`.
- No artwork, README, generator, tree copy or service changed/ran.

## Decision and rollback

The bounded CULTURA `tapiz` static consumer is integrated read-only. The
allowlist exposes the intended tapiz surface and blocks the broader
`projects/cultura/` tree. Raw content differences remain classified evidence;
they are not a reason to overwrite the MAK artwork or the user's SVG README.

Rollback is physical preservation: keep the current allowlist and assets. Any
future cultural slice needs its own named consumer, bounded paths and visual
validation before publication.

