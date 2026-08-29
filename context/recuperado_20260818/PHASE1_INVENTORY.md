# PHASE1_INVENTORY

## Objective

Construir un inventario físico reproducible de MAK, distinguiendo superficie operativa, baseline, evidencia histórica, salidas, departamentos, herramientas, datos, servicios y configuración. Este documento registra evidencia observada; no implica integración.

## Scope

Alcance inicial: `/home/mak/*`, con tratamiento explícito de `/home/mak/flujo` como baseline y `/home/mak/WIN` como evidencia histórica. Se registran rutas, tipo, tamaño, mtime, permisos, raíz, categoría, procedencia, estado y candidatos de propietario/consumidor. Se excluyen contenidos sensibles.

## Method

1. Leer el contrato operativo `/home/mak/flujo/agents.md` antes de inspeccionar otras superficies.
2. Enumerar raíces y archivos con `find`, `stat`, `du` y `file`; leer selectivamente nombres, manifests, README y configs seguros.
3. Mantener CSV append-only por lotes y sincronizar este MD después de cada lote importante.
4. No usar Git como inventario; no copiar árboles completos, iniciar servicios ni modificar evidencia histórica.

## Physical roots

Checkpoint de inicio: 2026-08-14T18:22:37-04:00.

Lote raíz 2026-08-14T18:24:xx-04:00: `/home/mak` enumerado a profundidad 1; `/home/mak/WIN` enumerado a profundidad 1. Se registraron 129 filas de raíz en CSV, incluyendo raíces ocultas y literales anómalas. `du -sh` observó aproximadamente: `curatoria_inbox` 173G, `RD` 57G, `WIN` 7.9G, `venvs` 6.6G, `portfolio_media` 5.5G, `flujo` 850M, `apps` 1.4G, `blender` y `blender-4.5.3-viejo` 1.2G cada uno. El tamaño de directorio en CSV es el tamaño del inode, no el uso recursivo.

Raíces cubiertas: MAK operativo (`flujo`, `plataforma`, `research`, `curatoria`, `codex`, `post`, `xio_puente`, `RD`, `apps`, `src`, `labs`, `n8n-local`, `actions-runner`, `vigia`, `vibecodeine`), datos/salidas (`curatoria_inbox`, `portfolio_media`, `renders`, `backups`, `rollback`, `quarantine`), herramientas/entornos (`blender*`, `models`, `venvs`, `venv-providers`, `searxng`) y superficies de usuario/configuración. WIN cubierto a raíz y primer nivel (`claude_sesiones`, `codex`, `flujo`, `incoming-20260813`, `manifests`, `updates-20260813`).

## Department/tool map

| Physical path | Classification | Owner candidate | Consumer candidate | Evidence |
| --- | --- | --- | --- |
| `/home/mak/flujo` | authoring/integration baseline | flujo maintainers | CLI, tests, web | pyproject, requirements, README |
| `/home/mak/plataforma`, `/home/mak/research`, `/home/mak/curatoria`, `/home/mak/post`, `/home/mak/xio_puente`, `/home/mak/codex` | department/runtime candidates | unknown | unknown | root metadata |
| `/home/mak/apps`, `/home/mak/src`, `/home/mak/labs`, `/home/mak/blender*`, `/home/mak/models`, `/home/mak/venvs` | tools, source, model and environment surfaces | unknown | unknown | root metadata and selective names |
| `/home/mak/RD`, `/home/mak/portfolio_media`, `/home/mak/renders`, `/home/mak/Escritorio` | outputs/media | RD or portfolio candidate | unknown | `du -sh`, root metadata |
| `/home/mak/WIN` | historical archive/evidence | migration owner unknown | reconciliation/inventory | README_ORIGIN and manifests names |

Possible functional duplicates preserved: `blender` vs `blender-4.5.3-viejo`; `Descargas` vs `descargas`; `Documents` vs `Documentos`; `Imágenes`/`Música`/`Vídeos` vs localized/English user surfaces; `apps` vs `Apps`; multiple department-looking roots and the literal paths beginning `/home/mak/\home\mak\flujo`. No merge or deletion performed.

## Evidence exclusions

- Se excluyó contenido de `/home/mak/.aws`, `.gnupg`, `.ssh`, `.pki`, `.config`, `.copilot` y archivos de sesión/historial con permisos privados; solo se registró metadata de raíces cuando fue visible.
- No se leyeron `.env`, tokens, credenciales, bases privadas, historial de shell, authorities, logs privados ni archivos de datos masivos. Se registran únicamente ruta, tipo/tamaño/mtime/modo y motivo.
- `/home/mak/WIN` se trató como evidencia histórica; no se ejecutó, editó ni publicó.

