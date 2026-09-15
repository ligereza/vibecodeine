# ORDEN NOCTURNA PARA MAK: REPOS, RAMAS Y LOOP DE CONSOLIDACION

Esta orden esta escrita para un agente nuevo que comienza directamente en MAK. La autoridad es el estado que exista en MAK al iniciar. Windows y cualquier copia externa son auxiliares y no pueden ser requisito para continuar.

## Objetivo

Comprender y consolidar los frentes de VIBECODEINE sin convertirlos en una sola aplicacion. Cada repo mantiene su identidad. La consolidacion ocurre cuando un productor de un frente entrega un artefacto que un consumidor de otro frente puede usar mediante un contrato, un adaptador, un replay o una salida visible.

La relacion de trabajo es:

`captura/evento -> observacion -> interpretacion o medicion -> propuesta -> representacion -> evaluacion`

Los nombres concretos son:

`XIO/VJ -> FLUJO/MAK -> VIZZ/PUPILA/LUCIDA -> WACHUMA/IRIS -> KINO/MAT-SI`

FARMAKSIA conserva los experimentos y la falsacion. bucle aporta material visual. El motor comun vive en los contratos y adaptadores, no en fusionar todos los repositorios.

No crees otra app central, otro sistema de preguntas, otra cola de informes ni otra capa de memoria para sustituir las que ya existan.

## Regla de autoridad: primero MAK

No presupongas que una ruta existe porque aparece en este documento. Antes de leerla, comprueba en MAK:

```bash
test -e <ruta> && echo EXISTS || echo MISSING
git -C <repo> show-ref --verify --quiet refs/heads/<rama> && echo LOCAL || echo NO_LOCAL
git -C <repo> ls-remote --exit-code <remoto> refs/heads/<rama>
```

Si un archivo o rama falta, no lo reconstruyas desde Windows ni lo reemplaces por una copia parecida. Busca el archivo equivalente dentro de la rama real que si exista. Si no existe, registra la ausencia en el estado interno y continua.

Los documentos, ramas y estados de Windows no son autoridad. Si una entrega de Windows es util, debe estar copiada dentro de MAK y tener una referencia verificable; de lo contrario no se consume.

## Repositorios canonicos de usuario en MAK

Aparte de VIBECODEINE hay **10 checkouts canónicos de proyecto y un núcleo
integrado de evaluación**:

| Repo | Ruta en MAK | Idea que representa |
|---|---|---|
| XIO | `/home/mak/XIO` | Runtime movil de terreno; RD y FOH como dialectos de captura, medicion y operacion. |
| FARMAKSIA | `/home/mak/FARMAKSIA` | Laboratorio de representacion, analogia, invariantes y falsacion. XANAX vive como linea experimental, no como repo separado. |
| VIZZ | `/home/mak/VIZZ` | Geometria, rayos, triangulacion, calibracion y rechazo de mediciones sin evidencia suficiente. |
| PUPILA | `/home/mak/PUPILA` | Asociacion de intencion, accion, modalidad y capacidad. |
| LUCIDA | `/home/mak/LUCIDA` | Motor host-neutral de eventos, reducer, propuestas y adaptadores para interfaces como Adobe o Resolume. |
| IRIS | `/home/mak/IRIS` | Portafolio, relaciones entre obra, artista, espacio y evidencia. |
| WACHUMA | `/home/mak/WACHUMA` | Cultura, material, SVG, malla, GLB, escenas y procedencia. |
| MOSAIK | `/home/mak/mosaik` | Repositorio de show input, capacidades VJ, replay, puentes de plugins y propuestas de ejecucion. |
| KINO | integrado en `/home/mak/MAT-SI/src/matsi/kino/` | Núcleo integrado de evaluación temporal, cache prequential y control de fuga de información; no es un checkout activo separado. |
| MAT-SI | `/home/mak/Escritorio/MAT-SI` | Evidencia, falsacion, orden, transferencia y replay de sesiones. |
| bucle | `/home/mak/bucle` | Material grafico y visual; consumidor potencial de SVG. |

