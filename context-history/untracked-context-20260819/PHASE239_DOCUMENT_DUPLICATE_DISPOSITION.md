# Phase 239 — Document duplicate disposition

## Read-only scan

The bounded scan covered 4,143 small text/metadata files in active department
surfaces and found 99 exact-hash groups covering 334 paths. Hash equality was
used only as a candidate signal; no document was removed or overwritten.

## Disposition classes

| Family | Evidence | Decision |
|---|---|---|
| Research corpus captures | repeated `.txt`/`.tables.json` under dated `fondart-*` runs | preserve as run/evidence history; they are not interchangeable source documents |
| Research archive reports | repeated dated reports under `research/informes/archive` | preserve provenance/date; no merge without editorial authority |
| Research source/runtime docs | `cultura/mak_research/*` and `/home/mak/research/*` exact pairs | canonical source plus runtime projection; retain runtime path |
| Platform source/runtime docs | `cultura/mak_plataforma/*` and `/home/mak/plataforma/*` exact pairs | canonical owner plus runtime projection; see Phase 238 |
| Curatoria candidate outputs | exact pairs `/home/mak/curatoria/db/*` and `/home/mak/flujo/docs/rd/candidatos_curatoria/*` | keep both for now: runtime evidence is older, while `tools/gen_propuestas_rd.py` defaults to the FLUJO docs path |
| Codex/Cultura projections | exact deploy docs, services and motor metadata | preserve source/runtime consumer paths |
| Generated director results | repeated `aws-result.json`/`ollama-result.json` and raw analysis | preserve generated evidence; never hash-delete output history |

## Consumer evidence

`/home/mak/flujo/tools/gen_propuestas_rd.py` explicitly consumes
`docs/rd/candidatos_curatoria/candidatos_db.jsonl`; the runtime
`/home/mak/curatoria/db` copy has older timestamps and no literal active code
reference in the bounded search. That is a candidate for future archival, not a
safe deletion today because it is generated curation evidence and its
provenance may be needed for comparison.

## Decision

Objective 9 advances to `CLASSIFIED_BY_PROVENANCE_AND_CONSUMER`. The remaining
duplicates are evidence/projection families, not confirmed garbage. Documents
will be fused by canonical ownership and explicit readers, not by deleting
equal bytes.

## Next concrete action

Review the 20 divergent Platform files one by one only where a real consumer
exists. Keep all document families untouched unless an exact path-specific
quarantine has a consumer proof and inverse move.