## Findings

- Las salidas obligatorias no existían al inicio: `PHASE1_INVENTORY.md`, `.csv` y `.duckdb`.
- El contrato operativo confirma que `/home/mak/WIN` es archivo histórico y `/home/mak/flujo` es baseline de autoría/integración.
- El CSV contiene 144 filas de evidencia (1 cabecera + 144 registros): 129 raíces físicas y 15 artefactos seguros seleccionados (baseline y manifiestos WIN). Hay 1 ruta duplicada por solapamiento intencional de lotes (`/home/mak/WIN/README_ORIGIN.md`); no se fusionaron filas para conservar provenance de cada lote.
- `flujo` declara paquete `flujo` versión `0.56.1`, entrypoint `flujo = flujo.cli:app`, Python `>=3.10`, dependencias runtime y extra `duckdb` en `dev`.
- El archivo WIN declara snapshot Windows importado el 2026-08-13, fuentes `C:\IA\flujo`, Codex y sesiones Claude; sus manifiestos incluyen reconciliación y sanitización de secretos.
- Conteo físico observado sin seguir montajes: `/home/mak` 516871 archivos y ~308,418,000,000 bytes; `/home/mak/WIN` 53099 archivos y ~8,204,310,000 bytes. Son totales de superficie, no filas CSV exhaustivas.

## Conflicts/risks

- `/home/mak/OneDrive` es inaccesible: `find`, `du`, `stat` y `file` devuelven `El otro extremo de la conexión no está conectado` / `Transport endpoint is not connected`.
- Hay 57G en `RD` y 173G en `curatoria_inbox`; expandirlos puede mezclar salidas, datos privados y evidencia. Requieren lote acotado por extensión/manifest antes de catalogación profunda.
- Existen raíces con nombres literales anómalos (`/home/mak/\home\mak\flujo\...`) y duplicados potenciales por mayúsculas/idioma; función y propiedad siguen sin resolver.
- DuckDB no está disponible: `command -v duckdb` no produjo ruta y `python3 import duckdb` terminó con `ModuleNotFoundError: No module named 'duckdb'`. No se instaló nada ni se creó DB; CSV es la fuente estructurada.

## Verification log

- `date -Is && sed -n '1,240p' /home/mak/flujo/agents.md`: exit 0; contrato leído antes del escaneo.
- `find /home/mak/flujo/context ...` y `stat ...`: exit 0 global; tres salidas obligatorias no existían.
- `find /home/mak -mindepth 1 -maxdepth 1 ...`: exit 0 con error de transporte al resolver `OneDrive` en la primera ejecución; segunda ejecución con stderr oculto produjo 129 entradas visibles.
- `du -sh -- /home/mak/*`: exit 1 por `OneDrive`; observó tamaños de raíces restantes.
- `find ... -type f ... | awk ...`: exit 0; 516871 archivos y ~308418000000 bytes MAK; WIN: 53099 y ~8204310000 bytes.
- `sed` selectivo sobre `flujo/README.md`, `pyproject.toml`, `requirements*.txt`, `WIN/README_ORIGIN.md`: exit 0; se observaron identidad del paquete, dependencias y procedencia histórica sin credenciales.
- `command -v duckdb; python3 import duckdb`: exit 0 del comando compuesto; DuckDB no disponible (`ModuleNotFoundError`).
- `apply_patch` creación incremental de MD/CSV y anexado de lote: exit 0; archivos creados sin sobrescribir evidencia existente.
- `python3` con `csv.DictReader` sobre `PHASE1_INVENTORY.csv`: exit 0; 144 filas legibles, cabecera exacta, 0 rutas vacías, 1 duplicado de provenance documentado, raíces MAK=125/WIN=19.
- `grep -c '^## ' PHASE1_INVENTORY.md` y `grep -c '^## Last checkpoint$' ...`: exit 0 esperado; se verificaron las secciones requeridas y el checkpoint final.

## Next action

Validar el CSV con un lector estándar, contar registros por raíz/categoría, verificar `Last checkpoint` y conservar CSV como fuente estructurada. Después, LUNA debe elegir un lote acotado para profundizar manifests/entradas de departamentos sin expandir datos masivos.

## Last checkpoint

2026-08-14T18:25:01-04:00 — raíces MAK/WIN, tamaños, manifiestos seguros, exclusiones e indisponibilidad DuckDB registrados; CSV validado con 144 registros legibles; DB no creado por dependencia ausente.