`/home/mak/flujo` es otro checkout/superficie del mismo repositorio VIBECODEINE, no un duodecimo proyecto. `XIO-IMPORT`, `XIO - copia` y la superficie historica de curatoria son duplicados o archivos de importacion. `ml-mobileclip`, `mwb-linux` y Zorin son soporte externo. No los conviertas en frentes del loop.

## Archivos minimos para comprender VIBECODEINE

Trabaja en `/home/mak`, remoto `vibecodeine-legacy`, repositorio `ligereza/vibecodeine.git`.

Lee primero, comprobando cada ruta:

- `git show main:README.md` si el README no esta en el worktree.
- `pyproject.toml`, `NEXT.md`, `CAPACIDADES_MAK.md`.
- `docs/MAK_SYSTEM_DIRECTIVE.md`.
- `docs/GRAMMAR_RUNNER.md`.
- `src/flujo/knowledge/source_learning.py`, `product_learning.py`, `deep_learning_gate.py` y `episode_runner.py`, solo si existen.
- `work/grammar-runs/first-run/index.html`, `library.json` y `checkpoint.json` como artefacto del primer motor grafico.

Despues contrasta `/home/mak/flujo` en la rama `integration/flujo-canonical-20260911` y los archivos equivalentes que realmente existan. El motor comun de VIBECODEINE debe conservar la diferencia entre memoria, episodio, propuesta, representacion y salida.

Ramas locales observadas en el root y no publicadas con el mismo nombre al medir MAK: `archive/main-pre-integrated-20260910`, `codex/main-union-current`, `worktree-actualizar-fechas-convocatorias`, `worktree-fix-agents-md-pointers`, `worktree-hub-portafolio-trim`, `worktree-main-union-mak-flujo`, `worktree-port-ciclo02-test`, `worktree-port-director-skills`, `worktree-revision-branches-huerfanas` y `worktree-xio-live-performance`. Son superficies de recuperacion; no son automaticamente mejores que `main`.

## Archivos minimos por repo

En cada repo lee la rama activa, luego la rama conceptual siguiente indicada en el loop. Lee estos archivos solo si existen; las rutas son guias de seleccion comprobadas en MAK, no permisos para inventar archivos.

### XIO

Ramas: `integration/xio-field-20260911` -> `codex/xio-transport` -> `codex/xio-interface-layer` -> `codex/xio-lucida-input-contract` -> `codex/xio-import-review` -> `codex/semantic-light-field` remoto -> `main`.

Ramas locales sin equivalente remoto observado: `codex-import` y `fix/tests-and-scope`. Rama remota sin local equivalente: `codex/archive-xio-pre-lucida-extraction`. No crees ramas para reemplazar ninguna.

Archivos:

- `README.md`, `NEXT.md`, `MATERIAL_ORIGEN.md`.
- `projects/rd-field/README.md`, `projects/foh-monitor/README.md`.
- `projects/cultura/MAPA_GENERATIVO.md`.
- `xio/vision/README.md`.
- `projects/foh-monitor/android/app/src/main/java/cl/xio/foh/FohNativeServer.java`, `FohCaptureService.java`, `FohLogStore.java`.
- `xio/new-plugins/showcontrol/cueengine.py` y su prueba.

Busca la relacion `Event/Snapshot/Proposal -> Observation` y el replay. RD y FOH no son dos repositorios nuevos: son contextos de uso del mismo runtime de terreno.

### FARMAKSIA

Ramas: `fix/provenance-integrity` -> `codex/pupila-farmaksia-integration` -> `codex/iris-farmaksia-integration` -> `codex/direct-iris-public-scope-20260907` -> `codex/public-scope` -> `codex/obras-experimental-rehearsal-farmaxia-root` -> `main`.

Archivos:

- `README.md`, `RESEARCH_LOOP.md`.
- `experiments/001-representation-boundary/README.md`.
- `experiments/003-vizz-decision/README.md`.
- `experiments/008-xanax-boundary/README.md`.
- `experiments/017-xanax-analogy-chain/README.md`.
- `experiments/020-vizz-codeine-event-bridge/README.md`.
- `experiments/056-farmaxia-representation-renderer/README.md`.
- `experiments/060-codeine-experience-compiler/README.md`.

