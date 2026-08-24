# Phase reports index

Status: archival evidence only. This file is a navigation boundary, not an
execution plan. The only active continuity authority is
`/home/mak/flujo/context/LAST_HANDOFF.md`; the global contract is
`/home/mak/flujo/agents.md`.

## Inventory measured 2026-08-16

The physical scan of `/home/mak/flujo/context/PHASE*` found:

| Range | Files | Classification |
|---|---:|---|
| `PHASE1`-`PHASE99` | 201 | initial inventory, migration and early runtime gates |
| `PHASE100`-`PHASE199` | 200 | ownership, department and projection consolidation |
| `PHASE200`-`PHASE299` | 150 | consumer, dependency and runtime validation gates |
| `PHASE300`-`PHASE399` | 117 | cleanup, safety, fixtures and objective reconciliation |
| `PHASE400`-`PHASE486` | 80 | portfolio, visual, venue and final architecture evidence |
| **Total** | **748** | **476 Markdown, 271 CSV, 1 JSON; 486 numbered phases** |

There are 271 same-stem Markdown/CSV pairs. The CSV is the tabular evidence
for its Markdown report; neither file is an executable instruction. The JSON
phase artifact is also evidence. The files remain in place to preserve
provenance and rollback context.

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

The active source of truth is deliberately small:

1. `agents.md` — global authority, safety and language contract.
2. `context/LAST_HANDOFF.md` — current objective, verified state, open items
   and next action.
3. Runtime source, contracts and focused tests — implementation authority.

The former monolithic migration record was retired from the active workspace;
it must not replace `LAST_HANDOFF.md` or be loaded wholesale for routine work.

`context/MD_CONTEXT_MASTER.md` is a navigation index. It links families and
provenance, but it does not promote historical phase conclusions to runtime
truth.

## Retention decision

Keep all 748 phase files as untracked historical evidence for now. Do not
stage them with implementation changes, do not delete them as duplicates and
do not read the whole corpus when a current handoff or a bounded evidence
file answers the question. A future retention pass may archive them outside
the active context path only after a separate manifest and reference audit.

## Reproducible check

From `/home/mak/flujo`:

```text
find context -maxdepth 1 -type f -name 'PHASE*' ! -name 'PHASE_REPORTS_INDEX.md'
```

The count and extension totals above are a measured snapshot, not a promise
that future phase files will be added here automatically. Any new phase file
must be treated as archival evidence until it is explicitly summarized in
`LAST_HANDOFF.md`.
