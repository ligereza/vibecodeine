# Markdown context master

Purpose: one navigable index for operational context, recovered sessions,
historical evidence and duplicate Markdown groups. Source files remain in
place; this file is the consolidation layer.

## Rules

- `context/` is operational continuity and technical evidence.
- `projects/cultura/` is idea/dossier material and may use human Spanish UTF-8.
- `WIN/`, worktrees, quarantine, Trash and vendor trees are source/evidence,
  not active owners.
- Exact duplicate content is represented once in this index; no source is
  deleted or overwritten.
- Similar but non-identical sessions require a diff and provenance decision.

## Canonical operational context

| role | canonical path | disposition |
|---|---|---|
| agent contract | `/home/mak/flujo/agents.md` | active authority |
| current handoff | `/home/mak/flujo/context/LAST_HANDOFF.md` | one active continuity file |
| phase evidence | `/home/mak/flujo/context/PHASE*.md` | archival audit records; see `context/PHASE_REPORTS_INDEX.md`; never active instructions |
| current architecture | `/home/mak/flujo/context/PHASE413_CROSS_DOMAIN_SERVICE_ARCHITECTURE.md` | service vision |
| current culture map | `/home/mak/flujo/context/PHASE416_CULTURE_TO_CURRENT_REPO_CROSSWALK.md` | language/idea crosswalk |

## Meaningful Markdown families

| family | source set | role and disposition |
|---|---|---|
| direction memory | `/home/mak/flujo/docs/recovered/claude_sessions_2026-08-12/raw/MEMORIA_DIRECCION.md` | human product direction and revenue hypotheses; source of intent, not an executable plan |
| architecture and capability | `/home/mak/flujo/MAPA.md`, `/home/mak/flujo/CAPACIDADES.md`, `/home/mak/flujo/PLAN.md` | current maps, measured capability surface and strategic backlog; reconcile against runtime before treating statements as current |
| RD editorial contract | `/home/mak/flujo/linea_editorial/v4.1.md` | active Spanish-facing RD visual/voice contract; separate from the machine-facing `projects/flujo/flujo.json` base |
| RD data and venue bridge | `/home/mak/flujo/docs/rd/DB_PRODUCTORAS_ESTADO.md`, `/home/mak/flujo/projects/plano/README.md`, `/home/mak/flujo/docs/HERRAMIENTAS_VISUALES.md` | operational documentation for catalog, venue/plano and visual consumers; keep databases and projections separate |
| opportunities and proposals | `/home/mak/flujo/docs/becas/`, `/home/mak/flujo/projects/cultura/dossiers/convocatorias_mak_ruta.md`, recovered Fondart extracts | research and proposal pipeline; candidate/unverified until primary source, eligibility and deadline are checked |
| raw conversation evidence | `/home/mak/flujo/.aider.chat.history.md`, `/home/mak/flujo/docs/recovered/` | provenance only; summarize durable decisions here, never use raw transcripts as runtime authority |
| RD research reports | `/home/mak/flujo/docs/rd/informes/`, selected `/home/mak/flujo/docs/becas/informes/` | generated research with sources and human-review debt; useful context, never legal/field authority by itself |
| VJ bridge specification | `/home/mak/flujo/tools/TAPIZ_RESOLUME_SPEC.md`, `/home/mak/flujo/docs/TAPIZ.md` | human/operator specification for OSC and visual material; spec-only unless its input/output contract is verified |

The family table is a navigation layer, not a claim that every statement in a
source is still true. Runtime checks, provenance and consumer evidence remain
the authority for integration.

### Editorial version lineage

`linea_editorial/v3.md`, `v4.md` and `v4.1.md` have distinct SHA-256 values;
they are revisions, not exact duplicates. `v4.1.md` is the current RD-facing
contract identified by the existing documentation, while v3/v4 remain useful
historical design lineage. Do not merge them by filename or retain all three
as runtime configuration.

### Bridge and research evidence

The `puente/` Markdown family is a cultural/theoretical bridge. It has no
runtime consumer and remains dossier/theory material. The recovered
Firecrawl/Crawl4AI Markdown under `docs/recovered/` is research evidence for
Curatoria and opportunity discovery; it is not an authorization to run a
provider, install a package or promote a scraped claim.

## Remaining Markdown boundary

The full physical scan found Markdown outside the canonical tree in large
historical/protected surfaces: `WIN`, `rollback`, `quarantine`, `research`,
`actions-runner`, `flujo-deploy`, `vibecodeine`, local caches and recovered
inboxes. Those files remain evidence, rollback, projection or external
research, not competing active owners. The canonical families already have a
master disposition; future work on an individual file must be driven by a
consumer or a provenance question, not by size alone.

## Exact duplicate groups

### `corpus_olvido/corpus.md`

SHA-256: `22d6671915d29097142b8acb37bb19df4413329c0f13c3a562e05bf4cd3908fe`

Seven physical copies share exactly 1,542,378 bytes. Active representative:

`/home/mak/flujo/projects/cultura/corpus_olvido/corpus.md`

Other copies are in `flujo-deploy`, `vibecodeine`, `actions-runner`, two
quarantined worktrees and `WIN`. Keep them as projections/history until their
owners are retired; the content is already consolidated by this index.

## Related but non-identical groups

### Recovered `nombre-cauce.md`

Three files describe the 2026-07-04 naming session. The second and third have
the same normalized SHA-256
`602b65689f3c83b85dab35fa897f2f012e0406302912e1037595e3900ae1ff08`.
The `WIN/flujo` version has normalized SHA-256
`53f80d8166ced343c8c3816a0eb0c4f734823de63cd161c2ab142aa43c62c4c2` and
differs by 546 unified-diff lines. Consolidation status:
`COMMON_SESSION_SUMMARY_REQUIRED; SOURCE_VARIANTS_PRESERVED`.

