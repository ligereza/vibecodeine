# Fase 8 — mapa bilingüe de `mak_plataforma`

Identity: LUNA-08

## Objective

Mapear físicamente y lingüísticamente el departamento `mak_plataforma` entre
authoring/source, active runtime y historical local snapshot (WIN), y separar
presencia física de consumo probado. No hubo copia, fusión, despliegue ni
modificación de source, runtime o WIN.

## Scope

- Source: `/home/mak/flujo/cultura/mak_plataforma`.
- Runtime: `/home/mak/plataforma`.
- WIN: `/home/mak/WIN/flujo/cultura/mak_plataforma`.
- Consumers inspected safely: `mak_research`, `mak_curatoria`,
  `mak_conductor` y `/home/mak/flujo/src/flujo`.
- Profundidad máxima 1–2; archivos regulares de Python, shell, Markdown,
  texto, manifests/configs pequeños y unidades declaradas.
- Excluidos: logs, JSON/JSONL vivos, locks, bases, credenciales, `.env`,
  `.venv`, `__pycache__`, backups/tandas masivos y artefactos grandes.
- No se usaron Git, SSH, `192.168.50.2`, workers, cron, servicios ni
  `repair_mak_sync.py`.

## Language coverage matrix

| Concepto humano | ASCII/técnico y aliases buscados | Resultado de cobertura |
|---|---|---|
| plataforma | `plataforma`, `platform`, `mak_plataforma`, `platforma` | presente en rutas, docs, imports y runtime |
| trabajo | `trabajo`, `work`, `job`, `task` | presente en `trabajo.py`, colas y consumidores |
| guardia | `guardia`, `watchdog`, `guardian`, `vigia`, `vigilar` | presente en scripts, docs y rutas de watchdog |
| bitácora | `bitácora`, `bitacora`, `log`, `ledger`, `journal` | ASCII y español presentes; acento cubierto |
| estado | `estado`, `state`, `status`, `health`, `salud` | presente en contratos, health y módulos |
| carpeta | `carpeta`, `directory`, `dir`, `path`, `ruta`, `route` | presente en código, rutas y CLI |
| servicio | `servicio`, `service`, `unit`, `systemd` | unidades presentes; ejecución no probada |
| cron/timer | `cron`, `timer`, `crontab`, `scheduled` | declaraciones y texto; no ejecución |
| cola | `cola`, `queue`, `backlog`, `pending` | presente en `ledger`, `trabajo`, conductor |
| investigación | `investigación`, `investigacion`, `research` | ambas formas y consumer `mak_research` cubiertos |
| curatoria | `curatoria`, `curation`, `curate` | ambas formas y consumer `mak_curatoria` cubiertos |
| conductor | `conductor`, `dispatcher`, `runner`, `handler`, `worker` | consumidor real en `handler_registry`; worker solo textual |
| entrega | `entrega`, `delivery`, `deliver`, `output` | presente en `entregar.py` y handlers |
| respaldo | `respaldo`, `backup`, `archive`, `restore` | presente; no se ejecutó ningún backup |

Se probaron mayúsculas/minúsculas mediante comparación `casefold()`, nombres
con y sin diacríticos, slugs, etiquetas humanas, nombres de archivo y claves
ASCII. Riesgo residual: aliases no literales, imports construidos por reflexión,
variables externas, symlinks fuera del alcance 1–2 y consumidores invocados por
configuración viva excluida pueden producir falsos negativos. Por eso ninguna
ausencia se concluye desde una sola búsqueda o un solo nombre.

## Source/runtime/WIN map

| Layer | Root | Files in bounded inventory | Bytes | Interpretation |
|---|---|---:|---:|---|
| authoring/source | `/home/mak/flujo/cultura/mak_plataforma` | 60 | 963,704 | baseline de autoría |
| active runtime | `/home/mak/plataforma` | 133 | 1,723,651 | runtime con docs/variantes adicionales |
| historical local snapshot | `/home/mak/WIN/flujo/cultura/mak_plataforma` | 64 | 992,042 | evidencia histórica, no runtime |

Las 60 rutas comunes source/runtime/WIN fueron comparadas con SHA-256. Hubo
4 diferencias source/runtime y 13 source/WIN; las diferencias runtime/WIN
también fueron 13. Cambios relevantes: `backlog_codex.txt`, `coherence.py`,
`entregar_micelio.py`, `tandas.py` y variantes de `hub.py`, `entregar.py`,
`crontab.mak`, unidades `.service`, `providers.py`, `capataz.py`,
`discernment.py`, `energia.py` y `chat_agente.py`. No se promovió ninguna.

## Consumer/dependency map

### Consumo probado

- `mak_conductor.handler_registry` importa por referencia funcional
  `cultura.mak_plataforma.providers`, `discernment`, `mineria_rd`,
  `visual_index`, `puente_issues`, `trabajo`, `tandas`, `entregar`, `revisor`,
  `capataz`, `junta`, `latido`, `material` y `backlog_codex`; import foreground
  exitoso y registry observado con 30 handlers.
