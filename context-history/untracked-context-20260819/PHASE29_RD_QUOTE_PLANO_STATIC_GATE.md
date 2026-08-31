Identity: LUNA principal

# Phase 29 — RD quote/plano static and fixture gate

## Decision

The next RD quote/plano vertical is already present in the MAK hub and its
pure consumers. No source adapter or data migration is justified by this
read-only gate. The route contract is sufficiently bounded for a later
temporary localhost HTTP check, but no POST route or hub process was called in
this phase.

Vertical under review:

```text
flujo app → web.hub → RD UI → quote/plano route → existing local data and pure renderer
```

## Physical contract

| Surface | Current MAK consumer | Input | Output | Mutation status |
|---|---|---|---|---|
| `GET /api/cotizacion-servicios` | `data/cotizacion_servicios.json` through `web/hub.py` | local JSON | editable service items/presets | read-only |
| `GET /api/rd-packs` | `plano/packs.py` + `data/rd_packs.json` | local tariff JSON | pack catalog/order/default | read-only; already validated in Phase 28 |
| `POST /api/cotizacion/render` | `cotizaciones_base.generar_cotizacion_base` | JSON event/preset | items, totals, Markdown | pure in-memory fixture path |
| `POST /api/plano/render` | `serve.server.api_plano_render` → `plano.engine`/`costs`/`packs` | JSON event/pack | layout, rider, costs, validation | pure in-memory fixture path; pack reload mutates only module memory |

## Foreground fixture result

Command used, with `PYTHONPATH=/home/mak/flujo/src` and the MAK venv:

```text
python3 -c "AST parse six modules; load two JSON inputs; run quote fixtures
under/base/mainstream; run plano fixtures INFO/TESTEO/COMPLETO; compare tracked
mtimes/sizes before and after"
```

Observed exit code: `0`.

- Six Python modules parsed: hub, lightweight server, quote base, packs,
  engine and costs.
- Two JSON inputs loaded: `data/cotizacion_servicios.json` and
  `data/rd_packs.json`.
- Quote fixtures passed for `under`, `base`, `mainstream`; totals were
  `359700.0`, `711700.0`, `1387100.0`.
- Plano fixtures passed for `INFO`, `TESTEO`, `COMPLETO`; zone counts were
  `2`, `5`, `6`, with totals `250000`, `300000`, `500000`.
- Tracked source/data mtimes and sizes were unchanged: `writes_detected=0`.
- Existing declaration gate remains green: `Pillow>=12.3.0` is in base
  `pyproject.toml` and `requirements.txt`.

## Temporary HTTP contract result

After documenting the mutation boundary above, a temporary in-process
`ThreadingHTTPServer` was bound to `127.0.0.1` on an ephemeral port. No
`flujo serve` process, browser or permanent service was started.

- `GET /api/cotizacion-servicios`: HTTP 200; service items JSON valid.
- `POST /api/cotizacion/render` with the `base` fixture: HTTP 200; total
  `711700.0` and non-empty items.
- `POST /api/plano/render` with the `INFO` fixture: HTTP 200; total `250000`,
  two zones and validation `ok=true`.
- The temporary server shut down and its thread joined successfully.
- Tracked data/UI mtimes and sizes remained unchanged: `writes_detected=0`.
- Command exit code: `0`.

## Dependencies and risks

- The pure quote/plano path uses the local `flujo` package, standard library,
  local JSON tariff/service data and the existing plano engine.
- The full hub imports Pillow directly; its base declaration was repaired in
  Phase 28. Desktop packages `pywebview` and `pystray` remain optional.
- The HTTP handlers use POST for render operations, so a temporary runtime
  check must document payloads, expected JSON, process lifetime and rollback.
- No PDF export, browser behavior, file upload, logo mutation or external
  provider is part of this gate.

## Next action

Classify RD quote/plano as integrated and move to the next unresolved hub
surface. The next slice must begin with the same static/fixture gate; do not
expand into uploads, external providers or mutating commands without a new
rollback boundary.
