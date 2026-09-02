# Phase 458 — RD POST Chemsex owner gate

## Scope and relationship

This cluster is a connected POST chain, not a set of unrelated duplicates:

```text
CARRUSEL CHEMSEX RevCO.pdf
  -> rd_post_chemsex_spec_build.py
  -> rd_post_chemsex_spec_2026-08-11.json
  -> rd_post_chemsex_spec_2026-08-11.html
  -> rd_post_chemsex_visual_brief_build.py
  -> rd_post_chemsex_visual_brief_2026-08-11.json + informe.md

rd_post_cover_prototype_2026-08-11.html -> rd_post_cover_prototype_2026-08-11.svg
```

The textual spec and visual brief share the spec contract; the cover is a
separate editable visual sibling. The durable active boundary is
`cultura/mak_post/pipeline.py`, which validates source-preserving packages and
keeps `public_gate=human_required`. It does not publish, rewrite or upgrade
editorial claims into scientific relations.

## Source and owner evidence

- The source PDF hash is
  `32980f6e09df56f0773393868578694263cbfe78c3fc401734680a755ba3dd48`.
- `tests/test_mak_post.py` consumes the recovered Chemsex JSON through
  `cultura.mak_post.pipeline`; the direct foreground validation returned zero
  errors, `status=candidate` and `public_gate=human_required`.
- `docs/rd/prototypes/2026-08-11/README.md` classifies the POST files and cover
  as non-operational visual/semantic prototypes. They are not mounted by
  `/api/rd-db`, `/portafolio/` or standalone Plano/Rider builds.
- No active POST publication route or production SVG asset catalog consumes
  the cover prototype.

## Foreground validation

The two existing builders ran against isolated temporary copies of their
bounded inputs:

```text
rd_post_chemsex_spec_build.py          -> exit 0; slides=7; interaction_cards=5; unlinked_relation_refs=0
rd_post_chemsex_visual_brief_build.py  -> exit 0; briefs=7
```

The isolated outputs matched the canonical recovered/prototype outputs with
`cmp` exit 0 for the spec JSON/HTML, visual brief JSON/report and cover-related
derived files. Source-preservation assertions passed: seven slides, verbatim
text-block contract, claim-only tracking for three unresolved editorial cards,
and no automatic scientific promotion.

Static checks also passed:

```text
HTMLParser: one inline script per HTML, expected data markers, 0 external asset refs
node --check: Chemsex spec script exit 0; cover script exit 0
SVG XML parse: cover SVG exit 0
local cover HTML -> SVG reference: exists, 0 external asset refs
cultura.mak_post direct validation: errors=0, candidate, human_required
```

No browser, POST request, provider, database write, package installation or
permanent service was used. The focused pytest command remains an environment
gate because this venv does not provide pytest; the direct contract check
passed.

## Disposition

```text
POST_SPEC_SOURCE_PRESERVING_GREEN
POST_VISUAL_BRIEF_DERIVATION_GREEN
POST_PIPELINE_CANDIDATE_GATE_GREEN
POST_CLAIM_ONLY_BOUNDARY_GREEN
COVER_SVG_EDITABLE_AND_LOCAL_GREEN
VISUAL_PROTOTYPE_NON_OPERATIONAL
NO_PUBLICATION_ROUTE
NO_PROMOTION
NO_DELETE
```

The chain is consolidated conceptually through its existing builder and POST
pipeline boundary, while the cover remains a separate visual consumer. No
active route, database, source document, generated production bundle or
historical evidence was changed.

## Next action

Continue the recovered HTML audit with the next large visual surface
`lasertoolkit.html`, then distinguish its active toolchain from the already
completed laser integration gate before any merge decision.