- `mak_curatoria.diagnostico_proyectos` importa
  `cultura.mak_plataforma.ledger`; import foreground exitoso.
- `mak_curatoria.ingesta_archivo` importa `cultura.mak_plataforma.visual_index`;
  AST e import del módulo exitosos.
- `flujo.autonomia` importa `ledger`, `providers` y `tandas`; import foreground
  exitoso. `flujo.cli` referencia `tandas` y el comando `flujo --help` pasó.
- `mak_research.interfaz` inserta `/home/mak/plataforma` y carga
  `filtro_entrada` de forma tolerante; esto prueba una dependencia declarada,
  no que el proceso research esté activo.

### Presencia o candidato, no ejecución probada

`mak-hub.service`, `mak-xio.service`, `crontab.mak`, `watchdog_mak.sh` y
`backup.sh` existen o son referenciados. Se clasifican como candidatos
declarativos/textuales: no se inspeccionó systemd, crontab ni procesos y no se
inició ningún servicio, timer, cron o worker.

## Hash/diff summary

El CSV registra 21 archivos críticos con tamaño y SHA-256. Los hashes se
calcularon con `pathlib.Path.read_bytes()` y `hashlib.sha256()`. Las diferencias
de texto pequeñas se evaluaron por rutas comunes; no se aplicaron diffs ni
reemplazos. `trabajo.py`, `ledger.py`, `guardia.py` y `latido.py` son iguales en
las tres superficies; `entregar.py`, `hub.py`, `crontab.mak` y las unidades
declaradas tienen divergencias históricas/runtime descritas arriba.

## Candidate vertical slice

`cultura.mak_conductor.handler_registry` → `cultura.mak_plataforma.ledger` /
`providers` / `tandas` / `entregar` es el slice candidato. Incluye consumidor
real, módulos fuente, entrypoints y dependencias explícitas. En esta fase solo
se verificó import/registry/help en foreground; no se ejecutó un job ni se
promovió ningún archivo. El siguiente paso debe ser un dry-run acotado de un
handler que no toque datos vivos, con contrato de entradas/salida y owner
explícito.

## No-change items

- No modificar source, runtime o WIN durante el mapa.
- No copiar ni fusionar variantes.
- No ejecutar servicios, cron, watchdogs, workers, backups o `repair_mak_sync.py`.
- No tratar la presencia de una unidad `.service` o script como ejecución real.
- No reparar `panel_directivo.py`: AST falla con `SyntaxError` en línea 145 y
  no existe contrato autorizado en esta fase.
- No resolver divergencias históricas de `entregar.py`, `hub.py`, `tandas.py`,
  `crontab.mak` o unidades sin owner/contrato.

## Risks

- `panel_directivo.py` del runtime no parsea; cualquier consumidor por reflexión
  quedaría oculto o fallaría antes de importar.
- Archivos vivos excluidos pueden contener rutas/aliases adicionales.
- Imports dinámicos, subprocesses y configuración externa pueden ocultar
  consumidores no literales.
- El snapshot WIN es evidencia histórica y no prueba integración actual.
- Las declaraciones service/cron podrían existir sin estar habilitadas.

## Verification log

- Read-first: `agents.md` y `context/LAST_HANDOFF.md` leídos antes de actuar.
- Inventory: script Python stdlib con `pathlib`, profundidad 1–2 y exclusiones;
  exit 0; counts 60/133/64.
- Hashes: Python stdlib `hashlib.sha256`; exit 0; 60 rutas comunes.
- AST: `PYTHONDONTWRITEBYTECODE=1`; 325 archivos parseados, 1 fallo conocido:
  `/home/mak/plataforma/panel_directivo.py`, línea 145.
- Imports: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/mak/flujo:/home/mak/flujo/src`
  importó `handler_registry`, diagnóstico de curatoria, ingesta y `flujo.autonomia`;
  exit 0; 30 handlers observados.
- Help: `python3 -m flujo --help` exit 0; `ledger --help` exit 0;
  `trabajo --help` exit 0 sin salida. No se iniciaron servicios.
- CSV: Python stdlib confirmó header exacto, 21 filas de datos, 13 columnas y
  hashes/tamaños consistentes.

## Next action

Diseñar y ejecutar un dry-run foreground, sin datos vivos, del handler de
`mak_conductor` que consuma `ledger`/`tandas`, después de fijar owner, contrato
de entrada/salida y límites de escritura. Mantener todas las divergencias y
el fallo AST como `no_change` hasta esa verificación.

## Last checkpoint

2026-08-14 America/Santiago — LUNA-08 completó el mapa bilingüe, la comparación
SHA-256, la prueba de consumidores y la persistencia de artefactos; no hubo
cambios en source/runtime/WIN ni procesos persistentes.
