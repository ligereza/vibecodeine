# Phase 433: mapping HTML owner consolidation

## Exact family

The following five files have the same SHA-256
`e5c06dbb5491b11ed1b36e37969c3d4772d45c476997b3d887b79560c0392d3c`:

- `web/public/mapping.html`
- `web/dist/mapping.html`
- `web/dist-rd/mapping.html`
- `web/dist-plano/mapping.html`
- `context/mapping.html`

`cmp` parity is therefore exact. A Python `HTMLParser` smoke check on the
source, dist and context files found 245 tags and the expected Event Rigging
title in each file.

## Owner and consumers

`web/public/mapping.html` is the source asset copied by Vite into each build
surface. `web/src/components/MappingTool.tsx` embeds and opens it through the
relative `mapping.html` path. `web/scripts/copy-context.mjs` copies the main
build version to `context/mapping.html` so the local `file://` hub keeps the
same relative contract.

The RD and Plano copies are generated public assets of their respective Vite
builds, not competing implementations. Deleting them or replacing them with
symlinks would break a distribution root even though their bytes are equal.

## Disposition

`MAPPING_HTML_LOGICALLY_CONSOLIDATED; FIVE_BYTE_IDENTICAL_CONSUMER_PROJECTIONS; NO_PHYSICAL_DELETE`.

No source, generated HTML, UI route or data changed. This is an ownership and
provenance consolidation only.

## Next action

Continue with the next independent HTML family, starting from the active MAK
consumer and tracing its source before considering any projection update.
