# Phase 4 Entrypoint Verification

## Objective

Verify whether the declared operational entrypoint `flujo = flujo.cli:app` resolves to the active source from the operational virtual environment, record minimum passing commands, and document why the system Python fails.

## Scope

In scope: `/home/mak/flujo/pyproject.toml`, `/home/mak/flujo/src/flujo`, `/home/mak/venvs/flujo/bin/python`, `/home/mak/venvs/flujo/bin/flujo`, and `/usr/bin/python3` as contrast. Foreground checks only. No package installation, code change, Git operation, service start, or WIN modification.

## Runtime map

- Contract: `/home/mak/flujo/pyproject.toml:53-54` declares `flujo = "flujo.cli:app"` and project version `0.56.1`.
- Active interpreter: `/home/mak/venvs/flujo/bin/python` -> `python3` -> `/usr/bin/python3.11`; `python3.11` in the venv resolves to `/usr/bin/python3.11`.
- Active launcher: `/home/mak/venvs/flujo/bin/flujo`, regular executable, shebang `#!/home/mak/venvs/flujo/bin/python3`.
- Active import: `flujo.__file__` and `inspect.getfile(flujo)` both resolve to `/home/mak/flujo/src/flujo/__init__.py`.
- Contrast interpreter: `/usr/bin/python3` -> `/usr/bin/python3.11`; it does not have the active source on its import path.

## Tests

1. `stat` and `readlink` confirmed the interpreter and launcher map above; exit 0.
2. `/home/mak/venvs/flujo/bin/python -c 'import flujo, inspect; ...'` imported `flujo`, reported version `0.56.1`, and reported `/home/mak/flujo/src/flujo/__init__.py`; exit 0.
3. `/home/mak/venvs/flujo/bin/flujo --help` displayed the Typer command list and version `0.56.1`; exit 0.
4. `/home/mak/venvs/flujo/bin/flujo version` displayed `flujo · versión 0.56.1` and the `v0.56.1` changelog; exit 0.
5. `/usr/bin/python3 -m flujo --help` failed with `No module named flujo`; exit 1.

## Result

PASS. The real venv entrypoint imports the active source tree and dispatches the declared `flujo.cli:app`. The minimum operational checks `--help` and `version` pass. The system Python is only a contrast runtime: it fails because `flujo` is not installed or otherwise present on that interpreter's import path. It must not be treated as the active runtime.

## No-change decision

No code, packaging, runtime, or WIN change is justified. The launcher, import path, and command behavior are reconciled already. Documentation and its evidence CSV are the only persisted outputs for this slice.

## Risks

- The venv uses the system Python binary through symlinks; a future system-Python replacement could affect the venv and should be checked before upgrades.
- Import resolution depends on the current venv installation/path configuration; do not infer that `/usr/bin/python3` can run `flujo` without an explicit supported installation or path setup.
- This slice verifies entrypoint reachability and two commands, not every subcommand or optional dependency.

## Verification log

| Runtime | Command | Exit code | Observed result |
|---|---|---:|---|
| venv | `stat`/`readlink` for Python binaries and launcher; read launcher shebang | 0 | Symlink chain and venv shebang match the active runtime map. |
| venv | `/home/mak/venvs/flujo/bin/python -c 'import flujo, inspect; ...'` | 0 | Module and inspection path: `/home/mak/flujo/src/flujo/__init__.py`; version `0.56.1`. |
| venv | `/home/mak/venvs/flujo/bin/flujo --help` | 0 | Help rendered; command list available. |
| venv | `/home/mak/venvs/flujo/bin/flujo version` | 0 | Version/changelog rendered; `v0.56.1`. |
| system contrast | `/usr/bin/python3 -m flujo --help` | 1 | `No module named flujo`. |

Machine-readable equivalents are in `context/PHASE4_ENTRYPOINT_VERIFICATION.csv`; the CSV was parsed with Python stdlib after writing.

## Next action

Keep `/home/mak/venvs/flujo/bin/flujo` as the documented operational command and use `/home/mak/venvs/flujo/bin/python` for direct probes; before the next integration slice, select one bounded non-artwork consumer and verify it with this same venv.

## Last checkpoint

2026-08-14 America/Santiago — LUNA-04 verified the declared entrypoint, active import path, help/version commands, and system-Python contrast; no active code or WIN change made.
