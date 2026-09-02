# Phase 440 — RD quotation HTML protected output gate

## Scope

The bounded slice is the RD quotation deliverable family under
`datadrops/cotizacion_general_eventos/`: the light and dark HTML products,
their Markdown brief, inline plan assets, rider, and dark PDF. This is a
client/producer handoff surface, not a runtime hub route and not a portfolio
HTML owner.

## Physical classification

- `cotizacion_general_eventos.html`: light HTML product, SHA-256
  `a5e0ef7b9b95e6ec6b9896975887f1f17a2827e5e1f8175712fdfc2f06f20fc9`.
- `cotizacion_general_eventos_dark.html`: dark/neon HTML product, SHA-256
  `de2ad4a889aae09b66439b451102dc75680f0c4070ec27da77cc52277e8de4ba`.
- `cotizacion_general_eventos_RD_dark.pdf`: PDF handoff, SHA-256
  `ac432699868a3adba9fce8d713f5a3b15b61dc29d92efdf66264a55926ef95ac`.
- The light and dark HTML files are different products, not duplicate bytes;
  both remain protected.
- The dark HTML has six exact physical projections across active deploy,
  worktree and WIN/evidence surfaces. The canonical file, deploy copy,
  vibecodeine copy and actions-runner copy compare equal; WIN copies are
  preserved as historical evidence.

## Foreground validation

Commands and observed results:

```text
HTMLParser over both HTML products
exit 0 — one html/body root each, zero script tags

Static marker and URL scan
exit 0 — RD title, pricing, plan and service markers present; only SVG/XML
namespace URLs, no external HTTP(S) asset dependency

Projection parity: cmp canonical dark HTML against flujo-deploy,
vibecodeine and actions-runner copies
exit 0 for each comparison

pdftotext cotizacion_general_eventos_RD_dark.pdf -
exit 0 — RD title, services and $500.000 package present
```

The dark product contains its SVG and image data inline and has no JavaScript
runtime. It is therefore a safe static handoff artifact. No browser service,
POST, database write or external provider was started.

## Disposition

This family is already a valid protected product output. No merge was
performed because light/dark variants are intentional and exact projections
are consumers, not independent sources. No file was edited, moved or deleted.
The visible active surface does not expose a safe generator owner to rewrite;
the deliverable remains protected until its existing RD generator contract is
explicitly selected.

Disposition: `RD_QUOTE_PRODUCTS_VALID; DARK_PROJECTIONS_EXACT; LIGHT_DARK_VARIANTS_PRESERVED; NO_SOURCE_REWRITE`.

Next action: inspect the next active venue/portfolio HTML owner, beginning with
`web/venues/index.html`, and keep quotation artifacts separate from the venue
registry and Plano/Rider projection.
