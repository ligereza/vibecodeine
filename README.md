<p align="center">
  <a href="https://github.com/ligereza/vibecodeine/">
    <img src="arte-ascii-readme.svg" alt="VIBE-CODEINE animated ASCII vessel" width="936">
  </a>
</p>

# VIBECODEINE / FLUJO
## DIMENSIONS OF ORDER

This repository is `ligereza/vibecodeine`.

**VIBECODEINE** is the artistic and technical body. **FLUJO** is the
local-first workspace. **DIMENSIONS OF ORDER** is the method for arranging
artwork, records, research, evidence, tools, memory, and decisions without
forcing every object into one permanent category.

The system serves one artist, graphic designer, VJ, and RD collaborator. It
connects personal work, client work, visual research, events, venues, VJ
records, design operations, and software. It is not a generic SaaS product.

The animated vessel is part of the artwork. Its double-cup geometry, ASCII
composition, color planes, layer relations, and motion are protected. Refresh
only its text layer with the existing generator:

```text
py tools/update_readme_svg.py
```

## Start Here

Read these files before changing the system:

```text
AGENTS.md
context/LAST_HANDOFF.md
CAPACIDADES.md
MAPA.md
```

Then verify the checkout and the measured runtime state:

```text
git status --short --branch
git branch -a
git log -5 --oneline
```

`context/LAST_HANDOFF.md` is the operational checkpoint. It contains the
current facts from MAK, completed circuits, failures, and one next action.
Old plans, raw logs, Downloads, and branch names are not authorities.

## Four Canonical Branches

Only these branches belong to the system:

```text
main   complete, reviewed, transferable system
mak    machine/inbox integration line and Linux MAK laboratory
rd     Reduciendo Dano institutional work
iskvw  artistic archive and public surface
```

No fifth branch is canonical. Preserve unique work before deleting an old
branch, compare its commit and files, and never reset the MAK checkout
blindly. The public `iskvw` archive is separate from research by default.

## Repository Map

```text
src/flujo/                  core package, CLI, and operational workflow
web/src/                    hub, department navigation, and visual surfaces
cultura/mak_plataforma/     ledger, batches, identity, routing, and gates
iskvw/                      archive, portfolio editor, and GTM projection
tools/                      existing maintenance and SVG/README utilities
projects/                   operational projects and visual experiments
xio/                        time, audio, event, and show data bridges
tests/                      focused verification for existing behavior
```

The portfolio editor is part of the MAK Hub, not an unrelated temporary
server. Its GTM/atlas surface is a projection over the archive, not a second
source of truth. It must keep registration, work, context, and relation
distinct.

## MAK and Departments

MAK is the runtime body and curator, not an automatic truth machine. Use the
Linux box for tedious scans and runtime checks; Windows is the director and
transport surface, not the default bulk-processing host.

```text
MAK       detects, organizes, proposes, and preserves uncertainty
Research  verifies external facts and primary sources
XIO       contributes time, audio, event, and venue traces when available
Faro      integrates durable system changes and directs promotion
iskvw     curates and publishes artistic surfaces
RD        prepares institutional outputs and evidence-backed deliverables
```

Artist, username, client, collaborator, event, festival, venue, producer,
location, date, and source are separate identities. A username is not an
artist by itself. A description is source material, not factual proof.
Stories are audiovisual records by default; posts and reels may be works or
records depending on evidence and human decision.

## Traceability Contract

All new work uses the existing `mak-work-v1` envelope and the existing ledger,
batches, discernment, identity graph, Capataz, and Hub. Do not create another
framework, database, graph, policy engine, or duplicate Python tool.

```text
work_id  parent_task  lane  purpose  format  created_at  provider
sources  evidence    status  owner  next_action  identity
```

The useful chain is:

```text
request -> identity -> format -> provider -> evidence -> criticism
         -> decision -> ledger -> human gate -> next action
```

The durable decisions are `hacer`, `revisar`, `refutar`, `archivar`, and
`descartar`. A report without identity is `legacy_unknown`; a claim without
evidence is not promoted. Rejected work remains traceable memory, not truth.

## Three Lanes

```text
OBRA      VIBE-CODEINE, SVG, animation, portfolio, archive, curation
TRABAJO   RD, grants, Fondart, clients, opportunities, events, design
SISTEMA   MAK, micelio, XIO, bridges, tools, providers, continuity, repair
```

Each lane keeps its proper output format. A curatorial reading is not an
investigative report, an opportunity is not an essay, and a record is not
silently converted into an artwork.

## Providers and Promotion

External models are bounded workers. They produce hypotheses, drafts, visual
observations, or classifications; they do not create truth automatically.

```text
AWS       visual evidence and image observation
Watsonx   research, hypotheses, and structured review
Ollama    local judging and cheap continuity
fallback  deterministic validation when a model fails or times out
```

Provider output stays isolated until the local gate and human review accept
it. Public, aesthetic, curatorial, and deletion decisions require a human
gate. A provider failure must become an explicit degraded state, never an
empty truth.

## Portfolio and Archive

The editor separates search, association, boards, triangulation,
classification, organization, and promotion. A single record may be viewed
through multiple lenses without copying the source file. The GTM atlas remains
stable during a human pass while the field learns from explicit decisions.

Evidence channels remain distinct: date, carousel, event, venue, artist,
client, semantic reading, audio, and process. A relation must retain its
source, evidence kind, uncertainty, and next action. Human selections and
rejections become learning signals; they never erase the original media.

## Verification

Run focused checks first, then the full suite when a coherent block is ready:

```text
node --check iskvw/mesa_montaje.js
py tools/update_readme_svg.py --check
py -m pytest -q
git diff --check
```

Record exact commands, measured MAK facts, failures, and the next action in
`context/LAST_HANDOFF.md` before ending a session. Commit and push only after
the requested gate is explicit and the four canonical branches can be
reconciled without losing work.
