Identity: LUNA-21

# Phase 19 — flujo core contract review / revisión de contrato

## Contract / contrato

Scope is the smallest KEEP_CANDIDATE group: `/home/mak/flujo/pyproject.toml`,
`src/flujo/cli.py`, `src/flujo/__main__.py` and `src/flujo/autonomia.py`.
Owner candidate / candidato de owner: `flujo maintainer`. Real consumer / consumidor real:
`/home/mak/venvs/flujo/bin/flujo` and the `flujo autonomia` commands. The declared
entrypoint is `flujo = flujo.cli:app`; `__main__.py` delegates to the same app.

The contract is adoptable as a bounded candidate, not as a live autonomy execution:
the launcher is real, help/version work, AST and imports pass, and the package metadata
matches the source tree. `tests/test_cli_smoke.py` is outside this review and remains
DEFER because pytest is unavailable (`command -v pytest` exit 1; `python3 -m pytest`
exit 1, `No module named pytest`).

## Dependencies / dependencias

Declared runtime dependencies are matplotlib, PyYAML, pydantic, typer, rich, jsonschema,
requests and boto3. In the launcher interpreter (`/home/mak/venvs/flujo/bin/python3`)
all eight are available: matplotlib 3.11.1, PyYAML 6.0.3, pydantic 2.13.4, typer
0.27.1, rich 15.0.0, jsonschema 4.26.0, requests 2.34.2 and boto3 1.43.66.
The declared build dependency `wheel` is missing in that interpreter; this does not
block the already-installed launcher but leaves packaging/rebuild risk. System Python
dependency availability is not the consumer contract; prior contrast remains
`/usr/bin/python3 -m flujo --help` exit 1 (`No module named flujo`).

`autonomia.py` imports `cultura.mak_plataforma.ledger`, `providers` and `tandas`.
Those are a hard integration dependency for autonomy status/run and were import-tested
only. No provider, queue, worker, service, API, network or autonomy execution was run.

## Side-effect boundary / límite de efectos

Safe checks performed: `stat`, SHA-256, source read, grep vocabulary scan, Python AST,
safe imports, launcher `--help`, launcher `version`, module `--help`, and autonomy
help commands. All permitted checks completed in foreground.

The imported module definitions expose these effects when their operational functions
are called: Git and `gh` subprocesses (`_run_git`, `_run_gh`), `ollama list`, SSH to
`mak@192.168.50.2`, ledger/tandas reads, `_logs/cauce_director/20260805/autonomia`
creation, brief writes, external batch/provider calls and ledger/batch updates. The
CLI also contains write-capable non-autonomy commands (for example `--salida`, queue,
job, airdrop and report paths). They were not invoked. The autonomy `run` command is
therefore not a read-only dry check merely because it accepts `--dry-run`: its dry path
still creates an output directory and writes briefs.

Residual risk / riesgo residual: `autonomia_status` itself can inspect GitHub/SSH or
local ledgers depending on executor and options; provider/ledger behavior belongs to
the imported MAK contracts and was not executed. There is no transaction boundary or
rollback implementation in `autonomia.py` for partial batch/brief/ledger writes.

## Rollback / reversión

No source, runtime, WIN, tests, logs, data, locks, DB, credentials, artwork or Git
state was changed. Consequently rollback for this review is “none required”. The
operational code has no explicit atomic rollback for `out_dir`, briefs or ledger
updates; a future authorized run needs an isolated fixture, pre-run snapshots/backups
of every ledger/output target, and a tested restore procedure before promotion.

## Commands and exit codes / comandos y códigos

- `/home/mak/venvs/flujo/bin/flujo --help`: exit 0.
- `/home/mak/venvs/flujo/bin/flujo version`: exit 0; observed `v0.56.1`.
- `PYTHONPATH=/home/mak/flujo/src python3 -m flujo --help`: exit 0.
- `/home/mak/venvs/flujo/bin/flujo autonomia --help`: exit 0.
- `/home/mak/venvs/flujo/bin/flujo autonomia status --help`: exit 0.
- `/home/mak/venvs/flujo/bin/flujo autonomia run --help`: exit 0.
- AST for `cli.py`, `__main__.py` and `autonomia.py`: PASS; safe imports for
  `flujo`, `flujo.cli`, `flujo.__main__` and `flujo.autonomia`: PASS.
- `pytest`: DEFER, unavailable; no installation attempted.

## Hashes / hashes

| Path | Exists | Size | SHA-256 |
|---|---:|---:|---|
| `pyproject.toml` | yes | 2009 | `61879f79b522e2d9a7ceb89453e43fcdceb943a19df2156cce377ea59729c7ff` |
| `src/flujo/cli.py` | yes | 127248 | `2dea3cc9df4398db877fd34374c9fc4dcf8de8eb2fa4ccac2b32a5065fc602a2` |
| `src/flujo/__main__.py` | yes | 59 | `41df9ff33d90dafa6210fdb1e8f045b09ae900258357114a424f36d0c845987a` |
| `src/flujo/autonomia.py` | yes | 16603 | `28d1c88ba02e0f6ec639db9bf65f0db992f5a145b26eb56e9dbb969e22841b81` |
| `/home/mak/venvs/flujo/bin/flujo` | yes | 223 | `223b79420741e4a345cfd878c342640d46697c75e6121796ee48987463a9c707` |

## Bilingual search coverage / cobertura bilingüe

Search vocabulary covered Spanish/English, accented/unaccented, casefold, aliases/slugs,
human labels and ASCII keys, interpreted by function, owner and consumer: plataforma /
platform; trabajo / work / job / task; estado / state / status; ruta / route / path;
servicio / service; cola / queue; conductor / dispatcher / runner / handler / worker;
entrega / delivery / output; respaldo / backup / archive / restore; legado / legacy;
reemplazado / superseded; obsoleto / obsolete; sin desarrollar / undeveloped; plus
autonomía / autonomy, proveedor / provider, tandas / batches, ledger and logs.
Residual false-negative risk: semantic aliases outside these four files or inside the
imported `cultura.mak_plataforma` contracts were not expanded into this slice.

## Decision / decisión

`ADOPTABLE_CANDIDATE` — retain this four-file group as the bounded next integration
candidate, with autonomy execution explicitly deferred and no runtime promotion implied.
The venv launcher is the verified consumer; system Python is not. Missing `wheel`,
unavailable pytest, and absent atomic rollback keep the residual risk open.

## Next action / próxima acción

Build a disposable, non-live Debian fixture for the MAK ledger/tandas contracts; verify
read-only status behavior without GitHub, SSH, providers or workers; then add an
explicit backup/restore test plan for output and ledger paths. Install nothing and do
not run real autonomy until that fixture and rollback boundary are approved.

## Confirmation / confirmación

Confirmed: no source, runtime, WIN, tests, logs, data, locks, DB, credentials, artwork
or Git state was modified. Only this report and its exact-header CSV were created.
