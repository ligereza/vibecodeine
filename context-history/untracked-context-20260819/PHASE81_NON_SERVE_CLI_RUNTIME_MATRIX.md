# Phase 81 — non-serve CLI runtime matrix

## Scope

Validated the local read-only CLI surface using the physical MAK tree first.
The canonical runtime is `/home/mak/venvs/flujo/bin/python`; system Python was
checked only to distinguish an environment problem from a code problem.

## Results

| Consumer | Runtime | Result |
|---|---|---|
| `flujo version` | system Python + `PYTHONPATH=src` | exit 0, 0.56.1 |
| `flujo health` | system Python + `PYTHONPATH=src` | exit 0 |
| `flujo job list` | system Python + `PYTHONPATH=src` | exit 0, 8 jobs |
| `flujo datadrop list` | system Python + `PYTHONPATH=src` | exit 0 |
| `flujo rd-db packs` | system Python + `PYTHONPATH=src` | exit 0 |
| `flujo rd-db eventos` | system Python + `PYTHONPATH=src` | exit 0 |
| `flujo rd-db testeos` | system Python + `PYTHONPATH=src` | exit 0, publication remains disabled |
| `flujo rd-db venues` | system Python + `PYTHONPATH=src` | exit 0 |
| `flujo knowledge list productoras` | system Python | exit 1, PyYAML missing |
| `flujo knowledge list productoras` | canonical venv | exit 0, 3 entities |
| `flujo knowledge list venues` | canonical venv | exit 0, 3 entities |
| `flujo health` | canonical venv | exit 0 |
| `flujo autonomia status` | system Python + `PYTHONPATH=src` | exit 0, external providers not called |

## Dependency conclusion

`pyproject.toml` and `requirements.txt` declare `pyyaml>=6.0.3`; the canonical
venv contains PyYAML 6.0.3. The system interpreter is not the project runtime.
No fallback parser, package installation or source edit is justified.

The shell currently has no `flujo` executable on `PATH`; users must activate
the venv or invoke its Python explicitly. This is an environment/entrypoint
follow-up, not a knowledge-base code failure.

## Safety

Only read/list/diagnostic commands ran. No job, datadrop, database, provider,
ledger, file or output mutation occurred.

## Next

Audit the project launcher/activation path and document a reproducible MAK
entrypoint, then continue with remaining static consumers. Do not install
dependencies automatically.
