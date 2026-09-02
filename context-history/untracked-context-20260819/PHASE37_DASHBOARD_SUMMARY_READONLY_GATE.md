# Phase 37 — dashboard summary read-only gate

Identity: LUNA principal
Status: INTEGRATED_READ_ONLY
Scope: validate the migrated hub's local dashboard summary without invoking
renderers, job lifecycle mutators or external providers.

## Consumer and inputs

- Hub route: `GET /api/dashboard-summary`.
- MAK hub source: `/home/mak/flujo/src/flujo/web/hub.py`.
- MAK scoring source: `/home/mak/flujo/src/flujo/dashboard/scoring.py`.
- Local inputs read by `collect_items(repo)`:
  - `jobs/*/brief.yaml` — jobs/trabajos, excluding `_template`.
  - `projects/flyer_eventos/*/manifest.json` — flyers/piezas de eventos.
  - `projects/piezas_vectoriales/*/config.json` — vector pieces/piezas.
- Search vocabulary used: `dashboard`, `summary`, `resumen`, `score`,
  `priority`, `prioridad`, `job`, `trabajo`, `flyer`, `pieza`, `manifest`,
  `config`, `alta`, `media`, `baja`. Residual false-negative risk is limited
  to future input directories not included by the existing scoring contract.

## Static and direct validation

Foreground command (exit 0):

```text
PYTHONPATH=/home/mak/flujo/src /home/mak/venvs/flujo/bin/python - <<'PY'
  ast.parse(src/flujo/web/hub.py)
  ast.parse(src/flujo/dashboard/scoring.py)
  import flujo.dashboard.scoring, flujo.web.hub
  collect_items(/home/mak/flujo)
  build_dashboard_summary(items)
  HubRequestHandler._get_dashboard_summary()
PY
```

Observed:

- AST/import gate: `PASS`.
- Input files discovered: 9 job briefs including `_template`, 6 flyer
  manifests and 5 vector configs.
- Scored items: `19` (8 non-template jobs, 6 flyers, 5 vector pieces).
- Summary: `total_items=19`, `alta=10`, `media=7`, `baja=2`.
- Envelope keys: `total_items`, `alta`, `media`, `baja`, `top_items`.
- Each top item has `name`, `priority`, `score`, `reason`; maximum four are
  returned.
- Direct builder and handler method payloads were equal.

## Temporary HTTP gate

A temporary in-process `ThreadingHTTPServer` was bound to
`127.0.0.1:<ephemeral>`. Exactly one `GET /api/dashboard-summary` was served,
then the server was shut down and joined.

- HTTP status: `200`.
- HTTP payload matched the direct payload exactly.
- Protected snapshots of jobs, flyer manifests and vector configs reported
  `writes_detected=false`.
- No renderer, job creation/preparation/activation, provider command,
  network call or worker ran.

## Decision and rollback

The dashboard summary slice is integrated read-only. It is a real cross-tool
consumer of the existing MAK hub and can summarize migrated WIN job/flyer/
piece inputs without adapting or duplicating their sources. No source or
runtime edit was required; only this evidence report and its CSV were added.

Rollback is physical preservation: retain the current scoring reader and
inputs. If a future scoring change needs mutation or an external provider,
stop at that boundary and classify that branch as deferred rather than
changing the dashboard contract silently.