Los directorios `experiments/...` son experimentos, no ramas. No fusiones experimentos entre si solo porque comparten nombres.

### VIZZ

Ramas: `fix/readme-honesty` -> `main`.

Archivos: `README.md`, `NEXT.md`, `src/vizz/geometry.py`, `src/vizz/portfolio_context.py`, `tests/test_geometry.py`, `tests/test_portfolio_context.py`.

Busca el contrato que transforma observacion en geometria o rechazo. Una simulacion no se presenta como medicion fisica.

### PUPILA

Ramas: `fix/ambiguity-consistency` -> `main`.

Archivos: `README.md`, `src/pupila/association.py`, `tests/test_association.py`.

Busca el contrato que transforma intencion y capacidad en una propuesta seleccionable para LUCIDA.

### LUCIDA

Ramas locales: `docs/next` -> `codex/lucida-python-engine` -> `codex/adobe-adaptive-composition` -> `RESOLUME` -> `MULTI` -> `main`.

Ramas remotas adicionales verificadas: `ADOBE`, `codex/lucida-resolume-final-merge-gate`, `codex/lucida-resolume-freeze`, `codex/lucida-resolume-overlay`, `codex/lucida-resolume-rc-rehearsal`, `codex/lucida-resolume-runtime` y `codex/lucida-resolume-semantic-light-field`.

Archivos: `README.md`, `NEXT.md`; en `codex/lucida-python-engine`, `lucida/engine/contracts.py`, `lucida/engine/reducer.py`, `lucida/engine/pipeline.py` y sus pruebas. En Adobe/Resolume lee primero README, schemas y adaptador concretos.

`MULTI` solo entra si contiene una diferencia funcional. Si es una copia de XIO, conserva XIO como autoridad y no dupliques el codigo.

### IRIS

Ramas: `postulacion/fondart-regional-2027` -> `docs/next` -> `main`.

Archivos: `README.md`, `NEXT.md`, `postulaciones/fondart-regional-2027/FONDART_2027_IRIS_POSTULACION.md`, `anexos/ANEXO_01_DESCRIPCION_PROPUESTA.md`, `anexos/CHECKLIST_ENVIO.md` y `anexos/README.md`.

Busca el consumidor de relaciones y evidencias que pueda mostrar un resultado, no un nuevo motor de aprendizaje.

### WACHUMA

Ramas: `postulacion/fondart-investigacion-2027` -> `main` -> `fix/enforce-content-schemas` -> `docs/next` -> `worktree-ciclo02-wachuma`.

Archivos: `README.md`, `NEXT.md`, `docs/architecture/ADR-0001-plataforma.md`, `ADR-0002-3d-garden-studio.md`, `ADR-0003-evidence-claims.md`, `ADR-0004-material-derivation.md`, `svg-to-mesh.md`, `procedural-generators.md`, `license-matrix.md`, `packages/scene3d/README.md`, `packages/procgen/README.md`, `apps/api/README.md`, `apps/web/README.md` y `apps/worker/README.md`.

Busca el puente SVG/manifest -> escena o GLB, conservando la procedencia y el caracter hipotetico de una reconstruccion.

### MOSAIK

Rama local: `codex/obras-experimental-rehearsal-mosaik-root`. Su remoto
`origin` apunta a `ligereza/mosaik.git` y ahora publica una rama equivalente,
con el mismo HEAD `1ab2076cbfb6`; el checkout la rastrea mediante
`origin/codex/obras-experimental-rehearsal-mosaik-root`. Existe además el
remoto local `windows-bundle` con refs de transferencia; no es la autoridad
cuando la rama pública está disponible.

Archivos: `README.md`, `README_AGENTES.md`, `adapters/vj/README.md`, `adapters/vj/contracts/show-input.schema.json`, `event.schema.json`, `proposal.schema.json`, `result.schema.json`, `adapters/vj/replay/engine.py`, `semantic_light_field.py`, `show_input.py`, `plugin_bridges.py`, `docs/architecture/arquitectura-mosaik-por-etapas-y-componentes.md`, `docs/decisions/ADR-006-cobertura-de-capacidades-lucida.md`, `ADR-010-semantica-canonica-de-unknown.md` y `ADR-017-replay-de-puentes-de-plugin.md`.

