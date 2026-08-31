# Phase 192 — Research role matrix

Status: `COMPLETE; NO_RUNTIME_ACTIVE`

| Family/path | Role | Consumer evidence | Current action |
|---|---|---|---|
| `mak_research/research.py` + `/home/mak/research/research.py` | Canonical runner + runtime projection | Manual/runtime entry; Research UI/worker references | Keep source plus wrapper |
| `mak_research/worker.py` + runtime wrapper | Job boundary | UI/queue references; GPU/provider boundary | Keep source plus wrapper; live inactive |
| `mak_research/interfaz.py` | Research UI source/runtime | `mak-research.service` declaration | Keep; user service `inactive` |
| Exact helper scripts | Historical/runtime helpers | Paused crontab/manual declarations | Preserve until individually redirected |
| `MAK_RESEARCH.md`, `USO.md`, `DIGEST.md`, reports | Human/operator docs | Runtime/manual reading | Preserve; source/runtime exact copies need later doc-owner decision |
| Mailboxes, logs, locks, checkpoints, corpus, reports | Durable evidence/state | On-disk outputs and history | Never classify by hash alone |
| `/home/mak/plataforma/interfaz.py` | Legacy competing UI | No launcher reference; same port 8890; import fails | Preserve as legacy candidate |

## Runtime status gate

Read-only user-unit checks returned `inactive` for `mak-research.service`,
`mak-codex.service`, `mak-hub.service` and `mak-interfaz.service`. The bounded
process search found no matching Research/Platform/Codex/Curatoria/Vigia
runtime process. This confirms that the audit and path fixes did not leave a
background service running.

## Decision

Research has a clear source/runtime owner and no safe deletion candidate in
this family. The next duplicate family can be selected from platform/Codex
projections, but only with the same role/consumer/rollback evidence.
