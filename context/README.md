# context/ — daily workspace and single checkpoint

This folder holds two different things, and mixing them up is what used to go
wrong:

1. **The state of the work** — one file, `LAST_HANDOFF.md`.
2. **The compiled UI of the app** — the `.html` files, which are build output
   and are never edited by hand.

The public-safe artistic direction template is `artist_context.example.json`.
The user's private profile may live in `artist_context.local.json`; it is
ignored and must never be committed.

## The single checkpoint

`LAST_HANDOFF.md` is the ONLY state file. There used to be seven competing ones
(SESSION_STATE, PLAN_SIGUIENTE_AGENTE, PLAN_SEMANAL_OPUS, ORQUESTACION_SUCESOR,
WALKTHROUGH, failed-handoff and this README), none of them saying which one
ruled, so every agent rebuilt the state from scratch and asked the user things he
had already answered. They were merged on 2026-07-26; the others live on in git
history and in `docs/handoffs/archive/`.

It stores ANSWERS, not questions: when the user decides something it gets written
there in the same session and stops showing up as pending.

## Authority and repository topology

The authority order is: physical/local material surfaces on Windows and the
MAK Linux computer; the transversal catalog and coordination layer; and the
reviewed Git projection. Windows and MAK determine what files, databases,
memories, services, mounted material, and generated outputs exist. The catalog
indexes those surfaces with IDs, locations, hashes, provenance, relations,
owners, statuses, and transport eligibility; it references sovereign data and
does not absorb it. Git records selected reproducible code and approved
projections, but it never decides local existence or runtime truth.

MAK, RD / Reduciendo Dano, and Portfolio / ISKVW are sovereign organisms.
Windows and MAK Linux are physical nodes, not domains or organisms. The target
is one logical knowledge database with bounded schemas for core, MAK, RD,
Portfolio, typed relations, products, and audit; each assertion retains
evidence, producer, owner, confidence/status, visibility, and version. Raw
material remains on its physical node or mount and is referenced by URI/hash.
Data, Capabilities, Products, Operations, and Tests may be distributed across
both nodes and selected Git projections. New changes use temporary `codex/*`
worktrees from `main`; `dependabot/*` is temporary and follows the same gate.

This is a target, not current database state. The Windows enriched RD SQLite
is a read-only `CANDIDATE_AUTHORITY` migration input; the MAK reduced SQLite
is a read-only `LEGACY_PROJECTION`; neither is yet the logical system of
record. Portfolio DB is `NOT_CONFIGURED` as a separate DB because Portfolio
belongs in the target schema. A single primary writer and explicit versioned
sync direction remain reconciliation outputs; no bidirectional writes are
allowed. Search/vector indexes are derived and rebuildable.

The old `mak`, `rd`, `iskvw`, `mejoras`, and `mak-svg` refs are transition or
history surfaces awaiting explicit reconciliation. Runtime mirrors, databases,
memories, and generated products remain provenance-separated and require an
explicit transport manifest and promotion gate before any projection or
physical migration.

## The daily entry point

```bash
py -m flujo app             # serves the hub with live data
py -m flujo app --desktop   # native window, no browser chrome
```

The `.html` files here are the app's compiled interface, produced by
`cd web && npm run build:context`. Opening one directly still works as a static
fallback with mock data, which is useful when the backend is not running.

- `flujo_hub.html` — the main workspace, and the daily center.
- `plano_demo.html` — interactive floor plan, rider and costs.
- `svg_visualizer.html` — real viewer for the SVG pieces.
- `mapping.html` — LED / pixel-mapping tool.

**Never edit these by hand.** The source is `web/src/`; any manual change is
erased by the next build.

## What does not belong here

Absolute paths, IPs, phone numbers or credentials. This repo is public; that
material lives in the assistant's local memory. Generated or personal files
(`DAILY.md`, `dashboard.html`, `*.local.md`) are gitignored and regenerate on
their own.

## Language

English, like the rest of the repo — this is an operational document, not a
product. Anything a human reads as a product (RD pieces and data, iskvw
curation) goes in correct Spanish with diacritics.

See also: `../AGENTS.md` (current operating contract), `../CLAUDE.md`
(compatibility and historical rules), and `../MAPA.md` (what the repo is and
every command).
