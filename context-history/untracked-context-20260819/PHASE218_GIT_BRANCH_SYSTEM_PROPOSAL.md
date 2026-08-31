# Phase 218 — Git branch-system proposal for MAK

Date: 2026-08-15 (America/Santiago)
Status: `PROPOSAL_ONLY; NO_GIT_OPERATION`

## Principles

- `main` is the only stable integration line.
- Every short-lived branch owns one vertical consumer slice and one write set.
- Branch names are ASCII and use the `codex/` prefix for traceability.
- `WIN` is historical evidence stored in the filesystem; it is not a branch
  source and is never rebased or cleaned through this system.
- Cleanup branches carry manifests and reversible quarantine operations; they
  never silently delete evidence.
- A branch cannot merge without a current `LAST_HANDOFF.md` entry, exact
  validation commands/codes, dependency disposition and rollback path.

## Naming system

| Branch pattern | Owner/write set | Purpose |
|---|---|---|
| `main` | release integration | Stable MAK baseline; protected review only |
| `codex/mak/architecture` | `flujo/context/*ARCH*`, maps and ledgers | Folder ownership, crosswalks and visual status; no runtime mutation |
| `codex/mak/rd-catalog` | `src/flujo/rd`, `data/rd_packs.json`, catalog readers | Regenerable catalog/assets; never field rows |
| `codex/mak/rd-field` | `src/flujo/rd/datos.py`, privacy schemas/tests | Privacy-first field authority; only with real source/approval |
| `codex/mak/rd-routes` | RD web route handlers/tests | Mutating route contracts and rollback; no live uploads by default |
| `codex/mak/flujo-cli` | `src/flujo/cli.py`, CLI docs/tests | Non-serve commands and job lifecycle |
| `codex/mak/automation` | issue bridge, paused cron/unit manifests | FLUJO issue workflow and automation; external calls isolated |
| `codex/mak/deps` | `pyproject.toml`, `requirements.txt`, slice manifests | Dependency declarations only; no broad upgrades |
| `codex/mak/departments/<name>` | one canonical `cultura/mak_<name>` plus its projection tests | Research/Codex/Curatoria/Plataforma/Lenguaje consumer fusion |
| `codex/mak/cleanup/<phase>` | one path-specific quarantine manifest | Exact confirmed junk or one reversible candidate |
| `codex/mak/release/<version>` | release notes and validation snapshots | Assemble already-reviewed slices for a stable release |

`<name>` and `<phase>` are lowercase ASCII tokens, for example
`codex/mak/departments/research` and `codex/mak/cleanup/phase219`. Do not use
personal names, model names or ambiguous labels as branch identifiers.

## Merge order

```text
main
  <- architecture/ledger
  <- deps
  <- rd-catalog + flujo-cli
  <- departments/<name>
  <- rd-field       (only after field authority)
  <- rd-routes      (only after mutator authority)
  <- automation     (only after external-call gate)
  <- cleanup/<phase> (only after rollback + foreground validation)
  <- release/<version>
```

The order is a dependency order, not permission to create or merge branches.
Independent branches may be reviewed in parallel, but each must retain a
disjoint write set and the handoff must identify its predecessor (`LUNA-N` or
phase number) and successor.

## Required merge gate

Before any PR/merge:

1. State the exact consumer and source-of-truth paths.
2. Run static parse/import checks in the canonical MAK venv.
3. Run bounded foreground fixtures; never start a permanent service.
4. Record commands, exit codes, changed files, risks and rollback in
   `context/LAST_HANDOFF.md`.
5. Run dependency check for the relevant slice only.
6. For cleanup, include full hash, mode, original path, quarantine path and
   inverse command; preserve WIN, databases, media, credentials and evidence.
7. Review Spanish/English aliases and Windows/Linux platform paths before
   declaring a consumer absent.

## Current recommendation

Do not create branches yet. The proposal is ready, but objectives 1, 3, 7,
11 and 12 still have open/deferred gates. Create the first branch only after
the architecture snapshot is accepted and the next slice has a bounded write
set. The first practical branch should be `codex/mak/architecture` if a Git
change is authorized; otherwise keep this proposal as a filesystem artifact.

