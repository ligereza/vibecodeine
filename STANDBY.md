# MAK standby checkpoint

Updated: 2026-08-14 03:40 UTC
Authority: physical Linux MAK under /home/mak
Checkout: /tmp/mak-clean-worktree (isolated validation worktree)
Base: origin/main at 486179789f67f2f6e5767d1b7bc7dd6575cd6aee
Proposal branch: codex/mak-web-restructure-20260814
Local transport commit: 9e92d4d0a1f1f711802e90443aeba415006b71a2

## Resume contract

Read this file and the current top of context/LAST_HANDOFF.md. Reverify every
live fact before changing files. The physical MAK runtime is authoritative.
/home/mak/WIN is archive/provenance only and must never execute or become a
runtime dependency.

Do not use reset, clean, pull, merge, branch deletion, automatic sync, browser
tooling, or destructive file operations. A read-only fetch of origin/main was
used only to measure the current Git base. Do not merge the stale PR #531.

## Stale transport found and isolated

The first proposal, PR #531, was based on old main 559fa6075e1cfb7a51be380c6d354d2af90dffb2.
Current origin/main is 486179789f67f2f6e5767d1b7bc7dd6575cd6aee. GitHub measured
the old proposal as diverged: 18 commits behind, 6 ahead, mergeable false,
dirty, with no checks. Its net comparison would delete historical recovered
material. Leave it open as evidence only; never merge it.

## Clean proposal state

This worktree starts from current origin/main and transports only the selected
positive or modified MAK scope. Historical/data deletions from the stale
proposal were excluded. The selected scope includes Linux runtime mirrors,
service contracts, read-only/manual workflows, dependency metadata, approved
curatoria candidates, Git boundary tests, coherence tests, privacy/test
repairs, and this checkpoint.

Runtime hash audit against /home/mak:

- mak_codex: 18 Python files, 0 different, 0 missing.
- mak_plataforma: 48 Python files, 0 different, 0 missing.
- mak_research: 28 Python files, 0 different, 0 missing.
- mak_xio_puente: 3 Python files, 0 different, 0 missing.
- mak_curatoria: 7 Python files, 0 different, 0 missing.
- Four systemd unit mirrors match by SHA-256: mak-codex, mak-hub,
  mak-research, and canonical mak-xio.

## Validation measured on this clean proposal

- Focused contract tests passed before the full run.
- Full pytest completed at 100 percent with exit code 0, zero failures, and
  zero skips. Existing Pillow and invalid-escape deprecation warnings only.
- Both active venvs report No broken requirements found.
- compileall passed for active MAK packages and tests.
- The bug hunt fixed stale provider-chain expectations, isolated env loading,
  empty-git handling, ESM package metadata, episode/work idle fixtures, and
  historical handoff privacy scanning. No historical evidence was deleted.

## Next action

1. Reverify the clean tree, remote base, and physical runtime hashes.
2. Push this new branch and create a new draft PR against current main.
3. Keep PR #531 stale and unmerged. Do not merge any canonical branch.

If a fact cannot be resolved locally, record the exact escalation block in
LAST_HANDOFF and the response:

STATUS: BLOCKED or DECISION_REQUIRED
AREA:
OBSERVED:
EVIDENCE:
CONFLICT:
OPTIONS:
RECOMMENDATION:
EXACT DECISION NEEDED:
COMMANDS NOT RUN:
FILES NOT MODIFIED:
