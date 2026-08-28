# Script inventory

Measured version: **0.56.1** (`pyproject.toml` + `src/flujo/version.py`),
verified 2026-08-28 against `ls scripts/`, `Makefile`,
`.github/workflows/*.yml` and a grep for invokers across `src/`, `tools/`,
`cultura/` and `scripts/`.

This inventory keeps agents from mistaking a legacy wrapper for the live core.
Every row declares its invoker so the claim is checkable: if the column says
`Makefile`, then `grep -n <script> Makefile` must return something.

Language: English ASCII, per the Language section of `agents.md` for operational
metadata.

## The 29 scripts, measured

A script with NO INVOKER is not dead: it may be a utility a person runs by hand.
What the column asserts is that no `Makefile`, workflow or module calls it --
that nothing will exercise it on its own.

| Script | Measured invoker |
|---|---|
| `piezas_generar.py` | `render_piezas_vectoriales.yml`, `Makefile`, `brief_to_project.py` |
| `flujo.py` | `src/flujo/version.py`, `flujo_health.py`, `run_airdrop_checks.py`, `generar_catalogo_rd.py` |
| `flujo_daily.py` | `Makefile`, `abrir_dashboard.sh`, `nuevo_pedido.sh` |
| `hub_smoke.py` | `src/flujo/cli.py`, `run_airdrop_checks.py` |
| `validate_airdrop.py` | `src/flujo/cli.py`, `run_airdrop_checks.py` |
| `abrir_dashboard.sh` | `Makefile`, `nuevo_pedido.sh` |
| `flujo_pipeline.py` | `Makefile`, `nuevo_pedido.sh` |
| `flujo_health.py` | `render_piezas_vectoriales.yml` |
| `piezas_check_outputs.py` | `render_piezas_vectoriales.yml` |
| `run_airdrop_checks.py` | `airdrop_gate.yml` |
| `flyer_create_project.py` | `Makefile` (`make new-flyer`) |
| `limpiar_basura.sh` | `Makefile` (`make clean`) |
| `setup.sh` | `Makefile` (`make install`) |
| `checkpoint.sh` | `src/flujo/airdrop.py` |
| `_common.py` | `flujo_health.py` |
| `apply_airdrop.sh` | NO INVOKER |
| `finish_airdrop.sh` | NO INVOKER |
| `backlog_list.py` | NO INVOKER |
| `brief_to_project.py` | NO INVOKER |
| `export_propuesta_pdf.py` | NO INVOKER |
| `find_duplicates.py` | NO INVOKER |
| `flyer_duplicates_report.py` | NO INVOKER |
| `flyer_set_input.py` | NO INVOKER |
| `generar_catalogo_rd.py` | NO INVOKER |
| `github_setup_labels.py` | NO INVOKER |
| `nuevo_pedido.sh` | NO INVOKER |
| `pdf_probe_basic.py` | NO INVOKER |
| `sanitize_sensitive.py` | NO INVOKER |
| `suggest_repo_hygiene.py` | NO INVOKER |

15 with an invoker, 14 with none.

## Airdrop: the chain is complete and its input does not exist

`_airdrop/` **is not in the tree**. Neither is `docs/AGENT_AIRDROP_PROTOCOL.md`,
which the previous version of this inventory cited as its protocol. What does
exist is the whole apparatus that serves it:

- `scripts/apply_airdrop.sh`, `finish_airdrop.sh`, `validate_airdrop.py`,
  `run_airdrop_checks.py`
- `src/flujo/airdrop.py` (494 lines) and the `flujo airdrop` command
- `.github/workflows/airdrop_gate.yml`, triggered by `release: published`
- 42 tests in `tests/test_airdrop.py`, `test_airdrop_signing.py`,
  `test_validate_airdrop.py`, `test_run_airdrop_checks.py`

The 42 tests pass today. They pass because they work over `tmp_path`, not over
`_airdrop/`. And `flujo doctor` reports `airdrop pendiente: OK -- no`, so the
absence of the subsystem reads as health.

Retiring that chain touches code, tests and a workflow -- not files -- so it is
declared here and not executed. See `docs/AUTORIDAD.md`.

## Corrections against the previous version (2026-07-18)

| Previous claim | Measurement 2026-08-28 |
|---|---|
| version pinned four minors behind | real version is `0.56.1`, per `pyproject.toml` |
| "`finish_airdrop.sh` mentions checkpoint.sh, **already nonexistent**" | `scripts/checkpoint.sh` **exists** and `src/flujo/airdrop.py` invokes it |
| `scripts/app.py` listed as an active Web/dashboard script | **does not exist** |
| legacy archived in `_archive/legacy_20260703_1413/` | `_archive/` **does not exist**; the cited destination cannot be inspected |
| legacy archived in `_archive/legacy_20260718_0110/scripts_oneshot/` | same |
| protocol at `docs/AGENT_AIRDROP_PROTOCOL.md` | **does not exist** |
| "Detalle en the repository hygiene tests." | a sentence cut in half in the previous version |
| `generar_catalogo_rd.py` | exists in `scripts/` and was missing from the inventory |

The common cause: the inventory asserted state in prose and named files without
a verifiable path. That is why the table above carries an invoker column.

## Retired legacy wrappers

The `job_*.py`/`job_new.sh`, `privacy_*.py`, `project_*.py`,
`piezas_formatos.py`, `piezas_validate_config.py`, `piezas_add_component.py`,
`piezas_components.py`, `piezas_project_summary.py`, `flyer_from_email.py`,
`flyer_analyze.py`, `flyer_index*.py/.sh`, `flyer_status*.py/.sh`,
`flyer_latest.sh`, `flyer_list.sh`, `ig_download.py`, `ig_redownload.py`,
`rider_new.py`, `rider_presets.py` family, plus the one-shot `cleanup_*.sh/py`,
`flujo_clean_generated.py`, `soft_cleanup.py`, `cleanup_demo_artifacts.sh` and
`cleanup_ig_temp_folders.sh`, are no longer in `scripts/`.

**Where they went cannot be verified**: the two archive paths the previous
version cited (`_archive/legacy_20260703_1413/`,
`_archive/legacy_20260718_0110/`) do not exist. The CLI equivalence table is in
`docs/CLI.md`, section "Migracion desde scripts legacy". Use `flujo job`,
`flujo flyer-import`, `flujo analyze`, `flujo index`, `flujo ig-redownload`.

## CLI equivalent where one exists

| Script | Prefer |
|---|---|
| `flujo_daily.py` | `flujo daily` |
| `flujo_health.py` | `flujo health` |
| `flujo.py` | `flujo ...` |
| `brief_to_project.py` | `flujo brief to-project` |
| `piezas_generar.py` | `flujo render run` (the script stays live: `make render` and CI call it) |
| `flyer_create_project.py` | no direct equivalent; stays live through `make new-flyer` |

## Hygiene: it exists and nothing triggers it

Three scripts do exactly the cleanup work this repo needs and none has an
invoker:

- `find_duplicates.py` -- duplicates by content hash
- `suggest_repo_hygiene.py` -- flags files pointing at dead docs or dead code
- `sanitize_sensitive.py` -- replaces credentials with placeholders

`limpiar_basura.sh` is called by `make clean`, but it only removes
`__pycache__` and generated outputs.

## Rule for future script changes

If a change touches a legacy script, it must explain why it does not touch the
CLI at `src/flujo/cli.py` or the live module under `src/flujo/` first.

And if it adds a row to this inventory, the row declares an invoker or declares
NO INVOKER. There is no third option: prose without a path is what left this
document four minor versions stale with nothing noticing.
