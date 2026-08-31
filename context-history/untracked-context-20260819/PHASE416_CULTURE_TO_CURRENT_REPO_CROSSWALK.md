# Phase 416 — culture to current repository crosswalk

Date: 2026-08-15
Agent: LUNA principal
Scope: connect the cultural genealogy to the current MAK contracts and active
consumers, incorporating the user's clarification that Tilde is the source of
the language boundary. No source, data, artwork or Git state was modified.

## Tilde is the language boundary

The correct relation is:

```text
Tilde: marks carry meaning and can be lost
  -> ASCII/Windows incident: machine text must survive checkout safely
  -> language contract: new machine-facing code uses English ASCII
  -> human-facing RD/Portfolio material remains Spanish UTF-8
```

This is not a ban on Spanish in the repository. It is a two-layer contract:

| layer | current rule | evidence |
|---|---|---|
| machine-facing | English ASCII for new code, identifiers, filenames, config keys, tests, technical logs and operational metadata | `agents.md`, `docs/GLOSSARY.md` |
| human-facing | correct Spanish with diacritics for RD, Curatoria/Portfolio material and reports | `agents.md`, `tools/idioma.py`, `tools/validar_curaduria.py` |
| legacy machine names | preserve when existing consumers depend on them; rename only with the consumer | `tools/idioma.py`, `docs/GLOSSARY.md` |
| public data keys | stable ASCII IDs/keys; values may be Spanish UTF-8 | `src/flujo/plano/iconos.py`, `src/flujo/web/hub.py` |

`tools/idioma.py` is the current measuring/ratchet instrument. It detects new
Spanish comments/docstrings and declarations without accusing legitimate
Spanish product strings. `tools/validar_curaduria.py` separately guards UTF-8
mojibake and ASCII IDs. The repo therefore contains the Tilde idea as a live
engineering boundary, not only as a dossier.

## Current crosswalk

| cultural line | present-day repo function | active evidence | maturity |
|---|---|---|---|
| Tilde | language/encoding boundary and loss measurement | `tools/idioma.py`, `desktop/tilde_meter.py`, `projects/tilde/sobrevivencia.py`, `validar_curaduria.py` | active contract + instrument |
| ASCII/Borradura | detect damage caused by over-broad machine rules; ASCII-as-pattern technique | `projects/cultura/borradura_ascii/`, `iskvw/piel/campo/ASCII_REFERENCIA.md` | active cultural instrument / curated technique |
| Tapiz | turn code generation and whitespace into visual material | `projects/tapiz/vibecode/`, `tools/sala3d/`, curated SVGs | active visual library + pieces |
| Cauce | recognize recurrence, render whitespace as rivers and preserve marks | `projects/tapiz/vibecode/cauce.py`, `cauce_cauce.svg`, `cauce_sala3d.svg` | active Tapiz mode |
| Psicosis | keep uncertainty, provenance and incompatible readings explicit | `projects/cultura/psicosis_agente/`, `fila_cero.py`, `mecanismo_residuo.py`, Curatoria filters | prototype/cultural governance |
| Precursor | research and dossier framing for cultural/legal structures | `knowledge/dossiers/precursor.yaml`, `projects/cultura/dossiers/precursor.md` | dossier-first, no operational tool |
| Curatoria | ingest, classify, index and preserve chaotic source folders | Curatoria intake/index surfaces and portfolio catalogue | service slice to map |
| RD/VJ | turn event/venue facts into plans, riders, quotes and visual layouts | `src/flujo/plano/`, venue 3D/SCD, RD web consumers | active production slice |

## The present-day flow

```text
source material / user language
  -> Tilde boundary: preserve meaning, classify machine vs human text
  -> Curatoria: provenance, indexing and context
  -> Tapiz/Cauce: visual materialization of pattern, void and recurrence
  -> RD/VJ: operational layout, venue, screen/scenography and rider
  -> Portfolio: approved public projection in Spanish UTF-8
```

Psicosis acts as the epistemic guard across the flow: an index, venue datum,
scraped result or generated proposal must not be narrated as more certain than
its source. Precursor supplies cultural research framing where the material
needs historical/legal interpretation; it does not become an unsafe production
pipeline.

## Consequence for integration

The shared core is not one language and not one database. It is a contract of
`stable_ascii_id + UTF8_human_value + provenance + confidence + consumer`.
That same contract can join Curatoria folders, RD events, VJ venues and
portfolio cases without erasing the reason each project exists.

## Next action

For each active service slice, map its input language, stable IDs, provenance,
confidence, output language and consumer. Start with the shared venue/RD/VJ
slice and the Curatoria indexing slice; preserve cultural dossiers and
historical WIN material as lineage, not as duplicate runtime code.
