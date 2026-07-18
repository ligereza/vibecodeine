# Inventario de scripts

Version: v0.52.0 (verificado 2026-07-18, contra `ls scripts/` + `Makefile` + `.github/workflows/*.yml` reales)

Este inventario evita que agentes confundan wrappers legacy con el núcleo real.

## Scripts críticos de proceso (airdrop)

| Script | Uso |
|---|---|
| `scripts/apply_airdrop.sh` | Copia `_airdrop/` al repo y crea backup. No hace tests. |
| `scripts/finish_airdrop.sh` | Muestra `git status` al cerrar un airdrop manual (menciona checkpoint.sh, ya inexistente). |
| `scripts/validate_airdrop.py` | Valida `_airdrop/` antes de aplicar (ver `docs/AGENT_AIRDROP_PROTOCOL.md`). |
| `scripts/run_airdrop_checks.py` | Flujo seguro: valida, aplica, `pip install`, compileall, pytest, health, version+changelog, hub smoke, checkpoint. |
| `scripts/cleanup_demo_artifacts.sh` | Limpieza controlada de demos/tests históricos. |
| `scripts/cleanup_ig_temp_folders.sh` | Limpia carpetas temporales Instagram. |

## Wrappers legacy archivados (ya no viven en `scripts/`)

Toda la familia `job_*.py`/`job_new.sh`, `privacy_*.py`, `project_*.py`, `piezas_formatos.py`,
`piezas_validate_config.py`, `piezas_add_component.py`, `piezas_components.py`,
`piezas_project_summary.py`, `flyer_from_email.py`, `flyer_analyze.py`, `flyer_index*.py/.sh`,
`flyer_status*.py/.sh`, `flyer_latest.sh`, `flyer_list.sh`, `ig_download.py`, `ig_redownload.py`,
`rider_new.py`, `rider_presets.py` fue archivada en `_archive/legacy_20260703_1413/` (2026-07-03)
por estar superada por la CLI Typer. Los one-shot spent (`cleanup_safe.sh`,
`cleanup_moderate.sh`, `cleanup_legacy_aggressive.sh`, `cleanup_repo_hygiene_20260630.py`,
`cleanup_v0359_windows_paths.py`) fueron archivados en
`_archive/legacy_20260718_0110/scripts_oneshot/` (2026-07-18): sus targets ya no existen. Tabla de equivalencias completa en
`docs/CLI.md` ("Migracion desde scripts legacy"). No están en `scripts/`; no las
uses como referencia de código vivo.

## Wrappers/compatibilidad CLI (vigentes)

Cuando exista equivalente `flujo ...`, preferir la CLI; estos scripts siguen presentes porque
`Makefile` o `.github/workflows/*.yml` todavía los invocan directamente.

| Familia | Preferir |
|---|---|
| `flujo_daily.py` | `flujo daily` |
| `flujo_health.py` | `flujo health` |
| `flujo.py` (wrapper unificado pre-Typer) | `flujo ...` (sin uso real en CI/Makefile) |
| `brief_to_project.py` | `flujo brief to-project` |
| `piezas_generar.py` | `flujo render run` (sigue vivo: usado por `make render` y CI) |
| `flyer_create_project.py` | sin equivalente CLI directo (crea proyecto manual en `projects/flyer_eventos/`; `flujo flyer-import`/`flujo eventos flyer-auto` cubren los casos con correo/Instagram); sigue vivo: usado por `make new-flyer` |

## Scripts activos por área (verificado contra `ls scripts/` real)

### Airdrop / mantenimiento de repo

- `apply_airdrop.sh`, `finish_airdrop.sh`, `validate_airdrop.py`, `run_airdrop_checks.py`
- `cleanup_demo_artifacts.sh`, `cleanup_ig_temp_folders.sh`
- `flujo_clean_generated.py` (limpia `__pycache__`, `*.pyc` y generados versionados por error)
- `limpiar_basura.sh` (usado por `make clean`)
- `soft_cleanup.py` (recorta espacios finales en archivos de texto, no destructivo)
- `suggest_repo_hygiene.py` (solo sugiere, no borra ni mueve nada; ver `docs/HIGIENE_REPO.md`)
- `sanitize_sensitive.py` (reemplaza credenciales/secrets por placeholders en texto)
- `find_duplicates.py` (detecta archivos duplicados por hash de contenido)
- `github_setup_labels.py` (crea/actualiza labels de GitHub; requiere `GITHUB_TOKEN`)

### Jobs / briefs

Los wrappers `job_*.py` fueron archivados (ver arriba); usar `flujo job ...`.

- `brief_to_project.py` (crea proyecto base `piezas_vectoriales` desde `jobs/.../brief.yaml`; duplica `flujo brief to-project`, sin uso en CI/Makefile)
- `backlog_list.py` (lista `jobs/_backlog/*.md`)
- `nuevo_pedido.sh` (atajo bash: correo -> job -> dashboard; no referenciado por Makefile/CI)

### Render / proyectos

- `piezas_generar.py` (usado por `make render` y `.github/workflows/render_piezas_vectoriales.yml`)
- `piezas_check_outputs.py` (usado por `.github/workflows/render_piezas_vectoriales.yml`)
- `export_propuesta_pdf.py` (PDF de propuesta RD por pack de servicio: brief + evento + plano + rider + cotización)
- `pdf_probe_basic.py` (inspección básica de PDF sin dependencias externas: páginas, MediaBox/CropBox/TrimBox)

### Flyers / Instagram

Los wrappers `flyer_from_email.py`, `flyer_analyze.py`, `flyer_index*.py`, `ig_*.py` fueron
archivados (ver arriba); usar `flujo flyer-import`, `flujo analyze`, `flujo index`, `flujo ig-redownload`.

- `flyer_create_project.py` (usado por `make new-flyer NAME="..."`)
- `flyer_duplicates_report.py` (solo reporta posibles proyectos duplicados, no borra)
- `flyer_set_input.py`

### Web / dashboard / operación diaria

- `app.py` (interfaz Gradio legacy standalone; la entrada real es `flujo app` / `flujo serve`)
- `hub_smoke.py` (smoke test del hub local; lo invoca `scripts/run_airdrop_checks.py`)
- `abrir_dashboard.sh` (usado por `make dashboard`)
- `flujo_daily.py` (usado por `make daily`; equivalente CLI: `flujo daily`)
- `flujo_health.py` (usado por `.github/workflows/render_piezas_vectoriales.yml`; equivalente CLI: `flujo health`)
- `flujo_pipeline.py` (usado por `make pipeline NAME="..." EMAIL=...`; correo -> job -> proyecto -> render con inferencia de tipo/medidas)
- `flujo.py` (wrapper unificado legacy pre-Typer, ver `docs/COMANDO_UNIFICADO.md`; sin uso real en CI/Makefile, preferir `flujo ...`)
- `setup.sh` (usado por `make install`)
- `_common.py` (helpers compartidos entre scripts; no es ejecutable por sí mismo)

## Regla para futuros airdrops

Si un airdrop modifica scripts legacy, debe explicar por qué no modifica primero la CLI `src/flujo/cli.py` o el módulo vivo correspondiente en `src/flujo/`.