### Handoff family

`/home/mak/flujo/context/LAST_HANDOFF.md` is the active owner. Files in
`/home/mak/.local/share/Trash/files/LAST_HANDOFF*.md` are historical snapshots,
not competing handoffs. They must not be reintroduced into the active path.

## Context classes

| class | examples | action |
|---|---|---|
| active operational | `agents.md`, `context/LAST_HANDOFF.md` | current authority and continuity only |
| archival phase evidence | `context/PHASE*.md/.csv/.json` | preserve and classify via `context/PHASE_REPORTS_INDEX.md`; never treat `Next concrete action` inside a phase file as current |
| recovered session | `docs/recovered/`, `WIN/claude_sesiones/` | summarize provenance; preserve raw |
| director scratch | `WIN/flujo/_logs/cauce_director/` | extract durable decisions; keep raw logs |
| historical Windows | `/home/mak/WIN/**/*.md` | read-only genealogy |
| reversible evidence | `context/quarantine/`, `/home/mak/quarantine/` | preserve manifests/rollback |
| user trash snapshots | `/home/mak/.local/share/Trash/files/` | do not treat as active context |
| vendor/dependency | `.venvs`, `node_modules`, plugin caches, licenses/changelogs | exclude from project idea consolidation |

## Next consolidation rule

Create a short master summary for each coherent idea family, link every source,
and mark each statement as active, prototype, dossier-only, historical or
unverified. Do not merge by filename, age or language alone.

## HTML owner map

| surface | source/owner | consumer | status |
|---|---|---|---|
| `context/flujo_hub.html`, `context/plano_demo.html`, `context/svg_visualizer.html` | one Vite build from `web/src`, copied by `web/scripts/copy-context.mjs` | `src/flujo/web/hub.py` path aliases | active generated family; parity gate open |
| `web/dist-rd/rd.html` -> `dist_compartir/herramientas_rd.html` | `web/rd.html` + `mainRd.tsx` + `vite.rd.config.ts` + copy script | standalone RD tools | separate RD projection; build gate open |
| `web/dist-plano/plano.html` -> `dist_compartir/plano_rd.html` | `web/plano.html` + `mainPlano.tsx` + `vite.plano.config.ts` + copy script | standalone RD/VJ plano | separate plano projection; build gate open |
| `web/public/mapping.html` -> `web/dist*/mapping.html`, `context/mapping.html` | Vite public asset + `MappingTool.tsx` + `copy-context.mjs` | VJ mapping/rigging console | one source with five byte-identical consumer projections |
| `web/venues/index.html` | generated by `tools/venue.py sitio` from `data/venues/*.json` | open venue catalogue/crosswalk | regenerated; separate from RD `knowledge/venues` |
| `iskvw/**` | portfolio skin/editor and publication workflow | public portfolio | separate public projection; publish gate open |
| `datadrops/**` | generated RD deliverables | producer/client handoff | protected products; preserve variants |

The three context aliases are intentionally one application selected by
pathname. RD and Plano standalone bundles are intentionally separate entries;
their source comments explicitly avoid importing the full hub. This is a
logical consolidation, not a physical flattening of files.

### Venue/Portfolio bridge truth

`web/venues/index.html` is a generated offline open-base catalogue. Before
Phase 428 it was stale and embedded only two examples; it is now regenerated
from the canonical `data/venues/*.json` registry and contains the three current
public records. It remains separate from the RD `knowledge/venues` catalogue.
The actual SCD venue consumer is
`iskvw/piel/venue/index.html`, which loads `data/venues/scd-plaza-egana.json`
or a `?venue=<id>` registry entry. The portfolio field activates that venue
link only when `iskvw/datos/tablero.json` declares `mejoras.venue3d=true`.
Therefore the public venue demo and the portfolio venue skin must not be
treated as one database or one interchangeable HTML file.

### Role correction: OpenKlub

User-confirmed role correction: `OpenKlub` is a producer/brand, not a venue.
The conflated `knowledge/venues/openklub.yaml` was reversibly quarantined in
Phase 430 and the generated `data/rd.db` no longer contains `venues.openklub`.
`productora_venues` still records the unresolved candidate `Central Cultural`
with no venue ID. `Espacio Riesco` remains a venue and may be referenced by
producer/event relations.

### Role correction: Paralelo 89 / FRVR

`paralelo_89` was an inferred venue created from the filename
`FRVR.PARALELO89.png`, not from venue metadata. The image identifies `Sala
Metronomo` as the event place, `FRVR` as the user-confirmed DJ headliner and
`Paralelo 86` in the artist lineup. The official Paralelo 86 site supports the
DJ/producer interpretation of that lineup name; no reliable public source was
found for `Paralelo 89` as a venue.
The YAML was moved reversibly to
`context/quarantine/phase431_paralelo89_role_correction/`. `FRVR` remains in
the compatibility `data/productoras` store with `tipo: artist_dj` and
`headliner: true`, while keeping Sala Metronomo as an unresolved event venue
with `venue_id: null`. The organizer remains unknown. This prevents a
filename typo or artist label from becoming a technical venue or a producer.

### Research triangulation rule

Incomplete event records are resolved by orthogonal keys: date from artist +
producer + venue; producer from artist + date + venue; artist from date +
producer + venue; and venue from date + artist + producer. Research records
raw queries, URLs, retrieval date, matched fields, confidence and conflicts.
OCR, filename repetition or a single unverified result cannot promote an
entity into the canonical venue/productora/artist tables.
