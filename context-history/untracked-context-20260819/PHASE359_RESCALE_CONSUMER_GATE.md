# Phase 359 — render rescale consumer gate

Date: 2026-08-15 (America/Santiago)

## Scope

Validated the downstream local consumer in
`/home/mak/flujo/src/flujo/render/rescale.py` using pure dictionaries and a
temporary config file. No real project or config was written.

## Results

```text
RESCALE_PURE_NO_MUTATION=PASS
RESCALE_DPI_TEMP=PASS canvas=1949x768
RESCALE_PROPORTION_ROLLBACK=PASS
CURRENT_DPI=PASS value=508
PYCOMPILE_RC=0
```

The DPI path preserves the input dictionary while scaling a copy, the
proportion path warns when elements are intentionally not repositioned, and
the file wrapper writes only to an explicit temporary output while preserving
the source config.

## Disposition

`VERIFIED_RESCALE_CONSUMER; REAL_CONFIG_MUTATION_UNRUN`

The local render-input vertical now includes config validation and controlled
rescaling. Actual real-project rescaling remains a foreground operation.

## Rollback and boundary

No source, real config, asset, project, database, service, provider, Git state
or WIN evidence changed. No rollback is required. Any in-place rescale must be
explicit and retain a byte/hash backup before execution.
