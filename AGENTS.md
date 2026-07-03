# AGENTS.md - contrato operativo de flujo

Este archivo es la entrada obligatoria para cualquier agente. El objetivo no es decorar el repo: el objetivo es que un agente sepa que hacer, como entregar, como verificar y como dejar continuidad.

## Orden obligatorio de lectura

1. `AGENTS.md`
2. `context/LAST_HANDOFF.md`
3. `docs/AGENT_AIRDROP_PROTOCOL.md`
4. `docs/REPO_MAP.md`
5. Archivo especifico de la tarea

Si hay contradiccion, manda este orden:

1. Instruccion directa del usuario
2. `AGENTS.md`
3. `context/LAST_HANDOFF.md`
4. docs especificos
5. README

## Identidad del asistente

El asistente de este repo se llama **Vibo**. El usuario lo llama asi en vez de "Claude" o "agente". Cualquier agente que trabaje aqui debe responder a ese nombre y usarlo al firmar handoffs conversacionales. La definicion canonica vive en `CLAUDE.md` (raiz); si el usuario cambia el nombre, actualizar ambos archivos en el mismo cambio.

## Entorno del usuario

```txt
Sistema principal: Windows + Git Bash
Comandos para usuario: py, no python
LAST_HANDOFF.md: ASCII-only
Credenciales: nunca guardar tokens, cookies, claves, datos privados ni archivos reales sensibles
Repo remoto: https://github.com/ligereza/vibecodeine/
QA visual real: el usuario tiene Illustrator local. Para piezas graficas nuevas
(suplementos, flyers), generar el paquete con "py -m flujo suplementos illustrator
<nombres...>" y dejar que el usuario lo revise ahi antes de dar por buena una pieza.
No depender de renderizadores headless (cairosvg no tiene su libreria nativa en Windows).
```

## Regla central

Todo agente debe dejar el repo mas operativo que antes. No se aceptan parches a medias.

Prohibido entregar como final:

```txt
TODO
completar luego
...
NotImplementedError
try/except: pass silencioso
cambios sin verificacion
archivos generados/caches dentro del airdrop
```

## Flujo de trabajo obligatorio

Antes de cambiar:

1. Leer `context/LAST_HANDOFF.md`.
2. Identificar area: core, web, RD/suplementos, Studio/eventos, Resolume, docs, pipeline.
3. Revisar archivos relacionados antes de editar.
4. Hacer cambios minimos, completos y verificables.
5. Actualizar `context/LAST_HANDOFF.md` en ASCII-only.
6. Entregar por airdrop si no tienes push directo.

## Continuidad entre sesiones (obligatorio)

Una auditoria detecto perdida de contexto entre sesiones: `context/SESSION_STATE.json` quedo 6 versiones desfasado (v0.42.1 vs v0.48.5 real) y `context/AVANCES_BLOCK.txt` seguia hablando de "datadrop" cuando el foco real ya era Resolume/Chataigne. Reglas firmes para no repetirlo:

1. Al cerrar CADA sesion, actualiza `context/LAST_HANDOFF.md` y `context/SESSION_STATE.json` con la version/fecha real (deben coincidir con `pyproject.toml` y `src/flujo/version.py`) y el estado real `done/doing/next/blockers`. No dejes version o fecha vieja "porque no hubo release" -- si trabajaste, el estado cambio.
2. Antes de "resolver" algo que ya se intento antes, revisa el changelog en `src/flujo/version.py` (`get_changelog()`) o los docs relacionados para ver que ya se probo y fallo, en vez de partir de cero cada sesion.
3. No reescribas `src/flujo/resolume/automator.py` (`build_chataigne_noisette_experimental`) adivinando el schema `.noisette` otra vez. Ya se reescribio 4 veces seguidas (v0.48.2 a v0.48.5), cada vez especulando sobre la estructura interna, y sigue marcado `experimental` porque nunca se valido contra un archivo real. Antes de tocarlo de nuevo: pide al usuario un `.noisette` real exportado desde su Chataigne 1.10.3 y guardalo como fixture en `tests/` -- no vuelvas a adivinar.

## Airdrop obligatorio para agentes sin push

El ZIP debe contener una carpeta `_airdrop/` en la raiz del ZIP.

Correcto:

```txt
_airdrop/HANDOFF_2026-06-30_nombre.md
_airdrop/context/LAST_HANDOFF.md
_airdrop/src/flujo/modulo.py
_airdrop/tests/test_modulo.py
```

Incorrecto:

```txt
airdrop/
_airdrop/_airdrop/
v0.48/_airdrop/
src/flujo/modulo.py suelto fuera de _airdrop
```

Todo airdrop debe incluir:

```txt
HANDOFF_*.md o HOTFIX_*.md
context/LAST_HANDOFF.md actualizado
archivos reales en rutas finales del repo
reporte de verificacion
```

Validacion en Windows/Git Bash:

```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "mensaje corto"
```

Si el runner aplico cambios pero fallo despues:

```bash
py scripts/run_airdrop_checks.py --resume "mensaje corto"
```

Si toca `src/flujo/airdrop.py`, requiere autorizacion explicita:

```bash
py scripts/validate_airdrop.py --allow-airdrop-engine
py scripts/run_airdrop_checks.py "mensaje corto" --allow-airdrop-engine
```

## Verificacion minima

Si tocas Python:

```bash
py -m compileall src/flujo
py -m pytest tests/ -q
py -m flujo verify
```

Si tocas web:

```bash
cd web
npm run typecheck
npm run build:context
cd ..
```

Si tocas airdrop:

```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "mensaje corto"
```

No declares OK si no corriste la verificacion correspondiente. Si algo falla, reporta el error real.

## Limpieza del repo

Permitido limpiar localmente:

```bash
rm -rf _airdrop
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
rm -rf .pytest_cache
rm -rf _logs
```

No incluir en commits ni airdrops:

```txt
__pycache__/
.pytest_cache/
node_modules/
dist/
build/
_airdrop/
_airdrop_backups/
_logs/
*.zip
*.db
archivos pesados reales
credenciales
```

Historico y documentos operativos se archivan, no se borran a ciegas.

## Areas operativas

### Core Python

```txt
src/flujo/
scripts/
tests/
pyproject.toml
```

Entrada diaria:

```bash
py -m flujo app
py -m flujo verify
```

### Web React/Vite

```txt
web/src/
context/flujo_hub.html
context/plano_demo.html
context/svg_visualizer.html
```

Build:

```bash
cd web
npm run build:context
cd ..
```

### RD / Suplementos

```txt
py -m flujo suplementos list
py -m flujo suplementos validate svg/suplementos_rd/04_contraportadas/generadas/*.svg
py -m flujo brief paquete-cotizacion jobs/<job>
```

### Studio / Eventos

```txt
py -m flujo eventos flyer-auto "https://www.instagram.com/p/XXXX/"
py -m flujo resolume automatizar jobs/<job_id>
```

Para Instagram usar `instaloader`. No usar `yt-dlp`.

## Entrega final obligatoria

Toda entrega de agente debe incluir:

1. Archivos modificados.
2. Problema resuelto.
3. Comandos de uso con `py`.
4. Riesgos o pendientes reales.
5. Reporte Formal de Verificacion y Tolerancia Cero a Errores.

Formato del reporte:

```txt
Reporte Formal de Verificacion y Tolerancia Cero a Errores
- py -m compileall src/flujo: OK/FALLO/no aplica
- py -m pytest tests/ -q: OK/FALLO/no aplica
- cd web && npm run build:context: OK/FALLO/no aplica
- py -m flujo verify: OK/FALLO/no aplica
- Observaciones: ...
```
