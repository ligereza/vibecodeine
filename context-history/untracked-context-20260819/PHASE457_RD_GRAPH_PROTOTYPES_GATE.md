# Phase 457 — RD graph prototype owner gate

## Scope

The next recovered RD HTML cluster was audited:

- `docs/recovered/claude_sessions_2026-08-12/raw/rd_fichas_entidades_2026-08-11.html`
- `docs/recovered/claude_sessions_2026-08-12/raw/rd_matriz_interactiva_2026-08-11.html`

Both are derived views over the RD entity registry, relation graph, source
catalog and integration index. They are siblings, not duplicate owners:
`rd_fichas_entidades_build.py` produces entity profiles, while
`rd_matriz_interactiva_build.py` produces the relation matrix. The matrix has
an active copy under `docs/rd/prototypes/2026-08-11/`, whose README explicitly
classifies it as a non-operational research/design prototype not mounted by
`/api/rd-db`, `/portafolio/` or the standalone Plano/Rider builds.

The profile view has no active route or consumer reference outside the
recovered evidence set and reconciliation records. It remains a derived
candidate view, not a second RD database or public source of truth.

## Physical and provenance result

Canonical and deploy copies of both HTML views are exact. The historical WIN
copies are exact with their corresponding recovered state, but stale relative
to the canonical regenerated views:

```text
rd_fichas_entidades HTML  canonical/deploy dd78b402...  WIN 0533f2d2...
rd_matriz_interactiva HTML canonical/deploy 4a7929e1...  WIN 19655752...
```

The five builder inputs were also checked. Registry, graph and normalized
reagent data are byte-identical across canonical/deploy/WIN. The catalog and
integration index are canonical/deploy-identical but differ from WIN, which
explains the regenerated view divergence without implying corruption.

## Foreground validation

The two existing builders were executed against an isolated temporary set of
the seven bounded source/input files; no source tree or generated bundle was
used as an output target:

```text
rd_fichas_entidades_build.py       -> exit 0; profiles=48 connected=40 unconnected=8
rd_matriz_interactiva_build.py    -> exit 0; entities=48 relations=52
```

The isolated outputs were byte-identical to the canonical recovered outputs:

```text
rd_fichas_entidades JSON  cmp -> exit 0
rd_fichas_entidades HTML  cmp -> exit 0
rd_matriz_interactiva HTML cmp -> exit 0
```

A preliminary probe used symlinked inputs and the builders' `Path.resolve()`
therefore resolved its output root back to the canonical recovered directory.
It rewrote the two recovered generated files with identical bytes; their
SHA-256 values remained unchanged. The validation above was then repeated with
real bounded temporary copies, so the final builder evidence does not depend
on that probe behavior.

Candidate-specific HTML assertions passed with exit 0 for both views: one
inline script, expected embedded data markers, zero external asset references,
and valid local HTML structure. Extracted JavaScript passed `node --check` for
both views with exit 0. No browser, network, provider, database write or
permanent service was invoked.

## Disposition

```text
RD_GRAPH_SOURCE_INPUTS_GREEN
RD_PROFILE_VIEW_DETERMINISTIC_GREEN
RD_RELATION_MATRIX_DETERMINISTIC_GREEN
CANONICAL_DEPLOY_PARITY_GREEN
WIN_PROJECTION_STALE_BY_PROVENANCE
NON_OPERATIONAL_PROTOTYPE
NO_ACTIVE_CONSUMER
NO_PROMOTION
NO_DELETE
```

No source, database, active RD route, portfolio skin or generated production
bundle had content changed. The two views remain preserved as research/design evidence
with their shared input contract; they are not merged into `/api/rd-db` or the
portfolio until an explicit route and human RD decision exists.

## Next action

Continue the recovered HTML audit with
`rd_post_chemsex_spec_2026-08-11.html` and
`rd_post_cover_prototype_2026-08-11.html`, locating owners and active
consumers under `/home/mak/*` before deciding whether either belongs to the RD
POST surface or remains a prototype.
