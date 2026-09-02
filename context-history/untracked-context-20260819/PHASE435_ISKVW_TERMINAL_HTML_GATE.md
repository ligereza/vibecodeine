# Phase 435: ISKVW terminal HTML gate

## Owner and projection

The active consumer is `iskvw/piel/terminal/index.html`. Its deployment copy
`flujo-deploy/iskvw/piel/terminal/index.html` is byte-identical (`cmp` exit 0)
and has the same 33,729-byte surface. WIN, Vibecodeine, quarantine and
rollback copies are separate historical/projection variants and were not
merged.

## Contract validation

The terminal is a static portfolio skin. It embeds a visual file and loads:

1. `../../datos/archivo.json` as the unified archive;
2. `../../datos/obras.json` as the fallback.

Both data paths exist in the active owner. The HTML title and fallback loader
markers passed static assertions. The two inline JavaScript blocks passed
`node --check` with exit 0. No service, fetch to a live hub, mutation or data
write was executed.

## Disposition

`ISKVW_TERMINAL_ACTIVE; DEPLOY_COPY_EXACT; STATIC_DATA_FALLBACK_VERIFIED; HISTORICAL_VARIANTS_PRESERVED`.

No file was edited or deleted.

## Next action

Continue the HTML owner audit on the next independent active consumer. Keep
historical copies as evidence and avoid treating generated parity as a reason
to delete a distribution surface.
