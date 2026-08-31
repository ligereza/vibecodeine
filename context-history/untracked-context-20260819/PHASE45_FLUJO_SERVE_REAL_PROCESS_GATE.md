# Phase 45 — real FLUJO serve process gate

Identity: LUNA principal
Status: PASS_TEMPORARY_PROCESS
Scope: prove that the active MAK `flujo serve` entrypoint starts the real hub
process and serves core health endpoints, then shuts down cleanly.

## Foreground process

Command:

```text
/home/mak/venvs/flujo/bin/flujo serve --no-abrir --host 127.0.0.1 --port 53317
```

The port was selected from an ephemeral local socket for this run. The
process was temporary, not a service installation, and did not receive
`--procesar-pendientes`, `--desktop` or any external-provider option.

Observed:

- `/api/ping`: HTTP `200`, `status=ok`, `version=0.56.1`, connected true,
  root `/home/mak/flujo`, real `http-server` mode.
- `/api/status`: HTTP `200`, `status=ok`, connected true, SVG and projects
  present.
- Process termination: return code `-15` after explicit terminate; no forced
  kill required; `process_alive=false`.
- Output confirmed the hub bound only to `127.0.0.1` on the temporary port.
- Protected source/jobs/data snapshot: `writes_detected=false`.

## Decision and rollback

The actual MAK FLUJO serve entrypoint is operational at the process and health
contract level. No source or runtime data changed. Rollback is the normal
process termination already completed; no persistent service remains.

