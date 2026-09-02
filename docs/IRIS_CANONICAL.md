# IRIS -- canonical definition of the Mesa de Montaje

> Written 2026-09-02 on the operator's direction. IRIS is a NAME for what
> already exists in MAK, not a new application. Anyone who reads this document
> and starts building a second surface, a second database, a second corpus or a
> second definition of "obra" has misread it.
>
> Authority order for this subject: the operator -> `CLAUDE.md` ->
> `context/LAST_HANDOFF.md` -> `docs/PORTAFOLIO_PRODUCCION.md` and
> `context/PLAN_MESA_DE_MONTAJE.md` (the two documents that hold the theory) ->
> this file. Where this file and those two disagree, they win and this file is
> wrong.

## 1. What IRIS is

IRIS is the visual table (`Mesa de Montaje`) through which a person walks their
own archive, sees why the system proposes a relation, and decides. It is the
PORTAFOLIO surface of the MAK Hub on port 8900, plus the local engine behind
it.

It is an epistemic instrument, not a catalogue, a dashboard or a decorative
graph. Its value is in what it refuses to assert.

## 1-bis. What IRIS is NOT: iskvw.cl (operator's correction, 2026-09-02)

Two things share a surface and must not be conflated. This agent conflated
them, so the boundary is written here before anything else.

**`iskvw/` is iskvw.cl**, the artist's published portfolio SITE. Three layers
declared in `iskvw/CONTRATO.md`: `datos/archivo.json` is the published content,
`CONTRATO.md` is what any skin must honour, and `piel/<name>/` is the skin,
replaceable whole. `datos/campo.json` and `datos/obras.json` are FALLBACKS the
live skin asks for only if `archivo.json` is missing. It is published by
`.github/workflows/publicar_iskvw.yml`, which uploads `iskvw/` and nothing
else. **It considers obras only**, and its 219-work scope is the operator's
explicit decision from #355 (2026-07-27): posts and reels, never
`archived_posts/` or `other/`, because publishing what someone archived
reverses a decision they made.

**IRIS is the PORTAFOLIO surface of the MAK Hub**, which grew out of
`iskvw/editor.html` -- the curation panel -- and then joined DIMENSIONES DEL
ORDEN. Today the Hub still MOUNTS that panel (`/portafolio/` ->
`iskvw/editor.html`, `PORTFOLIO_ROOT` = `/home/mak/iskvw`), which is the
historical join and the reason the two look like one thing. But the engine
behind IRIS -- `copilot.py`, the 35 `/api/portfolio/*` routes, the eight
layers, the five verbs, the evidence states, the GTM atlas and the ordering
field -- works on a richer model than a list of obras: records, works,
context and relations, with claims that carry provenance and a state.

**And it is DORMANT.** The operator's correction of 2026-09-02: iskvw.cl has
not published anything in about a month and is not in use. Its publish
workflow exists and is explicit, but nothing is being served from recent work.
So `iskvw/` is a parked surface with a real contract, not a live product.

The consequence, stated plainly: **the obras-only version is the older one, and
it is asleep. Editing `iskvw/datos/*` or `iskvw/piel/*` is not working on
IRIS.** On 2026-09-02 this agent read a red test suite, traced it to
`campo.json`, re-ran the capas and the animated pieces, and then -- the worse
error -- called that damage to a live published product. It was not. Measure
whether a surface is in use before calling it a product at risk. The lesson is
the boundary and the dormancy, not the revert.

## 2. The problem it answers

An archive of digital art keeps bytes, not decisions. `finalfinal.mp4`
preserves the file and loses the judgement that made it a work, a version or a
discard. Recovering that judgement is an inverse problem that is not
identifiable: several distinct histories produce the same stored evidence.

    E = g(W)      g is not invertible
    g(W1) = g(W2) = E   ->  W is not recoverable from E alone

So IRIS does not compute the true order. It exposes DEFENSIBLE orders and keeps
visible which part came from the archive, which part is an inference, and which
part belongs only to the author.

## 3. The four levels

Declared in `context/PLAN_MESA_DE_MONTAJE.md` and carried by the ledger:

