# Phase 133 - dependency and import read-only gate

## Foreground validation

Using the canonical FLUJO venv:

```text
python -m pip check                         -> exit 0
python import gate                          -> exit 0
(web) npm run typecheck                     -> exit 0
```

The import gate passed for `flujo`, `flujo.cli`, `flujo.rd.database`,
`flujo.web.hub`, `cultura.mak_plataforma.tandas` and
`cultura.mak_research.fuentes`. `pip check` reported no broken requirements.
The TypeScript compiler completed with `tsc --noEmit` and no diagnostics.

## Boundaries still open

- `pytest` is absent from the canonical venv and system Python; no install was
  attempted.
- The web production build remains a separate Node/Rollup gate because the
  host is Node 18.20.4 while Vite requires a newer Node range and the native
  Rollup package is absent.
- `qwen_agent` is absent; chat runtime remains gated without installation.

No provider, database, service, network, browser, generated output or Git
action ran.

## Decision

Core Python dependency/import and web typecheck gates are verified. The
remaining dependency statuses are explicit environment gates, not converted
into a requirements file or resolved by unapproved installation.

## Next action

Continue the full-MAK read-only audit and source/output ownership mapping;
revisit the environment gates only when the required runtime authority exists.
