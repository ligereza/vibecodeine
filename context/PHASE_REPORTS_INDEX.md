# Phase reports index

Status: archival evidence only. This file is a navigation boundary, not an
execution plan. The only active continuity authority is
`/home/mak/flujo/context/LAST_HANDOFF.md`; the global contract is
`/home/mak/flujo/agents.md`.

## Inventory measured 2026-08-28

The physical scan of `/home/mak/flujo/context/PHASE*` found **13 phase reports**
plus this index:

| Range | Files | Classification |
|---|---:|---|
| `PHASE459`-`PHASE460` | 2 | git branch restructure and ten-branch review |
| `PHASE462`-`PHASE464` | 3 | portfolio catalog, panel and public artifact gates |
| `PHASE470`-`PHASE481` | 5 | RD entity adapter, physical git architecture, RD database authority, remote candidate audit, knowledge reconciliation, inferential archaeology |
| `PHASE485`-`PHASE486` | 2 | branch copy manifest and branch topology slice |
| **Total** | **13** | **13 Markdown, 0 CSV, 0 JSON; numbered 459 to 486** |

All 13 are tracked in Git.

### What the previous measurement said, and why it is retained here

The 2026-08-16 version of this section reported **748 files** (476 Markdown,
271 CSV, 1 JSON, 486 numbered phases) and instructed: *"Keep all 748 phase
files as untracked historical evidence for now."*

Both halves of that instruction are false against the tree as it stands on
2026-08-28: there are 13 phase reports, not 748, and they are tracked, not
untracked. Whatever removed the other 735 files did not update this index, so
for twelve days the index gave a retention order about a corpus that was no
longer there. That is the failure this section now records: **a measurement
written as prose outlives the thing it measured.** The count above is dated
for the same reason -- it will rot too.

Two phase reports are still cited by name in `docs/MAK_CURRENT_STATE.md` and no
longer exist: `PHASE209_FINAL_MAK_ARCHITECTURE_DISPOSITION.md` and
`PHASE413_CROSS_DOMAIN_SERVICE_ARCHITECTURE.md`. Those citations are dangling.

Some archived reports retain the absolute paths that existed when their
historical checks ran. Those paths are evidence of that past run only; they
are not valid current commands or source locations. Current commands must use
`/home/mak/flujo` and its `.venv`.

## Operational rule

Phase reports must not be used as current instructions merely because they
contain words such as `Next concrete action`, `current`, `gate`, `final` or
`proposal`. Those phrases describe the historical phase that produced the
file. When a phase report conflicts with the current handoff, the current
handoff and a fresh foreground check win.

The active source of truth is deliberately small, and it is the read order that
`tools/agent_bootstrap.py` actually enforces -- not a fourth list:

1. `agents.md` -- global authority, safety and language contract.
2. `docs/MAK_CURRENT_STATE.md` -- compact current architecture.
3. `context/LAST_HANDOFF.md` -- current objective, verified state, open items
   and next action.
4. Runtime source, contracts and focused tests -- implementation authority.

Until 2026-08-28 this list omitted `docs/MAK_CURRENT_STATE.md`, which is second
in the order the bootstrap emits. An index that names the sources of truth and
then disagrees with the loader is one more source of truth. See
`docs/AUTORIDAD.md` for the full list of documents that declare themselves
canonical and what each one is actually good for.

The former monolithic migration record was retired from the active workspace;
it must not replace `LAST_HANDOFF.md` or be loaded wholesale for routine work.

`context/MD_CONTEXT_MASTER.md` is a navigation index. It links families and
provenance, but it does not promote historical phase conclusions to runtime
truth.

## Retention decision

Keep the 13 remaining phase reports where they are. They are tracked, they are
bounded, and reading all of them costs less than the archaeology of finding out
what one of them said. Do not read the corpus when the current handoff or a
bounded evidence file answers the question.

The previous decision -- *"Keep all 748 phase files as untracked historical
evidence"* -- is retired. It described a corpus that no longer exists, and it
described it as untracked when the survivors are tracked.

## Reproducible check

From `/home/mak/flujo`:

```text
find context -maxdepth 1 -type f -name 'PHASE*' ! -name 'PHASE_REPORTS_INDEX.md'
```

The count and extension totals above are a measured snapshot, not a promise
that future phase files will be added here automatically. Any new phase file
must be treated as archival evidence until it is explicitly summarized in
`LAST_HANDOFF.md`.
