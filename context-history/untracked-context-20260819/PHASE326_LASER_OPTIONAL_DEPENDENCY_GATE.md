# Phase 326 — laser optional dependency gate

Date: 2026-08-15 (America/Santiago)
Scope: local laser measurement versus optional vpype/hatched/flow chain.

## Consumer and dependency boundary

- Consumer: `/home/mak/flujo/src/flujo/laser.py` and the `flujo laser` CLI.
- Pure/local path: `flujo laser medir`, SVG parsing and point/travel
  measurement; no vpype required.
- Optional generation path: `flujo laser hatched`/`flow`, requiring external
  `vpype`, `hatched` and the flow plugin.

Installed check in `/home/mak/venvs/flujo`:

```text
vpype MISSING
hatched MISSING
cairosvg MISSING
pywebview MISSING
pystray MISSING
pyinstaller MISSING
```

Only vpype/hatched/flow are in this slice; no package was installed.

## Foreground results

- `python -m flujo laser estado` returned rc=1 as designed because all three
  optional laser executables are missing. It did not install or start anything.
- `python -m flujo laser medir /home/mak/trazos/2ac2c3508c8b.svg
  --presupuesto 800` parsed the existing SVG and returned rc=1 because the
  measured output is over budget: 1,069 points, 158 subtraces, 5,092.7 drawing
  units and 6,505.5 travel units. The CLI explicitly warns that the toolkit
  target is fewer than 8 subtraces.
- `flujo/laser.py` parsed successfully (rc=0).

No SVG, manifest, asset or source was changed.

## Disposition

`UNRESOLVED_OPTIONAL_DEPENDENCY; PURE_MEASUREMENT_AVAILABLE`.

The local measurement contract is usable and exposes a real quality gap in
this existing SVG, but the generation chain is not installed. This is not a
reason to install packages or reinterpret the existing `trazos` corpus as
trash. A future laser slice needs an explicit dependency decision and a
bounded source asset before generation.

## Risks and rollback

- Risk: treating `trazos` as laser-ready solely because it is SVG would be
  false; the measured sample exceeds the stated budget.
- Providers, network, services, databases, Git and WIN: untouched.
- Rollback: none needed; read-only measurement only.

