# Phase 343 — EVENTO flyer and issue bridge gate

Date: 2026-08-15 (America/Santiago)
Scope: canonical FLUJO automation helpers with all external edges mocked.

## Foreground validation

- `flujo.eventos.flyer_auto.extract_instagram_shortcode()` accepted post/reel
  URLs and rejected an unrelated domain.
- `run_eventos_flyer_auto()` ran twice against temporary roots: one simulated
  image download generated input/palette artifacts with no Blender/Photoshop;
  one simulated Blender render generated a temporary preview.
- `cultura.mak_plataforma.puente_issues._sin_rutas()` sanitized Windows/Linux
  paths while preserving a real URL.
- `_guardar_estado()` preserved the previous state and cleaned its temporary
  file when atomic replacement was forced to fail.

Results:

```text
EVENTO_FLYER_DIRECT_FIXTURE=PASS
ISSUE_BRIDGE_ROLLBACK_FIXTURE=PASS
NETWORK_EMAIL_GITHUB_BLENDER_CRON_CALLS=0
```

The helper printed that optional `parth_dl` and `curl_cffi` modules are absent;
the tested path used simulated download edges and did not attempt network.

## Disposition

`VERIFIED_LOCAL_AUTOMATION_CONTRACT; EXTERNAL_EDGE_GATED`.

The EVENTO/issue helper logic is sound locally and has rollback behavior. The
user-confirmed EVENTO issue/URL bridge remains operational by user evidence,
but this phase does not call it live or create cron automation.

No source, job, asset, database, service, provider, Git or WIN path changed.