| level | what it holds |
|---|---|
| `record` | the original file as found, with its own provenance |
| `work` | the curatorial object that may emerge from several records |
| `context` | conditions of production: event, venue, client, collaborators |
| `relation` | a still-open link between any of the above |

A stable `source_id` plus `provenance`, `confidence`, `permission` and
`consumer` lets one piece appear in several readings without duplicating the
file and without erasing its history.

## 4. The engine sequence

    input -> event -> state -> evidence -> proposal -> human_decision
          -> ledger -> optional_adaptation

The engine is not the visual surface and is not a conversational agent. It
processes signals, builds state, keeps evidence and emits explicit proposals.
`optional_adaptation` activates only when an independent evaluation shows it
beats the baseline.

Ordering a node is not a curatorial decision. Accepting or rejecting a
hypothesis is. Only the second reaches the ledger as a decision.

## 5. The four invariants

These are the promises the surface makes. They were already enforced, but
scattered across eight test files, so no single failure said "IRIS stopped
being honest". `tests/test_iris_invariants.py` (10 tests, lane `mak`) now names
them in one place.

| invariant | where it lives | how it is enforced |
|---|---|---|
| replay never promotes its own output | `copilot.replay_ordering_evaluation` | returns `promotion: "none"`, `next_action: "human_review"`, and does not mutate the corpus it measures |
| a learned metric activates only on measured gain | `copilot._stable_ordering_surface` | strict inequality on accuracy OR macro-recall; otherwise weights fall back to identity and the profile records `activation: "held_out_no_replay_gain"`, `rejection_reason: "no_replay_gain"` |
| the field does not move the atlas | same | `field.moves_geometry` is `False`; the atlas keeps `stable_during_pass` and the item set is unchanged |
| every machine output is a candidate | `copilot.active_ordering_seed`, `ledger.validate_item` | every seeded row carries `status: "human_candidate"`; a portfolio record without a declared action from `ACTION_BY_DOMAIN["portfolio"]` fails validation |

Activation is not promotion. Even when the pair metric earns activation, the
comparison still reports `promotion: "none"`: the metric may be used, the
answer it produces may not become a label.

## 6. Function map -- implemented, experimental, absent

Measured on the MAK checkout, 2026-09-02.

### Implemented and live

| piece | evidence |
|---|---|
| PORTAFOLIO surface of the Hub | `cultura/mak_plataforma/hub.py`, route `/portafolio/` -> `iskvw/editor.html`, 35 distinct `/api/portfolio/*` route names |
| local ordering engine | `cultura/mak_plataforma/copilot.py`, 1820 lines, 46 module-level functions, standard library only, no model provider |
| declared contracts | `faro-gtm-map-v1`, `faro-portfolio-atlas-v1`, `faro-ordering-field-v2`, `faro-ordering-replay-v1`, `faro-curatorial-inference-v1`, `faro-portfolio-vision-v1` |
| latent map | elastic rectangular grid, `GTM_DIMENSIONS = 32`, fit sampled above `GTM_FIT_LIMIT = 1024` |
| triage vocabulary | `ORDER_LABELS = ("work", "record", "review", "discard")` |
| active learning seed | `active_ordering_seed`, selection by uncertainty, coverage gap and spatial diversity, pool capped at 512 |
| append-only ledger | `cultura/mak_plataforma/ledger.py`, 6 item types, 8 domains, per-domain allowed actions, identity envelope `mak-identity-v1` |
| mounted curation panel | `/portafolio/` serves `iskvw/editor.html` with `PORTFOLIO_ROOT` defaulting to `/home/mak/iskvw` |
| test coverage | 21 files / 299 tests in the portfolio-archive family, plus 10 invariant tests |

### Experimental (works, not load-bearing)

- The learned pair metric. On the corpus measured 2026-08-09 it TIED the
  baseline (accuracy 0.857143 against macro-recall 0.859091 over 21 labels and
  221 pairs) and was retained without activation. It is a hypothesis with a
  negative result on record, not a feature.
- External challengers. Watsonx answered 1/21 and AWS 9/21 against 85.7% local
  on the same held-out subset. They are isolated as challengers and cannot
  promote a label.
