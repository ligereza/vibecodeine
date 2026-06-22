# Mapa del repo — flujo

Versión: v0.34.10 (historia consolidada)

Este mapa existe para que humanos y agentes de IA entiendan rápido qué carpetas están vivas, cuáles son históricas y qué NO deben tocar sin permiso.

## Núcleo vivo

| Ruta | Rol | Estado |
|---|---|---|
| `src/flujo/` | Paquete Python principal y CLI `flujo` | Vivo |
| `tests/` | Tests automatizados | Vivo |
| `scripts/validate_airdrop.py` | Validador de entregas `_airdrop/` | Vivo |
| `scripts/run_airdrop_checks.py` | Runner seguro con logs y checkpoint solo si pasa | Vivo |
| `.github/workflows/ci.yml` | CI real: install, compileall, health, pytest | Vivo |
| `pyproject.toml` | Metadata, dependencias y versión del paquete | Vivo |
| `requirements.txt` | Dependencias equivalentes para instalación simple | Vivo |

## Operación diaria

| Ruta | Rol | Estado |
|---|---|---|
| `jobs/_template/` | Plantilla versionada de jobs | Vivo |
| `inbox/` | Ejemplos/entradas de prueba | Vivo con cuidado |
| `projects/flyer_eventos/` | Proyectos flyer de ejemplo/estructura | Mixto |
| `projects/piezas_vectoriales/` | Proyectos y plantillas vectoriales | Vivo/ejemplos |
| `tools/` | Especificaciones, componentes y plantillas base | Vivo |
| `schemas/` | Schema intake JSON y ejemplos | Vivo |

## Proyectos satélite

| Ruta | Rol | Estado |
|---|---|---|
| `projects/piezas_vectoriales/` | Proyectos y plantillas vectoriales | Vivo |
| `projects/flyer_eventos/` | Flujos reales de eventos | Operativo |
| `projects/plano/` | Generador de planos/riders/costos | Vivo |
| `projects/tapiz/` | Experimento visual (VibeCode) | Referencia |
| `projects/aistetic/` | **Línea editorial central** (nuevo) | Nuevo — fuente de verdad estética |
| `projects/aistetic/ejemplos/` + `json/` | Ejemplos reales + JSONs descriptivos para análisis de IA | Lugar donde se "alimenta" la identidad visual |

Ver también `docs/FOR_EXTERNAL_AI.md` cuando se alimente el repo completo a una IA.

Nota: `projects/tapiz/vibecode.egg-info/` está trackeado históricamente. No agregar nuevos `.egg-info`.

## Documentación viva

| Ruta | Rol | Prioridad para nueva IA (bajo tokens) |
|---|---|---|
| `PARA_IA_CONTEXT.md` | Contexto rápido para agentes | Alta |
| **`context/LAST_HANDOFF.md`** | **Estado actual + qué sigue (single source of truth para continuidad)** | **MÁXIMA** |
| `README.md` | Entrada principal | Media |
| `docs/AGENT_GUIDE.md` | Guía de trabajo para agentes | Media |
| `docs/REPO_MAP.md` | Qué está vivo, histórico o generado | Media |
| `docs/CLI.md` / `docs/COMANDOS.md` | Referencia de comandos | Baja |
| `docs/AIRDROP_REVIEW.md` + `docs/AGENT_AIRDROP_PROTOCOL.md` | Protocolo airdrops | Baja (solo al entregar) |

**Regla de ahorro de tokens:** Una IA nueva casi nunca necesita leer más de los dos primeros + `flujo daily` + `flujo job next`.

## Histórico / referencia

| Ruta | Rol | Regla |
|---|---|---|
| `_archive/` | Material archivado de etapas anteriores | No usar como fuente primaria salvo investigación |
| `reference_old/` | Scripts/GUI legado del proyecto anterior | No modificar salvo migración explícita |
| `checkpoints/` | Bitácora histórica de avances (detalle de intentos) | No editar; nuevos checkpoints solo si valiosos |
| `docs/handoffs/` | Notas de agentes (HANDOFF, HOTFIX, AUDITORIA, REVISION) | Ubicación consolidada para higiene de raíz. No agregar ruido de tareas a medias |

**Nota de limpieza (2026-06):** Commits de v0.34.x con tareas parciales/fallidas fueron consolidados en un solo commit ("v0.34 consolidated"). El detalle queda en los archivos de handoffs/ y checkpoints/.

## Archivos generados/locales que NO deben entrar en airdrops

- `_airdrop/`
- `_airdrop_backups/`
- `_logs/`
- `__pycache__/`, `*.pyc`
- `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- `*.egg-info/` nuevos
- `data/*.db`, `*.sqlite*`
- `context/DAILY.md`, `context/dashboard.html` (LAST_HANDOFF.md **sí** se versiona: es el estado para continuidad de IAs)
- `projects/**/salida_generada/`
- media pesada: `*.mp4`, `*.mov`, `*.psd`, `*.ai`, `*.zip`, etc.

## Regla para agentes

Antes de proponer cambios, identifica si el archivo pertenece a:

1. Núcleo vivo.
2. Operación diaria.
3. Documentación viva.
4. Histórico/referencia.
5. Generado/local.

Si es histórico o generado, no lo uses como base de cambios sin avisar.
