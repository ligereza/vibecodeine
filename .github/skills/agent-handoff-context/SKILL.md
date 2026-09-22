---
name: agent-handoff-context
description: "Use when a new agent must continue work without reconstructing the repository from old handoffs."
---

# Agent continuity without handoff drift

The repository no longer uses a global handoff as its source of current work.

## Required bootstrap

1. Read `AGENTS.md`.
2. Read `REAL_INFO.md`.
3. Identify the current task from the user message, issue, PR or active branch.
4. Inspect `git status`, the relevant diff and only the domain files needed for that task.
5. Use `HISTORICO.md` only when a past decision or file movement must be explained.

## Never do this

- Do not scan `context-history/**`, recovered sessions or PHASE reports to discover what to do next.
- Do not treat `LAST_HANDOFF`, `HANDOFF_HISTORICO`, `NEXT.md`, a session closeout or a document labelled CURRENT as a backlog.
- Do not create another permanent global handoff file.
- Do not inherit an old “next action” without confirming it against the current task and tree.

## Continuation packet

When another agent needs context, pass only:

- current user objective;
- branch / PR / relevant commit;
- exact files already changed;
- verification already run and its real result;
- one concrete unresolved blocker, if any.

Everything else should be discoverable from `AGENTS.md`, `REAL_INFO.md`, code and Git.

## Finish

If a durable global fact changed, update `REAL_INFO.md` briefly.
If only historical context is worth preserving, add a short dated note to `HISTORICO.md`.
Do not write a new state narrative.
