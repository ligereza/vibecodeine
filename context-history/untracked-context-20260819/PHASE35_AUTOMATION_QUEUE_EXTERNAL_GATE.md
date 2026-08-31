Identity: LUNA principal

# Phase 35 — automation queue external-provider gate

## Decision

`GET /api/automatizaciones` is not a local queue consumer. Its real path runs
the external `gh issue list --state open --limit 60 --json ...` command to read
open GitHub issues; the visible chain is Gmail -> GitHub issue -> bridge ->
flyer/Blender -> drive. The physical host has `/usr/bin/gh`, so invoking the
real endpoint would cross an external provider boundary.

The real provider path was not called. A no-provider fixture temporarily hid
`gh` and forbade `subprocess.run`; both the direct reader and a temporary local
GET returned the documented unavailable fallback with HTTP 200, then the
server shut down with zero writes. The local `src/flujo/automation.py` runner
was parsed only; it was not executed because it prepares/activates jobs and is
write-capable.

Final status: `DEFERRED_EXTERNAL_RUNTIME`. The fallback behavior is
`SAFE_FALLBACK_VERIFIED`, not proof that the GitHub/Gmail queue is available.

## Boundary

```text
GET /api/automatizaciones
    -> shutil.which("gh")
    -> gh issue list ... (external GitHub/provider boundary)
    -> normalized queue JSON

no gh / no provider
    -> {cola: [], disponible: false, motivo: ...}
```

Search vocabulary covered both language variants and aliases:
`automatizaciones`, `automatizacion`, `automation`, `cola`, `queue`, `Gmail`,
`issue`, `GitHub`, `labels`, `etiquetas`, `bridge`, `flyer-auto`, `Blender`,
`provider`, `proveedor`, `worker`, `ejecucion` and `mutacion`.

## Static and no-provider fixture gate

Foreground command: AST parse of `src/flujo/web/hub.py` and
`src/flujo/automation.py`, static check of the TypeScript panel contract,
confirmation that `gh` exists at `/usr/bin/gh`, and a temporary test fixture
that made `gh` unavailable and raised if `subprocess.run` was called.

Observed exit code: `0`.

- Python AST: 2 modules, PASS; panel contract read, PASS.
- External boundary: `gh issue list` detected, PASS.
- Physical provider command: `/usr/bin/gh` exists; not executed.
- Direct no-provider fallback: `disponible=false`, `gh` reason, zero
  subprocess calls, PASS.
- Temporary local `GET /api/automatizaciones` under the same fixture: HTTP
  200, `disponible=false`, PASS.
- Temporary server shutdown: PASS.
- Protected hub/automation source sizes and mtimes: `writes_detected=0`.
- Gmail, GitHub, bridge, Blender, drive and workers: not contacted or run.

## Mutation boundary and rollback

The actual provider path is external and may return live issues; it must remain
deferred. `run_pending_flyers()` in `src/flujo/automation.py` can prepare and
activate jobs, so it is also outside this read-only gate. Rollback is fixture
restoration and temporary-server shutdown; no source, issue, job or queue state
changed.

## Risks and next action

- There is no verified local automation queue behind this endpoint; the empty
  fallback must not be interpreted as an empty real queue.
- A future provider slice needs explicit credentials/network authority,
  bounded read-only issue listing and a separate job-execution boundary.
- Continue with remaining local hub consumers or documentation surfaces. Keep
  provider calls, bridge execution and worker activation deferred.