Busca el puente show input/evento -> FLUJO y la propuesta que puede consumir LUCIDA.

### KINO

Rama `main`.

Archivos: `README.md`, `package.json`, `scraper/analysis/prequential_cache.py`, `scraper/analysis/tests/test_prequential_cache.py`, `lib/stats.ts`.

KINO entra despues de una transferencia concreta para evaluar si usa informacion disponible en el momento correcto. No se usa para fabricar otra auditoria.

### MAT-SI

Ramas locales: `main` -> `PREDICAR` -> `attack/reproducible-evidence` -> `research/autonomous-operators-foundation`.

Ramas remotas de research: `research/agent1-continuation`, `research/blind-reuse-discovery`, `research/closure-accessibility`, `research/cross-axis-order`, `research/future-equivalence`, `research/meta-lift`, `research/order-dimensions`, `research/order-width`, `research/quantum-order-stress`.

Archivos: `README.md`, `docs/STATE.md`, `docs/research.md`, `docs/phase3c-semantic-falsification.md`, `docs/phase3d-evidence-discovery.md`, `docs/phase4-cross-domain.md`, `docs/reproducible-evidence.md`, `tests/test_session_replay.py` y solo el manifest de `corpus/` que corresponda a la conexion actual.

Las ramas de research son dialectos de investigacion. No se fusionan por parecido nominal.

### bucle

Rama `main`; remoto `arena/019f7461-bucle`, `arena/019f7491-bucle`, `arena/019f74a1-bucle`.

Lee `README.md` y los SVG que el consumidor concreto vaya a usar. No es el motor central.

## Loop-list: orden de lectura y trabajo

La siguiente lista no es una lista de informes. Es un puntero de superficies. El agente recorre el orden, vuelve al inicio y usa las ramas existentes. En cada superficie completa la primera tarea funcional pendiente de esa rama, pero la lista no inventa tareas si la rama no tiene un consumidor real.

### Ciclo 1: autoridad y transporte

1. VIBECODEINE `main` en `/home/mak`.
2. VIBECODEINE `integration/flujo-canonical-20260911` en `/home/mak/flujo`.
3. VIBECODEINE `MAK`.
4. VIBECODEINE `FLUJO`.
5. XIO `integration/xio-field-20260911`.
6. XIO `codex/xio-transport`.
7. XIO `codex/xio-interface-layer`.
8. XIO `codex/xio-lucida-input-contract`.

### Ciclo 2: show, intencion y asistencia

9. MOSAIK `codex/obras-experimental-rehearsal-mosaik-root`.
10. LUCIDA `docs/next`.
11. LUCIDA `codex/lucida-python-engine`.
12. PUPILA `fix/ambiguity-consistency`.
13. LUCIDA `codex/adobe-adaptive-composition`.
14. LUCIDA `RESOLUME`.
15. FARMAKSIA `codex/pupila-farmaksia-integration`.
16. FARMAKSIA `codex/iris-farmaksia-integration`.

### Ciclo 3: geometria, cultura y presentacion

17. VIZZ `fix/readme-honesty`.
18. FARMAKSIA `fix/provenance-integrity`.
19. WACHUMA `main`.
20. WACHUMA `fix/enforce-content-schemas`.
21. WACHUMA `postulacion/fondart-investigacion-2027`.
22. IRIS `postulacion/fondart-regional-2027`.
23. bucle `main`.

### Ciclo 4: evaluacion y retorno

24. KINO `main`.
25. MAT-SI `main`.
26. MAT-SI `PREDICAR`.
27. MAT-SI `attack/reproducible-evidence`.
28. MAT-SI `research/autonomous-operators-foundation`.
29. FARMAKSIA `experiments/008-xanax-boundary` como directorio dentro de la rama que lo contenga; no es una rama.
30. FARMAKSIA `experiments/017-xanax-analogy-chain` como directorio dentro de la rama que lo contenga; no es una rama.
31. VIBECODEINE `worktree-xio-live-performance`.
32. VIBECODEINE `worktree-ciclo02-obras`.
33. VIBECODEINE `worktree-port-ciclo02-test`.
34. VIBECODEINE `worktree-revision-branches-huerfanas`.
35. VIBECODEINE `main`.

