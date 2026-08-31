# Phase 274 — trazos source/projection gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Scope

Started at `/home/mak/*`, then compared `/home/mak/trazos` with the active
ISKVW projection `/home/mak/flujo/iskvw/piel/trazos`. This phase is static and
fixture-only; no creative file was moved, rewritten or rendered.

## Physical inventory

```text
/home/mak/trazos:                  649 SVG files
/home/mak/trazos:                  649 XML-valid, 0 invalid
/home/mak/trazos:                  619 unique SHA-256 contents
/home/mak/trazos:                  29 duplicate-hash groups / 59 paths
/home/mak/flujo/iskvw/piel/trazos: 208 SVG files (plus _indice.json)
/home/mak/flujo/iskvw/piel/trazos: 193 unique SHA-256 contents
shared content hashes:             193
root paths sharing published content: 220
```

All 208 active projection files have matching content in the root corpus, but
the root corpus also contains 429 additional paths and duplicate variants.
The root directory has no active direct path references from the canonical
source/tool/test/data scope searched in this phase. The active code consumes
the named projection and its `_indice.json`, especially through the ISKVW
field/capa generators and tests.

## Meaning of the surfaces

| Surface | Role | Consumer | Language/platform | Disposition |
|---|---|---|---|---|
| `/home/mak/trazos` | large creative/source corpus and historical variants | no direct active path found | mixed human SVG; cross-platform | keep as source/evidence; no hash cleanup |
| `/home/mak/flujo/iskvw/piel/trazos` | filtered/published ISKVW projection | `_indice.json`, field/capa tools and tests | machine paths + visual SVG; Linux runtime | keep active projection |
| `flujo/svg` and `data/plano_simbolos` | named RD/templates and technical symbols | RD generators, plano readers and tests | Spanish-facing assets; cross-platform | keep separate by consumer |

The shared hashes prove derivation or publication overlap, not that the root
corpus is disposable. The 429 extra source/variant paths have no provenance
mapping yet, and duplicate SVG bytes may represent editable/source,
published, historical or generated roles.

## Validation

```text
tests/test_campo_filtro.py
tests/test_capas_iskvw.py
tests/test_svg_index_real.py
tests/test_plano_simbolos_catalogo.py
tests/test_svg_illustrator_integration.py
result: 39 passed, PYTEST_RC=0
```

The XML parse covered every root SVG. No renderer, hub, file upload, provider,
laser path or mutating generator was called. WIN and RD were untouched.

## Decision

Do not merge `/home/mak/trazos` into `flujo/iskvw/piel/trazos`, and do not
delete its duplicate hashes. The correct future operation is a provenance
crosswalk/index that records source, projection, delivery and variant roles;
only then can a named family receive a reversible quarantine decision.

## Rollback

No mutation occurred. The rollback is the unchanged original tree and active
projection.

## Next concrete action

Audit `/home/mak/bucle` statically from the physical root, then compare its
source/project role with canonical FLUJO consumers. Keep cultural source,
generated media, root installers, providers, XIO, n8n, workers, mutators and
Git operations gated.
