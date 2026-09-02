# AGENTS.md - Faro operating contract

This is the fast entry point for a fresh agent. Read it first, then read
`context/LAST_HANDOFF.md`. Do not reconstruct state from old plans, raw model
logs, Downloads, or chat memory.

## Authority and identity

1. Direct user instruction.
2. This file.
3. `context/LAST_HANDOFF.md`.
4. `CAPACIDADES.md` and `MAPA.md`.
5. Area-specific documentation and raw logs.

The current director is **Faro/Codex**. `Cauce` and `Claude` in older files are
historical names, not current instructions. The assistant speaks Spanish to
the user. Operational docs and code use English/ASCII where practical; human
facing RD and iskvw products keep correct Spanish and diacritics. Never strip
accents from human-readable values merely to make machine data ASCII.

## Non-negotiable rules

- The user is the artistic authority, not the technical operator. Decide
  technical paths directly; ask only about taste, meaning, authorship, or an
  unresolved factual relation.
- Work in large, coherent blocks. Do not spend the session on tiny patches,
  repeated CI polling, watchers, or cosmetic explanations.
- Do not use Codex subagents. MAK models are external workers only when a
  durable repo/system path exists for their output.
- Use the Linux MAK box for tedious scans and runtime checks. Windows is the
  director workspace and transport surface, not the default bulk-processing
  host.
- Use Watsonx/AWS only in bounded, evidence-backed batches. Outputs are
  candidates until the local judge and the human gate accept them.
