# Phase 38 — RD event presets read-only gate

Identity: LUNA principal
Status: INTEGRATED_READ_ONLY
Scope: validate the local RD event-presets catalog exposed by the migrated
hub, without rendering, posting, database writes or external calls.

## Consumer and provenance

- Hub route: `GET /api/event-presets`.
- MAK source: `/home/mak/flujo/src/flujo/web/hub.py` and
  `/home/mak/flujo/src/flujo/eventos/presets.py`.
- WIN source comparison: `/home/mak/WIN/flujo/src/flujo/eventos/presets.py`.
- The route returns `list_event_presets()`, which uses `deepcopy` over the
  local `EVENT_PRESETS` constants. It does not call a renderer, database,
  network provider or job lifecycle operation.
- Search vocabulary used: `event`, `evento`, `preset`, `operativo`, `under`,
  `underground`, `base`, `mediano`, `mainstream`, `masivo`, `festival`,
  `rider`, `plano`, `voluntarios`, `asistentes`, `testeo`. Residual risk is
  limited to future presets not added to the existing catalog.

## Static and direct validation

Foreground command (exit 0):

```text
PYTHONPATH=/home/mak/flujo/src /home/mak/venvs/flujo/bin/python - <<'PY'
  ast.parse(src/flujo/web/hub.py)
  ast.parse(src/flujo/eventos/presets.py)
  import flujo.web.hub, flujo.eventos.presets
  list_event_presets()
PY
```

Observed:

- AST/import gate: `PASS`.
- Preset IDs: `under`, `base`, `mainstream` (3 total).
- Each preset has the same 14-key schema: `id`, `label`, `description`,
  `duracion_horas`, `voluntarios`, `asistentes_estimados`,
  `incluye_testeo`, `masivo`, `mesas`, `sillas`, `electricidad`, `luz`,
  `zonas`, `notas`.
- Returned `zonas` values are lists and each `id` matches its map key.
- Deep-copy boundary: `PASS`; mutating a returned probe did not mutate
  `EVENT_PRESETS`.
- Normalized MAK/WIN source content: equal.

## Temporary HTTP gate

A temporary in-process `ThreadingHTTPServer` was bound to
`127.0.0.1:<ephemeral>`. Exactly one `GET /api/event-presets` was served,
then the server was shut down and joined.

- HTTP status: `200`.
- HTTP payload matched the direct payload exactly.
- Protected hub/preset source snapshot: `writes_detected=false`.
- No POST, renderer, database mutation, provider, network call or worker ran.

## Decision and rollback

The RD event-presets slice is integrated read-only. MAK already contains the
same local catalog as the WIN source; no adapter, copy or source edit is
required. The returned deep copy safely separates API consumers from the
constant catalog.

Rollback is physical preservation: retain the current preset reader and
constants. If a future event path requires mutation or external data, stop at
that boundary and classify it separately instead of changing this GET
contract.
