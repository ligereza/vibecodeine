# Phase 443 — Plano/Rider native contract gate

## Scope

This slice validates the real RD Plano/Rider backend and CLI, separate from
the unresolved Vite HTML bundle parity. The source package is
`src/flujo/plano/`; the active consumer is `src/flujo/cli.py`; the fixture is
`projects/plano/ejemplos/evento_ejemplo.json`. HTML projections are not
overwritten in this phase.

## Owner chain

- Event input: `projects/plano/ejemplos/evento_ejemplo.json`.
- Rules/layout engine: `src/flujo/plano/engine.py` and its package exports.
- RD icons and pack/cost logic: `src/flujo/plano/iconos.py`, `packs.py` and
  `costs.py`.
- CLI entrypoint: `python3 -m flujo plano` in `src/flujo/cli.py`.
- QA instructions: `docs/QA_EVENTOS_SUPLEMENTOS.md`.
- Standalone/editor and Vite HTML projections remain separate consumers.

## Consolidation performed

`docs/QA_EVENTOS_SUPLEMENTOS.md` was corrected from Windows-first `py -m`
commands to the current MAK invocation `PYTHONPATH=src python3 -m flujo`.
No source engine, event fixture, generated product or HTML bundle was changed.

## Foreground validation

The following commands ran against the real fixture, writing only to a
temporary directory `/tmp/mak-plano-check-moq9Pw`:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile src/flujo/plano/engine.py src/flujo/cli.py
exit 0

PYTHONPATH=src python3 -m flujo plano projects/plano/ejemplos/evento_ejemplo.json --validate
exit 0

PYTHONPATH=src python3 -m flujo plano projects/plano/ejemplos/evento_ejemplo.json --validate --rider
exit 0

PYTHONPATH=src python3 -m flujo plano projects/plano/ejemplos/evento_ejemplo.json --validate --costs
exit 0

PYTHONPATH=src python3 -m flujo plano projects/plano/ejemplos/evento_ejemplo.json --validate --output /tmp/mak-plano-check-moq9Pw/plano.svg
exit 0
```

The focused assertions exited 0: generated SVG parsed as XML, Rider included
feeding, testeo and low-stimulation containment, costs included TOTAL and the
fixture retained `grid_2x`. The temporary outputs were not copied into MAK
runtime or delivery paths.

## Disposition

The native Plano/Rider path is green and is the reliable backend contract for
the RD tool. The unresolved Vite/Rollup gate affects only the standalone HTML
projection; it does not invalidate this CLI/source path. The fixture is demo
data and was not promoted to a real venue measurement or event record.

Disposition: `PLANO_RIDER_NATIVE_GREEN; CLI_FIXTURE_GREEN; QA_COMMANDS_MAK_ALIGNED; VITE_PROJECTION_SEPARATE`.

Next action: inspect the next unresolved RD HTML projection without replacing
it from this backend until its own owner/build gate is verified.
