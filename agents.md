# MAK AGENT CONTRACT

This is the operational contract for the MAK Linux box. Linux paths are
case-sensitive. This lowercase file is canonical:
`/home/mak/flujo/agents.md`.

## Authority and physical migration

The physical Windows and MAK files are authoritative. Git is transport and
reproducibility only. Do not use Git as the inventory authority for what exists,
what is current or what must be integrated. A bounded consolidation task may
inspect local Git history read-only to establish provenance, prior contracts
and whether two sources evolved together; current filesystem and runtime
evidence still wins. Do not reset, clean, checkout, pull, merge, commit or push
unless the user explicitly asks for that operation in the current task.

For host-wide duplicate resolution, use the measured routing registry at
`/home/mak/indexes/mak-consolidation-20260829/MAK-DIRECTIVE-REGISTRY.md`.
It is a scope map, not a second handoff or a replacement for this contract.

The migration model is:

- Windows source material originated under `C:/IA/flujo`, including Codex
  memories, recovered Claude sessions, visual tools, source data and archives.
- That material was transferred to `/home/mak/WIN` as an historical Windows
  archive. `/home/mak/WIN` is evidence and source material, not the active
  runtime.
- MAK is the Linux operational box. Its active surface is `/home/mak/*`, not
  only `/home/mak/flujo`.
- `/home/mak/flujo` is the authoring and integration baseline.
- Runtime and department roots may exist outside it, including
  `/home/mak/plataforma`, `/home/mak/research`, `/home/mak/codex`,
  `/home/mak/curatoria`, `/home/mak/post`, `/home/mak/RD`,
  `/home/mak/xio_puente`, `/home/mak/src`, `/home/mak/apps`, `/home/mak/labs`,
  `/home/mak/n8n-local`, `/home/mak/workspace` and creative tool roots.
- The presence of a file in WIN does not prove that it is integrated into MAK.
  The absence of a file in `/home/mak/flujo` does not prove that it is absent
  from MAK. Compare physical surfaces and record provenance.

Never solve a migration discrepancy by copying a whole tree. Preserve the
source, classify the artifact and integrate the smallest complete component.

## Language

Speak Spanish to the user. Write machine-facing code, identifiers, filenames,
configuration keys, tests, technical logs and operational metadata in English
ASCII. Human-facing RD and Portfolio material may use correct Spanish,
accents and diacritics.

## User analogy convention

When a user message starts with `XANAX:`, treat the remainder as an analogy,
not as a literal request to install, test or research the named app or tool.
Infer the capability being compared, answer at the conceptual level, and act
on the named app only if the user separately makes that literal request.

## Permission and responsibility

The user authorizes editing of the MAK operational files, source components,
documentation, tests and integration targets required by the active task. This
permission is real and does not require repeated confirmation.

The permission does not allow:

- deleting historical evidence, databases, memories, journals, ledgers,
  credentials or generated products;
- overwriting a runtime source with a projection without a recorded reason;
- creating cron jobs, watchdogs or permanent background workers;
- hiding uncertainty by changing a status file;
- claiming integration because a file was copied or a JSON was edited;
- using lack of a prewritten handoff as an excuse to stop.

When an allowed target is clear, edit it and validate it. Do not manufacture a
permission blocker. If a destructive or externally consequential action is
actually required, state the exact target and stop only at that boundary.

## Integration objective

The objective is complete, working integration of the MAK ecosystem: tools,
libraries, departments, data contracts, services, visual utilities, research
pipelines and operational entrypoints. Integration means that each item has a
known physical source, destination, owner, consumers, dependencies, status and
verification result. A catalog or report is not integration.

Do not build duplicate frameworks or utilities before searching the existing
MAK and WIN surfaces. Reuse existing implementations and preserve historical
variants as classified evidence.

## Execution tactic

Read this file, run the mandatory bootstrap command below, then read
`docs/MAK_CURRENT_STATE.md` and only the emitted `Agent bootstrap — CURRENT`
packet before acting. Do not scan the append-only handoff to discover current
state. Then use this loop:

1. Establish the physical scope from `/home/mak` and `/home/mak/WIN`; do not use
   Git as an inventory shortcut.
2. Inventory existing tools, libraries, departments, databases, scripts,
   services, environments and generated outputs. Record exact paths and
   provenance.
3. Select one bounded vertical integration slice with a real consumer. A slice
   must include source, target, dependencies, interface and expected output.
4. Compare the source and target. Preserve runtime data and historical
   evidence. Apply the smallest necessary edit to the authorized target.
5. Validate the slice in the foreground: parse/compile, import, focused test,
   entrypoint contract or a bounded dry run as appropriate. Do not substitute
   a status edit for validation.
6. Reconcile the next unresolved dependency or tool. Continue automatically;
   do not wait for the user to send `continue`.
7. Update the handoff with evidence and immediately execute the next concrete
   action if work remains.

## Delegated-agent bootstrap (mandatory)

The subagent dispatcher does not reliably inject repository files into a new
worker context. A coordinator must therefore make the current state explicit;
the worker must not be expected to discover it by reading an append-only
handoff.

Before the first edit, every delegated worker must receive or execute:

```text
./.venv/bin/python tools/agent_bootstrap.py \
  --task "<bounded task>" \
  --write-set "<exact path or directory>"
```