- Vision features (`normalize_vision`) enter as weak evidence only.

### Absent, and deliberately so

- No automatic publication. Publication requires a human gate
  (`requires_human_gate`).
- No authorship claim from file evidence. `es_mio` and `hice_esta_parte` cap at
  `candidate` without a third-party receipt.
- No exposure of production in the Hub. `docs/PORTAFOLIO_PRODUCCION.md` section
  15 records this as a reasoned decision, not an omission.
- No universal ordering tool for every domain. Named as an anti-goal in
  `curatoria_inbox/funding-lab/JARDINES_INTERPRETATIVOS.md`.

### Absent and unresolved

- Three independent portfolio implementations with three incompatible
  definitions of "obra" (recorded in `docs/AUTORIDAD.md`).
- Four copies of `editor.html` on the machine.
- `POST /api/portfolio/dispatch` has no measured reader.
- The learning loop is blocked on human decisions, not on code.

## 7. Where the pieces physically live

The 2026-09-02 separation put MAK at `/home/mak` and FLUJO at
`/home/mak/flujo`. The consequence for IRIS, measured today: the portfolio
COMPILE and RENDER chain went to FLUJO while MAK's registry still claimed it.

- IRIS surface and engine: MAK (`cultura/mak_plataforma/`). The mounted
  curation panel and the published site live in `iskvw/` and are a
  different product -- see section 1-bis.
- Compile, render, opportunity fit: FLUJO (`flujo/tools/`, 35 tools, listed in
  `CAPACIDADES.md` section 5-quater).
- Knowledge layer: FLUJO (`flujo/src/flujo/knowledge/`), consumed by MAK tools
  through `FLUJO_SOURCE_ROOT` (default `/home/mak/flujo/src`). The retired
  dotted spelling `from src.flujo.` is now a ratchet in
  `tools/release_gate.py`.

## 8. What a future consumer may take

The ecosystem projects (LUCIDA, VIZZ, PUPILA, XIO, MOSAIK, CODEINE) are
ARCHITECTURAL and FUTURE. They are not current dependencies. No agent working
on MAK clones, imports or modifies them, and no second Hub, database, corpus or
portfolio definition is created to make a hypothetical integration easier.

What may be consumed later, through a contract and nothing else:

| contract | what it carries | what it never carries |
|---|---|---|
| `faro-portfolio-atlas-v1` | topology id, grid, stability flag | no file bytes, no private corpus |
| `faro-ordering-field-v2` | anchors, uncertainty, activation state | no promoted label |
| `faro-ordering-replay-v1` | evaluation, abstention apart from error | no promotion |
| `mak-identity-v1` | stable `source_id`, declared entities | no personal data that never entered as a product |

The shared surface principle, for every one of them: `overlay_only`,
`reversible`, `explains_why`, `host_untouched`.

## 9. Non-goals

IRIS does not decide which order was the true one. It does not claim authorship
from file evidence. It does not publish by itself. It does not accept NEW input
carrying personal data -- already-produced material may be re-read and
re-measured, which is the operator's correction of 2026-07-31.

## 10. Unknowns

- UNKNOWN: whether human decision curves the metric enough to generalize to a
  second archive. The one measurement available is a tie.
- RESOLVED 2026-09-02: the Fondart Regional line closes **9 September 2026 at
  15:00 Santiago**, extended to 16 September only for projects belonging to
  Arica y Parinacota, Tarapaca, Antofagasta and Atacama. The local bases PDF
  was verified sha256-identical to the live one.
- UNKNOWN: whether the applicant's trajectory counts as "primera obra
  artistica". Anexo 1 for 2027 is not published on the line's page and the 2024
  Anexo 1 does not define the term. It changes the selection order (two
  reserved slots per discipline), and it is the operator's fact to declare, not
  an inference to make from the archive.
- KNOWN GAP: the materialized product view declares 11534 internal assets and
  **0 assets with explicit public eligibility**, while the bases allow
  reference links inside a document only if they are live and key-free at
  evaluation time. Nothing is currently cleared for external view.

Retirement of this document: when the three portfolio implementations collapse
into one and the function map can be generated from the tree instead of
written by hand.
