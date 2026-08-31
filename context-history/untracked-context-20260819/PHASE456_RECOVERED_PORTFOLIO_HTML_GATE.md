# Phase 456 — Recovered portfolio HTML evidence gate

## Scope

The recovered HTML cluster under
`/home/mak/flujo/docs/recovered/claude_sessions_2026-08-12/raw/` was reviewed
as evidence, not as an active runtime source:

- `AX.html`: interactive image-analysis prototype with local file input,
  Canvas output and CSV export.
- `sinreferencia.html`: interactive visual/optical experiment with local
  Canvas scenes and no external runtime dependency.
- `organismo.html`: portfolio/artistic-position reference rendered with local
  SVG. The existing dossiers explicitly describe it as a reference of
  experience and artist position, not a definitive public build.

`organismo.html` is mentioned by
`projects/cultura/dossiers/grados_de_desacuerdo.md` and
`projects/cultura/PORTAFOLIO_ORGANISMO.md`. No active runtime owner or
consumer was found for `AX.html` or `sinreferencia.html`.

## Physical parity

The canonical recovered copies are byte-identical to the corresponding
historical Windows copies and the deploy projection:

```text
AX.html            cmp canonical/deploy=0  cmp canonical/WIN=0
sinreferencia.html cmp canonical/deploy=0  cmp canonical/WIN=0
organismo.html     cmp canonical/deploy=0  cmp canonical/WIN=0
```

SHA-256 values:

```text
AX.html            15b0e87d42f53eb8ab1ba2db0b4d57ad0e926b81abe81a7954c9501e5ebe4b02
sinreferencia.html 88832bfff60467edbeba2adf873ba0164d6e8eb47efbe47a4c13ecf4836fe1a4
organismo.html     4d4b18435ee2fc22a0e0bfa7c2fc44b48bd5cbcbab33d9fb6df1d9ea3690467
```

## Foreground validation

Candidate-specific HTMLParser assertions passed with exit 0:

```text
AX.html            25,510 bytes, 49 tags, 1 script, 0 external asset refs
sinreferencia.html 16,607 bytes, 91 tags, 1 script, 0 external asset refs
organismo.html     15,963 bytes, 173 tags, 1 script, 0 external asset refs
```

The assertions also found each local implementation marker: Canvas/object URL
and CSV export for `AX`, Canvas scenes and local interaction for
`sinreferencia`, and SVG construction for `organismo`. No network asset,
provider, service or browser automation was invoked. The process scan found no
running `flujo`, `uvicorn`, Vite or serving Node process.

## Disposition

```text
RECOVERED_PORTFOLIO_REFERENCE_ONLY
NO_ACTIVE_CONSUMER_FOR_AX_OR_SINREFERENCIA
ORGANISMO_REFERENCE_OWNER_DOCUMENTED
HISTORICAL_AND_DEPLOY_COPIES_EXACT
NO_PROMOTION
NO_DELETE
```

The three artifacts remain preserved in their existing canonical, deploy and
WIN evidence locations. They are not merged into the active portfolio skin,
not promoted as a second source of truth, and not removed as duplicate files.

## Next action

Audit the next recovered HTML cluster, beginning with
`rd_fichas_entidades_2026-08-11.html` and
`rd_matriz_interactiva_2026-08-11.html`, first locating their active owners
under `/home/mak/*`, then testing source/projection parity and real consumers.

