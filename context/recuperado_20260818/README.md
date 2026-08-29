# Recovered from the Trash -- 2026-08-28

These six files were produced on 2026-08-18 by a session that did exactly the
work "order MAK" names. They were found in
`/home/mak/.local/share/Trash/files/flujo/context/`, not deleted, and copied
back here with `cp -p`.

## What they are

| File | Content |
|---|---|
| `PHASE1_INVENTORY.csv` / `.md` | physical inventory of `/home/mak` and `/home/mak/WIN`, 144 rows, 12 columns |
| `PHASE2_FLUJO_RECONCILIATION.csv` / `.md` | 35 paths from three WIN manifests reconciled against `/home/mak/flujo`: 14 `content_changed`, 21 `metadata_only`, 35/35 present, 29 differing hashes, 6 matching |
| `PHASE3_CHANGED_ROUTES_REVIEW.csv` / `.md` | classification of the 14 changed routes; all resolved `no_change` |

## Why they matter

`PHASE1_INVENTORY.csv` carries the right schema for the question this repo keeps
asking: `path, type, size_bytes, mtime, mode, root, category, provenance,
status, owner_candidate, consumer_candidate, notes`.

**It is structurally complete and semantically empty.** Measured 2026-08-28:
`owner_candidate` is `unknown` in 135 of 144 rows, and `category` is `other` in
65. The frame was built and never filled. That is not a criticism of the session
that made it -- the frame is the hard part and it is correct.

`context/MAK_TRIAGE_20260828.md` fills it for the repo's 26 top-level paths,
crossing this inventory with the Git history mega-summary and the session's own
measurements.

## How they were found

Not by searching the repo. The trail was:

1. `/home/mak/.codex/memories/rollout_summaries/2026-08-18T07-35-37-ivVb-mak_inventory_reconciliation_luna_checkpoints.md`
   -- a Codex session summary naming these files by path.
2. The paths did not exist in `context/`.
3. `/home/mak/.local/share/Trash/files/flujo/context/` holds them. But read the
   `.trashinfo`: that `flujo` tree is `/home/mak/.codex/worktrees/31af/flujo`,
   a **Codex worktree** deleted 2026-08-24, not `/home/mak/flujo`. The
   2026-08-18 session ran with that worktree as its `cwd`, so these files were
   **written there and never reached the repo**. They went to the Trash with
   the worktree six days later.

The Trash holds 628 MB, 14065 files and 232 `.trashinfo` records. By original
location: 81 from `actions-runner/`, 59 from `plataforma/`, 29 from `research/`,
13 from `codex/`, 9 from `WIN/`. It is a surface, not an absence -- and every
file in it carries its origin and deletion date in a `.trashinfo` beside it.

## Rule this establishes

Before concluding that something does not exist, check: the Trash, the sibling
surfaces under `/home/mak`, and the Codex session summaries under
`/home/mak/.codex/memories/rollout_summaries/`. In this session every single
"it does not exist" that was checked against those three places turned out to
be "it exists and I looked in one place".
