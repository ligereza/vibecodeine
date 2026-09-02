# Phase 434: ISKVW editor contract gate

## Owner and family

The active editor is `iskvw/editor.html`; its exact deployment projection is
`flujo-deploy/iskvw/editor.html` (same size and SHA-256
`d90010161edb83ec1e341c00bcf203510badd70df6cadcdeb23f02ba996d9f75`).
`WIN/flujo/iskvw/editor.html`, `/home/mak/plataforma/iskvw/editor.html` and
rollback copies are different historical variants and were not merged.

## Contract evidence

The editor reads `iskvw/datos/curaduria.json` and `tablero.json`, exposes the
existing portfolio triangulation/review/index routes, and describes its output
boundary as download-first. Its page text explicitly says that selection does
not publish or move files. The HTML references the existing
`tools/validar_curaduria.py` gate and `mesa_montaje.js` consumer.

The repository tests could not be invoked because both the FLUJO venv and
system Python lack `pytest`:

`/home/mak/venvs/flujo/bin/python -m pytest ...` -> exit 1,
`No module named pytest`.

No package was installed. The following foreground substitute passed without
writing canonical files:

- `tools/validar_curaduria.py` compiled with the FLUJO venv (exit 0);
- static marker assertions passed for contract, triangulation, review,
  download-only and no-move boundaries;
- Node executed the real `construirCuraduria()` extracted from the active HTML;
  it preserved UTF-8 `Diseño y daño — el año`, rounded `0.351` to `0.35`,
  preserved unknown `orden_ritual`, retained `mostrar: false` and returned
  exit 0.

## Disposition

`ISKVW_EDITOR_ACTIVE_CONTRACT_CONFIRMED; DEPLOY_COPY_EXACT; HISTORICAL_VARIANTS_PRESERVED; PYTEST_ENVIRONMENT_GATED`.

No editor, data file, portfolio record or projection changed.

## Next action

Continue the next independent HTML consumer. Keep the missing pytest dependency
and the stale RD Vite bundle as separate environment gates; do not install or
rewrite either one during HTML consolidation.
