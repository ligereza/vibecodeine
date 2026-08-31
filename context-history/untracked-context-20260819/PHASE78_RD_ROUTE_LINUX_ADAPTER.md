# Phase 78 — RD route Linux adapter

## Objective

Make the active FLUJO route consumer usable on MAK without rewriting the
historical Windows route index. The bounded consumer is
`src/flujo/route/resolver.py`, exposed through `flujo hub route`.

## Physical evidence

- Index: `/home/mak/flujo/src/flujo/route/rutas_rd.json`
- Historical root in index: `C:\\rd`
- Local creative root: `/home/mak/RD`
- Existing contract: `FLUJO_RD_ROOT` is already used by RD asset code.
- No other active consumer translates `C:\\rd`; the previous direct
  `flujo route` documentation was not an installed command.

## Change

`resolver.py` now accepts `--base-dir` on `where` and `doctor`, and uses
`FLUJO_RD_ROOT` when the option is absent. It translates only the configured
historical root prefix, preserves relative suffixes, and leaves
`rutas_rd.json` unchanged. With neither option nor environment variable, the
original Windows paths remain visible for provenance.

`route/README.md` and the resolver usage text now identify the real command:
`python -m flujo hub route ...`.

## Foreground validation

1. `python3 -m py_compile src/flujo/route/resolver.py` → exit `0`.
2. `PYTHONPATH=src python3 -m flujo hub route where --area eventos --pieza flyer --base-dir /home/mak/RD --json` → exit `0`; returned `/home/mak/RD/AUTOMATIZACION` and local delivery paths.
3. `FLUJO_RD_ROOT=/home/mak/RD PYTHONPATH=src python3 -m flujo hub route where --area eventos --pieza flyer --json` → exit `0`; returned local paths.
4. `FLUJO_RD_ROOT=/home/mak/RD PYTHONPATH=src python3 -m flujo hub route doctor` → exit `0`; checked 28 local routes, 1 expected pipeline artifact missing.
5. Without local configuration, the resolver still returned `C:\\rd` paths → exit `0`.
6. Index SHA-256 after change: `e9bbc598765c68b0606bdc1f7a0d43127b6a5a7c238e54627cd10c9d2f1b0bd8`; no index/data/asset mutation.

## Risk and rollback

The one missing doctor route is an expected not-yet-generated pipeline artifact
(`input_ig.jpg` or `preview_cartelera.png`), not a missing source directory.
Rollback is a single source/document patch: remove the adapter and usage
documentation changes; `rutas_rd.json` was not modified.

## Next

Continue with the next unresolved live consumer or external boundary. Do not
delete evidence, rebuild the full RD asset tree, install dependencies, or
reopen XIO, hardware, n8n or ADB.
