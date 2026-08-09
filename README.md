<p align="center">
  <a href="https://github.com/ligereza/vibecodeine/">
    <img src="arte-ascii-readme.svg" alt="VIBE-CODEINE animated ASCII vessel" width="936">
  </a>
</p>

# VIBECODEINE / FLUJO
## DIMENSIONS OF ORDER

This repository is ligereza/vibecodeine.

**VIBECODEINE** is the artistic and technical body.
**FLUJO** is the local-first workspace.
**DIMENSIONS OF ORDER** is the method for organizing work, evidence, tools,
memory, and decisions.

The system serves one artist and graphic designer. It connects artwork,
portfolio, visual research, RD work, events, venues, VJ records, design
operations, and software. It is not a generic SaaS product and must remain
useful as the artist's practice changes.

The animated vessel above is part of the work. Its double-cup geometry, ASCII
composition, color planes, and motion are preserved as an artwork. The text
layer may be refreshed from this README with:

    py tools/update_readme_svg.py

## START HERE

Before changing anything, read in this order:

    AGENTS.md
    context/LAST_HANDOFF.md
    CAPACIDADES.md
    MAPA.md
    the relevant branch documents
    the files directly related to the task

Then inspect:

    git status --short --branch
    git branch -a
    git log -5 --oneline

Do not assume that an old report is true. Do not create a new tool before
searching for an existing one. Do not treat a generated document as evidence
by itself. The current state, measured MAK facts, unfinished work, and next
action live in context/LAST_HANDOFF.md.

## THE FOUR CANONICAL BRANCHES

Only these four branches belong to the system:

    main
    The complete and verified system. Only stable, reviewed and transferable
    work belongs here.

    mak
    The operational MAK inbox and laboratory. It receives work, research and
    experiments before promotion. MAK is also the Linux box on the local network.

    rd
    The Reduciendo Dano institutional line. It contains RD data, supplements,
    events, proposals, research and deliverables for the organization.

    iskvw
    The artistic archive and portfolio line. It contains curation, artwork, public
    archive and portfolio surfaces. Its current domain is temporary and must not
    become a permanent dependency.

No fifth branch is part of the system. A branch found on the MAK checkout may
be an old agent worktree; preserve unique work before reconciling or deleting
it. Never reset a remote checkout blindly.

## REPOSITORY MAP

    src/flujo/
    Core Python package, CLI and operational workflow.

    web/src/
    React/Vite hub, department navigation, editors and visual surfaces.

    cultura/
    Art research, visual experiments, SVG work and cultural tools.

    cultura/mak_plataforma/
    Ledger, batches, work identity, discernment, routing and promotion rules.

    tools/
    Existing maintenance, SVG, README and workflow utilities.

    projects/
    Operational projects, experiments, bridges and delegated work.

    xio/
    On-device Xiaomi controller for time, audio, event and show data.

    tests/
    Focused verification for the existing system. Read tests before inventing
    new behavior.

## MAK LINUX BOX

The Linux machine is the preferred place for tedious work. Use Windows as a
control surface and transport layer, not as the main research engine.

MAK services include:

    research
    codex
    plataforma
    hub

The Hub normally runs on :8900; research and codex are separate departments.
The box may use Watsonx, AWS, Groq, Cerebras, or Ollama when configured.
External models produce hypotheses, drafts, visual observations, or
classifications. They do not create truth automatically. Every external result
must remain traceable and must pass the local decision gate.

Never copy credentials into the repository, README, logs, or Downloads. The
provider environment belongs on MAK or the appropriate local runtime.

## WORK IDENTITY

Every task or product should preserve the existing mak-work-v1 envelope:

    work_id
    parent_task
    lane
    purpose
    format
    created_at
    provider
    sources
    evidence
    status
    next_action
    owner
    identity

The basic chain is:

    request
      -> identity
      -> correct format
      -> provider
      -> evidence
      -> criticism
      -> decision
      -> ledger
      -> human review
      -> next action

A report without identity is legacy_unknown. A claim without evidence is not
promoted. A duplicate is not new work. A rejected result remains memory, not
truth.

## THREE INITIAL LANES

### OBRA

VIBE-CODEINE, SVG, animation, portfolio, archive, curation, and visual
relationships.

### TRABAJO

RD, grants, Fondart, clients, opportunities, events, music, design, nursing,
and family context.

### SISTEMA

MAK, micelio, XIO, bridges, tools, memory, providers, continuity, and repair.

Each lane may have different formats. Do not force a curation into a research
report. Do not force an opportunity into an essay. Do not turn an audiovisual
record into an artwork without human or evidential support.

## DEPARTMENTS

    MAK detects, organizes and proposes.
    Research verifies external facts.
    XIO contributes time, audio, event and venue traces when real data exists.
    Faro/Codex integrates durable system changes.
    iskvw curates and publishes artistic surfaces.
    RD prepares institutional outputs.
    The human artist decides final meaning, selection and release.

Artist, username, client, collaborator, event, festival, venue, producer,
location, date, and source are separate identities. A username is not
automatically an artist. A description is not factual proof by itself.
Stories are records by default; posts and reels may be works or records.

## CURRENT TRACEABILITY BLOCK

The stable system is built around the existing ledger, batches, discernment,
identity graph, GTM projection, portfolio editor, and Hub. Do not create a
parallel framework or database.

The goal is not autonomous volume. The goal is an explainable result:

    what was received
    why it was processed
    what evidence supports it
    what remains uncertain
    what decision was made
    what must happen next

Current provider roles are bounded and replaceable:

    AWS      visual evidence and image observation
    Watsonx  research, hypotheses and structured review
    Ollama   local judging and cheap continuity
    Fallback deterministic rules when a model fails or times out

No provider can promote public material alone. Public, aesthetic, curatorial,
and deletion decisions require a human gate.

## PORTFOLIO AND ARCHIVE RULES

The portfolio editor lives inside the MAK Hub, not on an unrelated temporary
port. It separates search, association, boards, triangulation, organization,
and promotion. Its organism and GTM surfaces are projections over the archive,
not new sources of truth.

The public iskvw archive is separate from research by default. Research essays,
icons, and visual proposals enter the public surface only through an explicit
opt-in path. A story record keeps format=registro; it is not silently
converted into an artwork.

The future portfolio may relate semantic vectors, event dates, venues, artists,
clients, media, and process, but every relation must retain its evidence kind
and uncertainty. Human selections and rejections become traceable learning
signals; they do not erase the source file.

## ARTWORK RULE

arte-ascii-readme.svg is an artwork, not a disposable template. Preserve its
double-cup geometry, ASCII composition, color planes, layer relationships, and
intentional accidents. Refresh only its generated text layer unless the artist
explicitly reopens the visual design.

## LANGUAGE AND DATA

Code and technical documentation use English where practical. Human-facing RD
and iskvw products use correct Spanish. Machine keys, ids, slugs, paths, and
provider fields stay ASCII-safe. Do not remove accents from human-readable
values to satisfy a machine-key rule.

## DAILY COMMANDS

    py -m flujo app
    py -m flujo app --desktop
    py -m flujo verify
    py -m flujo health
    py -m flujo version

Python changes should be checked with the focused tests first. Do not waste a
session polling a long suite before the meaningful circuit is complete. At the
end of a session, update context/LAST_HANDOFF.md with measured facts, exact
commands, failures, user decisions, and one next action.

## THE CURRENT AUTONOMY CRITERION

The repository is not autonomous because it produces more. It is autonomous
when it can locate itself, choose the right format, preserve evidence,
criticize its own output, keep uncertainty visible, and leave a concrete next
action for the artist.
