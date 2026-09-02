# Phase 85 — core verify and dependency gate

## Scope

Validated the canonical MAK FLUJO entrypoint and its declared core runtime
dependencies without installing packages or starting the hub.

## Foreground results

- `/home/mak/venvs/flujo/bin/flujo verify --no-pytest --no-hub-smoke` -> exit
  `0`; compileall, health and version passed.
- `/home/mak/venvs/flujo/bin/python -m pip check` -> exit `0`; no broken
  requirements.
- Required import probes in the canonical venv passed: `typer 0.27.1`,
  `yaml 6.0.3`, `Pillow 12.3.0`, `pydantic 2.13.4`, `requests 2.34.2`,
  `boto3 1.43.66` and `matplotlib 3.11.1`.
- No pytest or hub smoke was run in this gate: pytest is not part of the
  current runtime contract and hub smoke starts a process; both remain
  separately bounded by earlier gates.

## Decision

The core FLUJO dependency slice and non-serve verifier are integrated in the
canonical venv. Web build remains blocked by Node/Rollup platform state from
Phase 80; optional render/provider/device paths remain separately classified.

## Safety

No package installation, lockfile edit, source data mutation, Git operation,
provider call or persistent process occurred. `compileall` may regenerate
normal Python cache files; these are regenerable artifacts, not source edits.

## Next

Continue the MAK-wide consumer/dependency audit, selecting a bounded local
slice with a real entrypoint. Keep optional external and mutating paths behind
their documented authority gates.