Al regresar al punto 1, consulta solo el estado y los artefactos producidos desde la vuelta anterior. Una superficie sin cambios y sin arista pendiente se salta.

## Regla de consolidacion de ramas

No crear ramas nuevas durante este loop.

Antes de usar una rama:

1. Comprueba que existe localmente o como ref remota en MAK.
2. Comprueba su repo, commit, worktree y cambios sucios.
3. Lee primero su README/estado minimo y luego el diff de la rama conceptual siguiente.
4. Identifica si la diferencia es funcional, un dialecto, un experimento, un checkpoint o historia.

Fusiona una rama extra solo si:

- pertenece al mismo repositorio;
- contiene una capacidad del mismo concepto;
- sus archivos tienen un consumidor real;
- el merge es revisable y la rama destino puede proteger los cambios ajenos;
- el consumidor ejecuta correctamente despues de la fusion.

Mantiene separadas las ramas de Adobe/Resolume, RD/FOH cuando expresen dialectos, los experimentos de FARMAKSIA, las ramas de research de MAT-SI, los checkpoints/worktrees y las historias antiguas. No fusiones por nombre, fecha, cantidad de tests o parecido documental.

No uses `git reset --hard`, `git checkout --`, `git add .` ni force-push. Selecciona archivos concretos. Si el worktree esta sucio, no cambies de rama a ciegas. Si una fusion entra en conflicto y no puede resolverse con claridad, conserva el estado y avanza al siguiente elemento.

## Unidad de avance

Una visita cuenta como avance solamente si deja al menos una de estas cosas:

- un adaptador productor -> consumidor ejecutado;
- una capacidad existente consumida desde otro repo;
- un replay que funciona con una segunda entrada;
- una salida visible SVG, HTML, overlay, GLB u otra representacion navegable;
- una tarea funcional de una rama completada y probada por su consumidor;
- una fusion de codigo que reduce una duplicacion real y deja su consumidor funcionando.

Un informe, un JSON de estado, un hash, una auditoria, un conteo o una prueba verde aislada no son avance suficiente.

## Anti-loop

- No generes Q-IDs ni preguntas sucesoras para mantener actividad.
- No repitas una verificacion que no cambio codigo, entrada, version o dependencia.
- No permanezcas mas de 20 minutos leyendo una superficie sin pasar a una tarea funcional o avanzar al siguiente nodo.
- Dos intentos del mismo bloqueo obligan a cambiar de arista.
- Una vuelta completa sin artefacto nuevo, consumidor nuevo o diff funcional deja el loop en espera.
- No llames a un agente o modelo para inventar la siguiente lista cuando hay una arista pendiente.
- No cierres los frentes. Cierra solo una unidad funcional y vuelve al puntero.

## Estado y autonomia

Conserva un unico estado interno en:

`/home/mak/work/overnight-repos/state.json`

Si no existe, crealo una sola vez. Debe registrar `current_repo`, `current_branch`, `loop_index`, `pending_edges`, `done_edges`, `skipped_edges`, `artifacts`, `last_error` y `next_repo`. No lo conviertas en un informe.

MAK debe poder continuar sin Windows. Cualquier artefacto producido por Windows debe copiarse a MAK por SSH antes de ser usado. El agente puede trabajar con modelos o proveedores disponibles para el entorno actual; no impongas modelos locales de baja calidad como razonadores. Las iteraciones mecanicas deben quedar en codigo local.

Al terminar una unidad funcional, deja un commit selectivo si el worktree y la rama lo permiten. Haz push normal al remoto correcto cuando exista autorizacion y no haya divergencia insegura. Verifica el SHA remoto. Un rechazo de push no debe borrar el commit ni crear una rama sustituta.

Cuando una vuelta termine, vuelve al inicio. Si hay una arista elegible, continua. Si no hay ninguna, espera sin inventar informes ni nuevas preguntas.
