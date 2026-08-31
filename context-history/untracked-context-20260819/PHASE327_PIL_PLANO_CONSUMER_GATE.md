# Phase 327 — Pillow/plano consumer gate

Date: 2026-08-15 (America/Santiago)
Scope: installed image dependency and pure RD plano generation functions.

## Consumer paths

- `/home/mak/flujo/src/flujo/plano/trazador.py` — Pillow-backed PNG-to-SVG
  symbol tracing.
- `/home/mak/flujo/src/flujo/plano/engine.py` — in-memory event validation,
  SVG layout and rider generation.
- Dependency: Pillow `12.3.0`, already verified in Phase 325.

## Foreground fixture

An in-memory RGBA PNG was created with Pillow and passed as bytes to
`trazador.trazar()`. A synthetic event fixture with name, 6-hour duration,
8 volunteers, testeo, 2,500 attendees and `grid_2x` layout passed
`engine.validate_evento()`, `render_svg()` and `render_rider()`.

```text
PIL_TRACER_FIXTURE=PASS svg_chars=189
PLANO_ENGINE_FIXTURE=PASS svg_chars=8695 rider_chars=655
FILES_WRITTEN=0
```

The first probe omitted the required event name and correctly returned
`ok=False` with `Falta nombre del evento`; the fixture was corrected and
rerun. No source failure or file mutation occurred.

## Disposition

`VERIFIED_INSTALLED_DEPENDENCY_SLICE`.

Pillow is sufficient for the active symbol/plano slice; the functions run
without vpype, Cairo or an external service. The generated SVG/rider was kept
in memory only. The separate laser generation dependency remains unresolved
per Phase 326.

## Changes and risks

- Files, assets, databases, services, packages, providers, Git and WIN:
  unchanged.
- Risk: this proves the in-memory core, not live POST mutators or filesystem
  project creation.
- Rollback: none needed; no persistent output was created.

