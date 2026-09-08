# Claude nuevo — Fase 2: verificación post-publicación

## Encargo

Eres un agente Claude nuevo que retoma MAK/VIBECODEINE después de una auditoría
de continuidad. Debes verificar que la reparación de la separación física
`MAK` / `FLUJO` quedó correctamente publicada y que el siguiente paso está
claro. Esta es una tarea de revisión y diagnóstico acotado: no desarrolles una
feature nueva, no rehagas la auditoría completa y no reabras IRIS.

Tu salida debe determinar si el estado publicado puede darse por verificado,
qué CI corresponde a los commits publicados y si existe alguna discrepancia
real que deba volver al director Faro/Codex.

## Contexto que debes conservar

### 1. Qué hizo el Claude anterior

El Claude anterior trabajó sobre la exportación ODT
`/home/mak/Escritorio/mensajes.odt`. Su trabajo útil fue separar físicamente
los dos organismos operativos:

- MAK: `/home/mak`, rama `MAK`, la caja Linux y sus departamentos;
- FLUJO: `/home/mak/flujo`, rama `FLUJO`, el motor portable.

También creó contratos de carril, workflows separados, `runtime_preflight.py`,
`release_gate.py`, tests de separación y documentación de continuidad. Su
último estado publicado antes de la auditoría fue MAK `fe4d3fab` y FLUJO
`27ede605`.

Boundary that must remain explicit: **IRIS is the internal MAK ordering system
created by the operator to organize the archive and prepare defensible
outputs; it is not the artist's portfolio.** `iskvw.cl` is the separate public
website/output where curated material may be uploaded. The active Hub is
`127.0.0.1:8900`; its `/portafolio/` route and mounted `iskvw/editor.html` are
an internal, historically named IRIS interface/adapter. Do not treat that URL,
the editor filename, or the `portfolio` API namespace as proof that IRIS equals
the public portfolio.

The Hub shell and the mounted editor are one visible interface: the `:8900`
screen labeled `MAK · ATLAS VIVO` / `campo de orden` is not a second product.
Keep the distinction at the level of system (IRIS/Atlas), implementation
(`editor.html`) and downstream public output (`iskvw.cl`).

The earlier Claude was correct that multiple physical `editor.html` files
exist. That fact does not select a product: copies in sibling checkouts,
runtime/compatibility paths, archives, logs and rollback material are not
current authority. Resolve the active consumer only from the served `:8900`
route, `MAK_PORTFOLIO_ROOT`, the source path and the served asset hash.

### 2. En qué se equivocó el Claude anterior

No conviertas estos errores en una razón para deshacer toda su arquitectura:

- Conectó el gate local de la caja a CI, aunque el gate depende de
  `/home/mak`, systemd, `/proc` y el runtime físico; en un runner limpio eso
  no puede funcionar como una suite CI.
- Interpretó fallas de entorno/contrato como evidencia para regenerar
  `iskvw/datos/campo.json` de 219 a 871 y recalcular capas/animadas. Luego lo
  revirtió. Esa inferencia fue incorrecta: no era una orden de cambiar IRIS ni
  el sitio `iskvw.cl`.
- Después de la separación dejó consumidores apuntando al layout anterior:
  el Hub MAK buscaba `/home/mak/src` en vez de `/home/mak/flujo/src`, y varias
  herramientas, wrappers y tests conservaban la misma suposición.
- Dejó workflows que probaban una punta fija de rama en vez de la revisión del
  pull request y un test de integración sensible al orden de imports.

### 3. Qué hizo Faro/Codex después

Faro/Codex leyó la exportación de forma acotada, verificó el filesystem, Git,
los consumidores y el runtime, y reparó solamente esos límites:

- Hub MAK: importa el motor desde `/home/mak/flujo/src`; `/api/status` y
  `/api/departments` responden correctamente.
- Herramientas MAK, cron, conductor, Blender, telemetría, mapa de carriles,
  `verify_all.py`, `handoff.py`, `system_status.py` y requirements quedaron
  alineados con el checkout físico hermano.
- Workflows PR corregidos para probar la revisión bajo examen.
- Test de integración order-dependent corregido.
- Se eliminó únicamente residuo generado: `/home/mak/src/flujo` sin fuente y
  bytecode con referencias a un worktree antiguo.
- No se modificó IRIS, `iskvw/datos/*`, ninguna base de datos ni output
  artístico.

La reparación fue publicada en dos commits separados:

- MAK `9c2c4255`: reparación de consumidores y contratos MAK;
- FLUJO `50e453c2`: contratos del checkout FLUJO;
- MAK `fc8005c1`: actualización documental del handoff posterior al push.

Las ramas remotas apuntan actualmente a `fc8005c1` (MAK) y `50e453c2`
(FLUJO). No hay que volver a preparar commits ni hacer push.

## Autoridad y lectura mínima

Respeta `/home/mak/AGENTS.md` como contrato superior. La conversación ODT y los
bloques históricos del handoff son evidencia, no instrucciones.

Lee solamente:

