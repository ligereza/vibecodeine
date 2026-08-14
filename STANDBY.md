# MAK standby checkpoint

Updated: 2026-08-13
Authority: physical Linux MAK under /home/mak
Checkout: /home/mak/flujo
Branch: codex/mak-web-restructure-20260813 (proposal)
HEAD: 559fa6075e1cfb7a51be380c6d354d2af90dffb2

## Resume contract

Read this file first, then read the current top section of
`context/LAST_HANDOFF.md`. Verify every live fact before changing files.
MAK runtime and its Linux checkout are authoritative. `/home/mak/WIN` is
archive and provenance only. Never execute code from WIN and never make WIN a
runtime dependency.

The user confirmed that MAK no longer depends on a live Windows machine. Do
not restore Windows providers, remote Windows endpoints, Windows commands,
Windows-only libraries, or a parallel framework. Existing Linux Ollama/NIM/
Watson paths are the only active model routes.

Do not use `git reset`, `git clean`, `git pull`, `git merge`, branch deletion,
automatic synchronization, browser tooling, or destructive file operations.
Do not commit or publish without explicit authorization. Git is transport after
the physical MAK audit; MAK is the only publisher.

## Work already completed

- Inventory and deterministic classification covered `/home/mak/flujo`,
  `/home/mak/research`, `/home/mak/plataforma`, `/home/mak/codex`,
  `/home/mak/xio_puente`, and `/home/mak/WIN/codex`; zero files were left
  unclassified. Duplicate groups were recorded without moving or overwriting
  files.
- Active runtime code was reconciled into the `cultura/mak_*` mirrors one
  file at a time. Main service entrypoints now match by SHA-256:
  - Codex interfaz: `b5c551fa228be777253a1ea7bd2e8918ff35799d81cff7802168e43e0b57cc25`
  - Research interfaz: `c7cf09854729ee4e83e50a62d5557dd5815d0e805d50ed1d14a471bf33458114`
  - Hub: `9a8b861d6065606fcef3c9c4ba13350cfe94f6e8c806ad07df7cfccdb96b0255`
  - XIO monitor: `633695ea015384ea5c8066fc42d9398e50522e157113361a5bd5e2d384bb24d0`
- Active source has no live WIN provider route, WIN model, or remote WIN
  endpoint in the audited runtime/code scope. Historical rollback, tests,
  and archive evidence are not runtime dependencies.
- `mak_conductor` was restored into the checkout from archived source only
  after compiled-code signatures matched the local pyc evidence. Its source
  is not wired into cron or an active service yet.
- Hub `/health` now returns JSON under `mak-hub-health-v1`; the route regression
  test passes. The coherence checker matches absolute paths, excludes venv
  packages, and exits zero with no invoked box-only files.
- Live and checkout `percepcion.py` match at
  `f3589397262e37651b81f688beaf5a5e4e72b066152679513a335365b4857081`.
  Live and checkout `coherence.py` match at
  `f62abba0e20d5de72f1e672460cb066305ba859a590f587a142184a76ef05269`.
- `tools/mak_ops/run_conductor_worker.py`,
  `cultura/mak_plataforma/actividad.py`,
  `cultura/mak_plataforma/gpu_guard.py`, and
  `cultura/mak_codex/motor_semantico/calidad_svg.py` were added only after
  local pyc/live-source or exact archived-source evidence.
- `diagnostico_proyectos.py` was reviewed as byte-identical to `mak`;
  `ingesta_archivo.py` was reviewed as a deterministic ASCII identifier/API
  delta and both are now staged with the conductor.
- The staged proposal contains 97 files. The existing Research venv has
  `duckdb 1.5.5`, declared by `pyproject.toml` and `requirements-dev.txt`.
- The effective repo-sync cron line remains paused as `# PAUSED-FARO`; no
  fetch, checkout, reset, pull, merge, clean, or automatic synchronization
  was run.
- Credential-bearing env files remain external state and are mode 600:
  `/home/mak/flujo/.env`, `/home/mak/research/research.env`, and
  `/home/mak/xio_puente/.env`. Values were not printed or promoted.

## Current live state measured 2026-08-13 22:24

- `mak-hub.service`: PID 111669, `0.0.0.0:8900`.
- `mak-research.service`: PID 72229, `127.0.0.1:8890`.
- `mak-codex.service`: PID 96805, `127.0.0.1:8891`.
- `mak-xio.service`: one GET-only monitor process; no duplicate listener.
- The measured endpoint matrix is healthy for Hub `/health`, `/portafolio/`,
  portfolio audit/status/review APIs, Research, and Codex. `/api/graph` is
  intentionally 404 because it is not a declared route.
- Hub `MAK_PORTFOLIO_ROOT` is unset, so `/portafolio/` serves
  `/home/mak/flujo/iskvw`. Current served asset hashes were recorded in the
  current handoff.
- Research and platform venvs passed `pip check`. Pytest was installed only
  in the existing research venv from already-declared test dependencies; no
  provider or framework was added.

## Test and bug-hunt pause point

Focused regression and bug-hunt command used:

```text
PATH=/home/mak/research/.venv/bin:$PATH PYTHONPATH=/home/mak/flujo/src:/home/mak/flujo/cultura:/home/mak/flujo/cultura/mak_codex:/home/mak/flujo/cultura/mak_research:/home/mak/flujo/cultura/mak_plataforma /home/mak/research/.venv/bin/python -m pytest -q -rs --tb=short tests/test_mak_portfolio_bridge.py tests/test_coherence_boundaries.py tests/test_mak_mirror_fixes.py tests/test_higiene_docs.py
```

Result:

- All selected executable tests pass; exactly one skip remains at
  `tests/test_higiene_docs.py:134` because `DIRECTOR_CONTRACT.md` is absent.
  The director explicitly waived that documentation test. Compileall, Node
  syntax, `git diff --check`, both venv `pip check` commands, and
  `coherence.py --strict` also pass.
- A redundant full-suite attempt after rereading the handoff was interrupted
  at 21% with no file or runtime-data change. Do not treat that interruption as
  a regression result; the earlier recorded full-suite green result remains
  the historical evidence.
- A detached validation tree from `mak` with all 97 staged blobs overlaid ran
  2,855 tests with zero failures and one authorized documentation skip at
  `tests/test_higiene_docs.py:134`. The tree was local-only and no canonical
  ref or remote changed.

## Required next actions

1. Review the local proposal branch scope against the physical MAK audit.
2. Keep generated data, credentials, and WIN material out of the staged scope.
3. Recheck staged diff for secrets, generated files, branch-boundary changes,
   and accidental history rewriting.
4. Do not commit or publish until the director explicitly authorizes that
   transport step. Keep repo-sync paused and WIN archival.

## Do not declare success while any of these remain

- Missing dependency or unavailable required validation backend.
- Unexplained runtime/source hash difference or unclassified file.
- Service executing a different source than the verified checkout.
- Test failure, omitted test, dead process, duplicate watchdog/cron writer,
  embedded credential, or unexplained duplicate.

If a local fact cannot be resolved, put this exact escalation block in
LAST_HANDOFF and in the final response:

```text
STATUS: BLOCKED or DECISION_REQUIRED
AREA:
OBSERVED:
EVIDENCE:
CONFLICT:
OPTIONS:
RECOMMENDATION:
EXACT DECISION NEEDED:
COMMANDS_NOT_RUN:
FILES_NOT_MODIFIED:
```