The worker must read `agents.md`, `docs/MAK_CURRENT_STATE.md` and the
`## Agent bootstrap — CURRENT` packet in `context/LAST_HANDOFF.md` in that
order. Its first progress report must include `schema=mak-agent-bootstrap-v1`,
the three context hashes, its exact write-set and the first validation command.
If the worker starts without that acknowledgement, the coordinator must treat
its result as unbootstrapped and review it before accepting any claim. The
coordinator must include the packet output in the dispatch prompt when the
worker uses a fork/context mode that cannot access the shared filesystem.

The packet is a compact operational projection; the remainder of
`context/LAST_HANDOFF.md` is historical evidence and is never selected by
position, recency of a heading, or a chat summary.

## Fast path for simple bounded tasks

Not every request is an integration slice. If the user asks for a simple
read-only answer, names no implementation target and gives a bounded output
shape (for example, “five lines”), use this fast path:

1. Run the bootstrap, read `agents.md`, `docs/MAK_CURRENT_STATE.md` and the
   emitted CURRENT packet.
2. Read only the files directly named by the request or required to answer
   that one fact. The current packet is sufficient for facts it explicitly
   declares.
3. Do not scan the repository, recalculate unrelated hashes, inspect
   databases, query services, audit consumers or open historical handoff
   sections unless the request explicitly asks for that evidence.
4. If an unrelated discrepancy appears, mention it in one short sentence and
   stop; it is not permission to widen the task or repair anything.
5. Match the requested output bound exactly and stop after the direct answer.

This fast path does not weaken validation for edits or integration work. It
prevents a small question from becoming an unsolicited audit and keeps the
agent's effort proportional to the user's requested result.

## Reflection gate

Pause after at most 10 tool/command actions or 10 inspected files, whichever
comes first. Pause immediately after the first failed validation, conflicting
evidence, a proposed schema/database change, or an action that could broaden
scope. Use a short gate before continuing:

1. What is the real user outcome?
2. What was observed versus inferred?
3. What is the smallest reversible next action?
4. Can the dependency be removed or the route changed instead?
5. What result would make this path a dead end?

This gate is a decision budget, not a requirement to write another report. If
the answer is only more reading without a new validation signal, change the
route or stop the slice.

A phase label is only navigation. Never repeat an old phase because a chat
summary mentions it. Derive the current work from the open items in the
handoff and the physical state. If one item is deferred, keep it explicitly
open with its reason and move to the next executable item; do not let a list
of deferred items masquerade as complete integration.

## Verification standard

Every completed item must include:

- exact source and target paths;
- the action actually performed;
- the command executed in the foreground;
- exit code and observed result;
- changed files or verified no-change result;
- dependency and consumer impact;
- unresolved risk and concrete next action.

A response containing only a report, a plan, a Mermaid diagram, a status-file
edit or a claim of completion is not evidence of work. A tool is not
integrated until its import/entrypoint/contract and relevant output are
verified, or it is explicitly classified as unavailable with the exact reason.
Do not start permanent services during integration. If a bounded runtime check
is necessary, run it temporarily, capture evidence, then clean it up.

## Single useful handoff

Maintain only this operational handoff:
`/home/mak/flujo/context/LAST_HANDOFF.md`.

Keep it concise and current. It must contain these sections:

- `Current objective`
- `Physical authority and migration status`
- `Completed work with command and result`
- `Open integration items` with exact paths and status
- `Tool and dependency verification matrix`
- `Conflicts and risks`
- `Next concrete action`
- `Last verified`

The handoff is evidence and continuity state, not a list of abstract rules.
Never write `next phase: rest`, `waiting`, or `nothing pending` while an open
integration item, failed verification, unresolved conflict or untested tool
exists. After reporting progress, continue with `Next concrete action` in the
same task. If the context is compacted, read this handoff and resume from its
open item instead of restarting or improvising.

## Short-lived branch contract

The root `agents.md` is global and applies to every branch. A short-lived topic
branch must additionally carry a scoped `agents.md` copied from
`contracts/BRANCH_AGENTS_TEMPLATE.md` under
`contracts/branches/<branch-id>/agents.md`. It must name the branch, owner,
consumer, allowed write set, dependency group, validation commands and rollback.

The same branch must carry a private continuity file copied from
`context/BRANCH_HANDOFF_TEMPLATE.md` under
`context/handoffs/<branch-id>.md`. This file is not a second global handoff:
it is the branch's bounded execution record. Before the branch is merged, its
durable facts must be promoted to `context/LAST_HANDOFF.md`; after promotion,
the topic branch and its temporary contract/handoff are deleted together.

The root README and its current SVG artwork are protected assets. A topic
branch may not rewrite, reformat or replace them as collateral work.

If a real blocker exists, record the exact path, command, exit code, error and
smallest recovery action. A generic statement such as "not authorized",
"needs review" or "phase incomplete" is not a blocker without that evidence.

## Finish condition

The work is finished only when the handoff shows no unverified integration item
within the authorized scope, every claimed tool has a verification result,
all conflicts have a disposition, no unsafe process remains running, and the
next action is genuinely empty because the defined objective is complete. Until
then, report briefly and keep working.
