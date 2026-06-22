# Mapa del repo — flujo

Versión: v0.34.6

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
| `projects/plano/` | Generador de planos/riders/costos | Vivo |
| `projects/tapiz/` | Experimento/proyecto satélite visual | Referencia |

Nota: `projects/tapiz/vibecode.egg-info/` está trackeado históricamente. No agregar nuevos `.egg-info`.

## Documentación viva

| Ruta | Rol |
|---|---|
| `README.md` | Entrada principal |
| `PARA_IA.md` / `PARA_IA_CONTEXT.md` | Contexto rápido para agentes |
| `docs/AGENT_GUIDE.md` | Guía de trabajo para agentes |
| `docs/AIRDROP_REVIEW.md` | Revisión local de airdrops |
| `docs/AGENT_AIRDROP_PROTOCOL.md` | Protocolo que deben seguir agentes externos |
| `docs/CLI.md` / `docs/COMANDOS.md` | Referencia de comandos |
| `docs/CLEANUP.md` | Política de limpieza |
| `docs/LINEA_EDITORIAL.md` | Pendiente: brújula editorial/visual cuando se integre |

## Histórico / referencia

| Ruta | Rol | Regla |
|---|---|---|
| `_archive/` | Material archivado de etapas anteriores | No usar como fuente primaria salvo investigación |
| `reference_old/` | Scripts/GUI legado del proyecto anterior | No modificar salvo migración explícita |
| `checkpoints/` | Bitácora histórica de avances | No editar commits pasados; agregar nuevos checkpoints |
| `HANDOFF_*.md` antiguos | Contexto histórico | No corregir salvo casos críticos |

## Archivos generados/locales que NO deben entrar en airdrops

- `_airdrop/`
- `_airdrop_backups/`
- `_logs/`
- `__pycache__/`, `*.pyc`
- `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- `*.egg-info/` nuevos
- `data/*.db`, `*.sqlite*`
- `context/DAILY.md`, `context/dashboard.html`
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