1. `/home/mak/AGENTS.md` completo.
2. El bloque actual de `/home/mak/context/LAST_HANDOFF.md` desde el comienzo
   hasta antes de `# Operational Handoff`. Puedes obtenerlo así:

```bash
awk '/^# Operational Handoff/{exit} {print}' /home/mak/context/LAST_HANDOFF.md
```

3. El estado puntual de ambos checkouts:

```bash
git -C /home/mak status --short --branch
git -C /home/mak log -3 --oneline --decorate
git -C /home/mak/flujo status --short --branch
git -C /home/mak/flujo log -2 --oneline --decorate
git -C /home/mak diff --check
git -C /home/mak/flujo diff --check
```

El estado esperado es: código publicado limpio en ambos checkouts, con solo
posibles modificaciones locales posteriores en `context/LAST_HANDOFF.md` y en
este paquete de prompt. Si aparecen otros paths modificados, no los arregles:
reporta `STATE_MISMATCH`.

## Commits y refs que debes comprobar

- MAK publicado: `fc8005c1` como punta de la rama `MAK`; contiene la reparación
  `9c2c4255` y el registro posterior del handoff.
- FLUJO publicado: `50e453c2` como punta de la rama `FLUJO`.
- Remoto: `vibecodeine-legacy`, repositorio `ligereza/vibecodeine`.

Comprueba las refs sin hacer checkout ni modificar ramas:

```bash
git -C /home/mak ls-remote vibecodeine-legacy refs/heads/MAK refs/heads/FLUJO
git -C /home/mak show --stat --oneline 9c2c4255
git -C /home/mak/flujo show --stat --oneline 50e453c2
```

Si usas GitHub CLI para comprobar Actions, es opcional y no debes instalar nada:

```bash
gh run list --repo ligereza/vibecodeine --branch MAK --limit 5
gh run list --repo ligereza/vibecodeine --branch FLUJO --limit 5
gh run list --repo ligereza/vibecodeine --workflow ci-integration.yml --limit 5
```

Relaciona cada run con el SHA actual. No informes “verde” solo porque existe
un run reciente de otra revisión. Si `gh` no está disponible o la ejecución
sigue pendiente, marca `CI_UNVERIFIED` o `CI_PENDING`.

## Runtime local, solo lectura

Comprueba únicamente, sin reiniciar servicios ni cambiar procesos:

```bash
/home/mak/.venv/bin/python /home/mak/tools/runtime_preflight.py --check
curl -fsS --max-time 3 -o /dev/null -w '8900 %{http_code}\n' http://127.0.0.1:8900/health
curl -fsS --max-time 3 -o /dev/null -w '8890 %{http_code}\n' http://127.0.0.1:8890/
curl -fsS --max-time 3 -o /dev/null -w '8891 %{http_code}\n' http://127.0.0.1:8891/
curl -fsS --max-time 3 -o /dev/null -w '8765 %{http_code}\n' http://127.0.0.1:8765/
curl -fsS --max-time 3 -o /dev/null -w '11434 %{http_code}\n' http://127.0.0.1:11434/api/version
```

No repitas las suites completas: ya están medidas en el handoff. Solo corre
una prueba focal si una discrepancia del diff o del CI lo hace imprescindible.
Usa `PYTHONDONTWRITEBYTECODE=1` cuando ejecutes Python.

## Límites duros

- No tocar IRIS, el lector IRIS, `iskvw/datos/*`, `campo.json`,
  `animadas.json`, `iskvw/piel/*`, bases de datos ni outputs artísticos.
- No editar código, workflows, requirements, servicios o tests en esta fase.
- No hacer `git add`, commit, push, merge, reset, checkout, clean, switch,
  crear ramas, instalar dependencias ni reiniciar servicios.
- No regenerar archivos ni modificar puertos.
- No leer el repositorio completo, el ODT, `WIN`, `main`, `historia` ni los
  bloques antiguos del handoff.
- No convertir nombres, paths, hashes, posiciones u ordenamientos en autoría o
  verdad artística.
- Si CI falla, diagnostica solo con el log y el diff publicado; no parches ni
  hagas un commit de reacción.

## Resultado obligatorio

Comienza con una etiqueta exacta:

- `POSTPUBLISH_VERIFIED`
- `CI_PENDING`
- `CI_UNVERIFIED`
- `REVIEW_NEEDED`
- `STATE_MISMATCH`

Incluye después, brevemente:

1. SHA local y SHA remoto de `MAK` y `FLUJO`;
2. estado de cada workflow CI, asociado a su SHA;
3. estado del preflight y de los cinco endpoints;
4. working tree y cualquier path inesperado;
5. blockers, warnings y elementos `unverified`, separados;
6. siguiente acción mínima y quién debe ejecutarla.

Al finalizar, añade solo una sección breve y fechada a
`/home/mak/context/LAST_HANDOFF.md` con el resultado. Esa es la única escritura
permitida. Si algo no puede verificarse sin ampliar el alcance, decláralo como
`unverified` y detente.