- Never put credentials, tokens, private exports, or new artifacts in
  `Downloads`. Director logs belong in
  `C:\IA\flujo\_logs\cauce_director\20260805\`.
- Do not create another framework, ledger, graph, policy engine, or duplicate
  Python tool before checking the existing implementation.
- Do not delete historical work because it is wrong. Classify it as unknown,
  duplicate, rejected, archived, or candidate; preserve evidence and source.
- Do not commit, push, merge, delete branches, delete tags, or reset a checkout
  unless the user explicitly requests that operation in the current session.

## Authority, organisms, nodes, and Git transport

The authority hierarchy is explicit:

1. Physical/local material surfaces on Windows and the MAK Linux computer:
   files, databases, memories, services, mounted storage, and generated
   outputs. These surfaces determine what exists and what is current.
2. The transversal catalog and coordination layer: it indexes material where
   it lives and records IDs, locations, hashes, provenance, relations, owner,
   status, and transport eligibility. It references sovereign data; it does
   not absorb or replace it.
3. Git: a reviewed reproducibility and publication projection. Git history is
   useful transport evidence, but it never decides what exists in Windows or
   MAK and is not the complete runtime inventory.

There are three sovereign organisms:

- `MAK`: computational producer, curator, researcher, and coordinator.
- `RD` / Reduciendo Dano: NGO with its own sanitary, ethical, legal, and
  publication governance.
- `Portfolio` / ISKVW: the artist's archive with its own authorial and human
  governance.

Windows and the MAK computer are physical nodes, not organisms or domains.
Either node may host material belonging to any organism. Capabilities are
replaceable tools; products are derived outputs; transport manifests describe
how selected material moves between surfaces. MAK may produce research or
curation for itself, RD, Portfolio, or a transversal relation. Producer,
owner, subject domain, final authority, status, visibility, and evidence must
remain separate.

The target data architecture is one logical knowledge database, not one
undifferentiated table. Its bounded schemas are `core` (identity, context,
provenance), `mak` (operations, research, curation), `rd` (scientific, field,
safety), `portfolio` (works, records, authorial curation), `relations` (typed
cross-domain links), `products` (publication projections), and `audit`.
Every assertion and relationship carries source/evidence, producer, owner,
confidence/status, visibility, and timestamp/version. Raw and binary material
remains on Windows, MAK, or mounted storage; the knowledge database stores
its URI and hash.

This is a target architecture, not the current physical state. The measured
Windows enriched RD SQLite is a read-only `CANDIDATE_AUTHORITY` migration
input, not an established system of record; the measured MAK reduced SQLite
is a read-only `LEGACY_PROJECTION`. Portfolio has no separate configured DB
and remains `NOT_CONFIGURED` as a standalone database because Portfolio will
be a schema in the logical database. Local SQLite files are migration inputs,
caches, or projections. A single primary writer is the intended end state;
bidirectional writes are prohibited until reconciliation defines a writer and
versioned sync direction. Search and vector indexes are derived and
rebuildable, never knowledge authority.

Two operational branches, each a physical checkout (2026-09-02):

- `FLUJO` (this one): the portable motor. `/home/mak/flujo` is its checkout:
  CLI, Hub, packaging, the `flujo` lane. It installs and runs without the MAK
  tree; the box layer is an optional peer.
- `MAK`: the Linux box. `/home/mak` is its checkout: departments, services,
  Hub, box tooling, the `mak` and `integration` lanes. It consumes this motor
  from `/home/mak/flujo/src`.
- `main` and `historia`: historical. Not runtime, not deployment targets, no CI
  trigger.
- `.claude/worktrees`: never runtime.
- `dependabot/*`: temporary automated dependency-update branches using the
  same gate.

Each operational branch pushes its own ref. Nothing returns through `main`.

The old refs `mak`, `rd`, `iskvw`, `mejoras`, and `mak-svg` are
transition/history refs. Preserve them until their contents are reconciled and
a separate cleanup decision is made; do not create new work there. `mak-svg`
is a historical SVG experiment, not a permanent artistic line. No mass folder
move is implied: logical indexing and an explicit transport manifest precede
any physical migration or Git promotion.

Verify the checkout before editing. The Linux box may have an old branch even
when Windows has the correct `main` ref. Do not reset or clean that box
blindly: preserve its work, compare hashes, then reconcile deliberately.

## System boundaries

- MAK is a runtime body and curator, not an automatic truth machine.
- `story_record` is an audiovisual record, not automatically an artwork.
- Artist, username, client, collaborator, event, festival, venue, producer,
  location, and source are separate identities. Do not infer one from a bare
  description or username.
- The common work envelope is `mak-work-v1`; keep `work_id`, identity, lane,
  purpose, format, evidence, provider, status, owner, and next action together.
- Existing decisions are `hacer`, `revisar`, `refutar`, `archivar`, and
  `descartar`. Public promotion always requires a human gate.
- Existing routing is enough: AWS for visual evidence, Watsonx for research or
  hypotheses, Ollama for local judging, and deterministic fallback when a
  model fails. Never let a provider failure become an empty truth.
- The portfolio editor, GTM projection, identity graph, ledger, Capataz,
  `tandas.py`, `discernment.py`, and `contrato_archivo.py` are connected. Extend
  them; do not build a parallel UI or data store.
- The only operational portfolio surface is `/portafolio/`, the current
  GTM/map editor served from the MAK checkout under `/home/mak/flujo/iskvw`.
  Legacy list/card or older editor surfaces are historical references: do not
  edit them, deploy them, or use them as evidence of current behavior.
- Before changing portfolio UI, verify with a command that `/portafolio/` is
  the served route and identify the exact `MAK_PORTFOLIO_ROOT` file and served
  asset hash. If the checkout, runtime, handoff, and served asset disagree,
  reconcile the discrepancy first; never choose an editor by filename alone.
- README/SVG geometry is protected. The user explicitly reopened the README
  text layer on 2026-08-09; update text through the existing generator only.
  The canonical `arte-ascii-readme.svg` must retain its `viewBox`, 30-frame /
  9-second playback, frame order, masks, `readme-source-static`, and playback
  delays. The canonical vessel currently contains 150 masks and 100 `tspan`
  elements; any experiment involving `clipPath`, remapped frames, or altered
  timing belongs outside `main`; use a temporary `codex/*` worktree for
  experiments. Do not redesign the
  vessel without a new artistic instruction. Domain migration is later than
  archive separation, export independence, and a stable public surface.

## Required continuation

Before asking a question or changing code:

1. Read `context/LAST_HANDOFF.md` completely.
2. Verify the specific local or MAK fact with grep, git, endpoint, or process
   inspection. Do not trust a stale sentence just because it is in a document.
3. Choose one meaningful vertical circuit, not a broad scan of all 7,044
   portfolio records.
4. Record the result, measured command, failure, and next action in the
   handoff before ending the session.
5. If the handoff contains stale operational facts, update the facts after
   verification; preserve them only as dated historical evidence.

The next agent must begin with the `Next action` section of the handoff. Raw
logs are evidence, not instructions. Historical plans are reference only:
`PLAN.md`, `PLAN_ANUAL_2026-2027.md`, `PROYECCION.md`, and
`context/PLAN_CIERRE_PRE_COMPACT.md` must not be treated as active checklists.
