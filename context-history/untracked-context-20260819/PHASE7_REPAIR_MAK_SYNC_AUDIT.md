# Phase 7 Repair MAK Sync Audit

## Objective

Determine whether `repair_mak_sync.py` has an explicit owner, operational consumer, dependency set, and authorized contract. Document static potential effects and the divergence between the active MAK file and the historical WIN file without executing repair behavior.

## Scope

- Active: `/home/mak/flujo/tools/mak_ops/repair_mak_sync.py`
- Historical WIN: `/home/mak/WIN/flujo/tools/mak_ops/repair_mak_sync.py`
- Read first: `agents.md`, `context/LAST_HANDOFF.md`, `context/PHASE6_LOCAL_MAK_OPS_COMPARE.md`, and its CSV.
- Allowed work: bounded text inspection, `diff`, `sha256sum`, `grep`, and AST parsing with `PYTHONDONTWRITEBYTECODE=1`.
- Excluded: script execution, `--repair`, `--apply`, SSH, Git commands, service/cron changes, output-file writes, secrets, `.env`, and private data.

## Active contract

The active file has a docstring and argparse contract, but no authorized owner or runtime consumer was found. Its advertised invocation is `--apply --output <path>`; `--apply` is required before the remote action, and the default report path is `mak_sync_repair.md`. The main guard is present at lines 122-123 and calls `main()` through `SystemExit`.

Static behavior if `--apply` were authorized and executed: it would invoke `ssh` to `MAK_USER@MAK_HOST` (defaults `mak@192.168.50.2`) with a shell script. The remote script checks `/home/mak/flujo`, creates a backup branch, reads and replaces the `MAK-REPO-SYNC` crontab line, performs `git fetch`, `git checkout -B`, and `git reset --hard`, then runs four `cp -ru` mirror copies to `/home/mak/plataforma`, `/home/mak/research`, `/home/mak/codex`, and `/home/mak/curatoria`. It finally reads branch/status/crontab and probes three localhost HTTP endpoints with `curl`. The local process writes the requested report after SSH returns.

The source text claims not to touch secrets, RD data, services, network, XIO, models, or GitHub, but the actual embedded shell does alter Git state and crontab and performs network-mediated SSH and localhost probes. These claims are not an authorization contract.

## WIN divergence

Active SHA-256: `1eb2a1d794f95322984983811602a60d5be9853594ac4c743aa2367c43c45615`.

WIN SHA-256: `6502982d9bae0c634d0a7b23680fb6320e2bbeb796d847dd8fb2074bb69341b8`.

The divergence is material. The active variant directly changes the live checkout, replaces cron, resets `origin/main`, copies four live mirrors, and probes APIs. The WIN variant avoids resetting the human checkout, creates or reuses a disposable `$HOME/flujo-deploy` worktree, backs up crontab, and provisions `/home/mak/bin/mak_sync_safe.py` through `scp` and `ssh`; it does not itself fetch, checkout, reset, copy the four mirrors, or activate cron. WIN therefore adds `scp`, `install`, `/tmp/mak_sync_safe.py`, and the WIN-only dependency `sync_mak_safe.py` (present at `/home/mak/WIN/flujo/tools/mak_ops/sync_mak_safe.py`, absent at the active path).

Both variants have `argparse`, `--apply`, `--output`, a `main` function, and a `__main__` guard. Neither was run, and help was not invoked because the task required avoiding entrypoint execution unless safety was guaranteed.

## Effects/risk

- `git fetch`: changes remote-ref state in the active remote checkout.
- `git checkout -B`: moves or creates `main` in the active checkout; WIN uses a detached disposable worktree instead.
- `git reset --hard`: active variant can discard tracked and index/worktree state after its clean-status gate; this is externally consequential.
- `cp -ru`: active variant can mutate four live department roots and overwrite older destination files according to `cp` semantics.
- `ssh`/`scp`: both variants can transmit commands or a script to the configured host; host defaults are embedded and environment-overridable.
- `systemd`: no systemd command or unit reference was found in either file; no service was started or changed.
- `cron`: active variant rewrites the `MAK-REPO-SYNC` crontab entry; both variants read and back up crontab. WIN does not activate cron itself.
- Output files: both variants write a Markdown report at `--output` (default `mak_sync_repair.md`) only after their apply path; no output was written during this audit.
- Local APIs: active variant probes `127.0.0.1:8890`, `8891`, and `8900/api/salud` from the remote shell.
- Main guard: direct execution routes into argparse and, with `--apply`, into side effects; import alone does not call `main()`.

## Owner/consumer/dependency

- Owner candidate: none identified. No explicit team, person, service owner, or deployment authority appears in either file or the bounded active-tree references.
- Consumer candidate: `/home/mak/flujo/tests/test_operational_entrypoints.py` contains a text reference only; it is not evidence of an operational consumer. No active service, timer, cron declaration, launcher, or import consumer was found in the bounded search.
- Dependency candidate, active: Python standard library (`argparse`, `datetime`, `os`, `subprocess`, `pathlib`), local `ssh`, remote `bash`, Git, `crontab`, `cp`, `mktemp`, `grep`, `rm`, and `curl`, plus the remote paths listed above.
- Dependency candidate, WIN: the same Python standard-library class, local `scp` and `ssh`, remote `bash`, Git worktree/status, `crontab`, `mkdir`, `install`, and `rm`, plus `sync_mak_safe.py` and `/home/mak/bin/mak_sync_safe.py`.
- Authorized contract: not established. The `--apply` flag is an implementation gate, not proof of authorization.

## No-change decision

Decision: `no_change`. Do not promote either variant, copy WIN files, execute an entrypoint, alter cron/systemd, modify Git state, use SSH, or create/modify output files. The default no-change rule applies because no explicit owner, operational consumer, dependency contract, or authorization was identified, and the variants have materially different destructive/provisioning effects.

## Verification log

- Read four required context files: exit `0`; context and Phase 6 evidence loaded.
- `stat` on both target files: exit `0`; active size 5424/mode 644, WIN size 4131/mode 600.
- `sha256sum` on both target files: exit `0`; hashes recorded above.
- `nl -ba` on both target files: exit `0`; full bounded source text inspected.
- `diff -u active WIN`: exit `1`; expected material difference, inspected without edits.
- `rg` operation scan: exit `127`; `rg` is unavailable. No fallback risk was introduced.
- Acotado `grep` reference scan: exit `0`; only the test text reference and phase evidence were found in the active tree; no active operational consumer found.
- AST parse with `PYTHONDONTWRITEBYTECODE=1`: exit `0` for both files; both parse successfully, expose their functions, and contain a `__main__` guard.
- AST string/call extraction: exit `0` for both files; identified argparse, subprocess, SSH/SCP, Git, cron, copy/provision, report-write, and endpoint strings as applicable.
- File existence check: exit `0` for both repair files; WIN `sync_mak_safe.py` exists; active `sync_mak_safe.py` is absent (test exits `0` and `1` respectively).
- No script, `--apply`, `--repair`, `--help`, SSH, Git, systemd, cron, or output action was executed.

## Next action

Request an explicit owner, named operational consumer, dependency contract, approved target host/paths, and a separately bounded dry-run or review procedure before any execution or promotion. Until then, retain both files as evidence and keep the decision `no_change`.

## Last checkpoint

2026-08-14 America/Santiago — LUNA-07 completed static audit; no source, WIN, service, cron, Git, SSH, or output changes made.
