# Phase 44 — FLUJO serve entrypoint gate

Identity: LUNA principal
Status: PASS_ENTRYPOINT_NO_SOURCE_EDIT
Scope: validate the actual migrated `flujo serve` entrypoint without starting
the hub service.

## Foreground validation

Commands and exit codes:

```text
/home/mak/venvs/flujo/bin/flujo serve --help
exit 0

PYTHONPATH=/home/mak/flujo/src /home/mak/venvs/flujo/bin/python -m flujo serve --help
exit 0
```

Observed contract:

- Command is available in the active MAK venv and as the module entrypoint.
- `serve` describes the real hub: `context/flujo_hub.html`, SVG/Plano
  visualizers, intake, jobs, RD database, tariff, plano symbols and the
  pywebview bridge.
- Options are present for `--port`, `--host`, `--desktop`, `--no-abrir` and
  `--procesar-pendientes`.
- `--procesar-pendientes` is explicitly mutating and was not called.
- The retired `--legacy` Gradio route is absent from the active option set and
  is documented as historical/unsupported.
- No server, browser, worker or persistent process was started.

## Bounded WIN → MAK entrypoint crosswalk

- `/home/mak/flujo/src/flujo/serve/server.py` and
  `/home/mak/WIN/flujo/src/flujo/serve/server.py`: normalized content equal.
- `/home/mak/flujo/src/flujo/cli.py` and the WIN counterpart both exist but
  differ; this is expected migration-anchor evidence and was not overwritten.
- `/home/mak/flujo/abrir_hub.bat` and the WIN counterpart both exist and have
  normalized content equal; raw bytes differ and the Windows launcher remains
  evidence, not a Linux runtime target.
- AST/import of MAK `cli.py` and `serve/server.py`: `PASS`.

## Decision and rollback

The active MAK `flujo serve` entrypoint is integrated and executable at the
help/contract level. No source edit is required. Keep the CLI difference open
for a later route-level comparison only if a concrete behavior mismatch
appears. Rollback is unchanged physical preservation of MAK source and WIN
launcher evidence.

