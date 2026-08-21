# Operational Handoff

## Current objective

Mantener el repo web y el runtime local en un estado coherente y verificable,
con una primera capa artistica-cultural-investigativa comun para curatoria,
portfolio, research y matematicas. La hipotesis P versus NP se usa aqui como
modelo conceptual de representacion, busqueda y certificados; no como un
teorema ya demostrado.
El estado operacional ya no depende de releer este archivo: se consulta en la
CLI y en el Hub real de 8900 mediante `mak-system-status-v1`, que reúne el
ledger con los consumidores locales y deja las atenciones explícitas. Los
gates de esta tanda quedaron cerrados: se preserva la incertidumbre
matematica y Research 4 tiene un consumidor local simbólico, con licencia y
revisión humana aún pendientes. La continuidad de ideas se consulta en el lane
registry, no releyendo la memoria historica completa.

## Session transfer checkpoint — 2026-08-21

La fase web/DB queda validada y lista para publicar. El conjunto propio de esta
fase es la limpieza de superficies Windows obsoletas, la preservacion de XIO
como workflow manual diferido, el gate `tools/repo_audit.py`, su regresion,
`tools/gen_rd_standalone.py`, la fila de `CAPACIDADES.md`, los cambios de CI/
Makefile y este handoff. No se debe hacer `git add .`: el worktree contiene
otros cambios de sesiones anteriores que deben permanecer intactos y sin
mezclarse.

Pruebas cerradas: pytest completo exit 0; `npm run typecheck` exit 0;
`repo_audit` exit 0 (36 modulos, 35 alcanzables, 0 muertos, 0 referencias
obsoletas, cuatro SQLite integras); compileall y `git diff --check` exit 0.
No hay procesos de pytest, intake, Blender ni render activos. La siguiente
accion exacta es revisar el staging del conjunto propio, crear el commit y
hacer push de `main`; despues la nueva sesion debe continuar desde `Next
concrete action` sin repetir la auditoria.

CERRADO: ese checkpoint se completo en `69e7fba` + `268ef4b` y el resto del
worktree se publico en `90f92be`. Se conserva como registro; la accion vigente
esta en `Next concrete action`.

## Physical authority and migration status

- La autoridad física es `/home/mak/*`; `/home/mak/flujo` es el baseline de
  autoría y `/home/mak/WIN` es evidencia histórica de Windows.
- No se copia ni se borra el árbol histórico. Los datos locales ignorados y los
  productos generados se preservan fuera del commit salvo que una regla del
  repo los declare artefactos versionables.
- Git tiene una sola rama local (`main`) y una sola rama remota operativa
  (`origin/main`). El README y su SVG protegido no se modifican.
- En la inspección actual se observaron `cron`, el runner local de GitHub
  Actions y Open WebUI ya instalados; esta tarea no inició ninguno. El Hub
  existente `mak-hub.service` fue reiniciado de forma controlada para activar
  la nueva ruta read-only y quedó activo en 8900; no se inició ningún servicio
  nuevo ni se dejó un render adicional.
- La interfaz temporal del Research local ya estaba activa antes de esta
  tanda; no fue iniciada, detenida ni modificada aquí.

## Completed work with command and result

- Se agregó `src/flujo/knowledge/learning_policy.py`: learner categórico
  auditable, split por `project_id`, abstención ante evidencia insuficiente y
  registro de política solo como candidata.
- Se agregó `tools/project_learning.py` y
  `tests/test_learning_policy.py`. El adaptador
  `mak-verified-result-v1` exige proyecto existente, evidencia, validador y
  checks pasados; es idempotente y falla cerrado.
- `src/flujo/knowledge/project_api.py` expone `learning.policy` en modo
  read-only. `CAPACIDADES.md` y `docs/MAK_CURRENT_STATE.md` declaran el
  contrato.
- Se integró `operational_status()` en
  `src/flujo/knowledge/project_api.py`, `tools/mak_status.py` y el campo
  `operational` de `GET /api/status`. CLI y Hub comparten el mismo contrato
  read-only: estado general, evidencia pendiente, bloqueos, abstenciones y
  siguientes acciones. El Hub conserva sus campos históricos de servicio.
- Se agregó `src/flujo/knowledge/system_status.py`, el sobre
  `mak-system-status-v1` que conecta el ledger con once consumidores físicos:
  fuente/Hub 8900, Research 8890, Codex 8891, SearXNG 8888, runner de eventos,
  Blender/RD, portafolio, runtimes, configuración de proveedores y el registro
  transversal de lanes. Solo lee
  rutas, `/proc`, listeners loopback y nombres de variables; no hace requests
  externos, no inicia jobs y nunca devuelve valores de claves.
- El Hub canónico `/home/mak/plataforma/hub.py` ahora expone
  `GET /api/status` y una pestaña `● estado` en 8900. El endpoint real fue
  verificado con HTTP 200, esquema `mak-system-status-v1`, once componentes y
  `read_only=true` después del reinicio controlado.
- El componente `lanes` del mismo sobre valida, sin mutar, el registro
  `mak-cross-domain-lane-registry-v1`: 19 lanes bajo
  `cultural_research_first` (1 implementada, 7 parciales, 11 propuestas).
  El CLI y el estado del Hub comparten ahora el módulo
  `src/flujo/knowledge/lane_registry.py`.
- Se agregó `runtime_tools.resolve_blender()`: resuelve la instalación real
  `/home/mak/blender/blender` aunque no esté en `PATH`. `contract_registry` y
  `episode_runner` comparten esa resolución, eliminando el falso faltante de
  `blender_optional` sin instalar ni ejecutar Blender desde el estado.
- El probe de render cuenta procesos por el ejecutable real de `/proc`, no por
  texto de argumentos: una orden de inventario que mencionaba la ruta de
  Blender había producido un falso `active`. La lectura final muestra
  `render=ready` y `process.running=false`; no hay render en segundo plano.
- La auditoría de contratos más reciente se registró explícitamente como
  `simulation_consumer_20260820`: 59 contratos, 59 verificados, 0 con
  evidencia pendiente y 0 no disponibles. El ledger actual queda con 2
  atenciones accionables (4 proyectos en revisión y 3 episodios sin evidencia)
  y 2 informativas (abstención segura y falta de holdout independiente).
- `tools/source_learning_bridge.py` y
  `src/flujo/knowledge/source_learning.py` conectan dos raices fisicas por
  referencias: `/home/mak/WIN/claude_sesiones` como memoria de hipotesis y
  `/home/mak/curatoria_inbox/MAK_TODO_SESION_2026-08-19` como auditoria y
  contratos de investigacion. El caso versionado valida 2 raices, 9 archivos,
  9 mensajes por UUID/hash, 7 hallazgos y 5 unidades de aprendizaje sin copiar
  los arboles ni el texto privado de las conversaciones.
- La ingestion real se registro como proyecto activo
  `mak-pnp-search-ecology-2026-08-19` y episodio verificado
  `episode-source-learning-c6f328491b44e1af7828ec1b`. El alcance guardado es
  `source_integrity_and_epistemic_contract_only` y
  `mathematical_truth_validated=false`: no afirma una solucion de P versus NP.
- `src/flujo/knowledge/math_kernel.py` agrega un scheduler metadata-only sobre
  el mismo Project IR y la misma base SQLite: una capsula `MILLENNIUM-PNP-001`,
  requests acotados y ResultCards sellados. El proyecto conserva los dominios
  `cultura`, `curatoria`, `portfolio`, `research` y `mathematics`; como la
  fidelidad semantica esta `UNTRUSTED`, su estado es `review_required` y el
  ciclo real solo dejo una request `METADATA_ONLY` en cola. No se ejecuta un
  worker ni se promueve verdad por ausencia de contraejemplos.
- `knowledge/lane_registry/mak_cross_domain_registry_2026-08-20.json` y
  `tools/project_lanes.py` agregan un mapa read-only de 19 lineas bajo la misma
  primera capa: P=NP, tenis, captura/scraping, deep learning/micelio,
  transpilacion, eventos, simulacion de crecimiento, XIO, claims, lenguas, patentes, crops, dental,
  jardin/geometria, vibe coding, storage, patronage y autoria. Cada linea
  conserva dialectos, estado epistemico, evidencia, consumidor si existe,
  guardrails y un siguiente gate; las propuestas no se presentan como trabajo
  implementado.
- El lane de tenis ya tiene `src/flujo/tennis/shot_events.py` y el consumidor
  read-only `tools/tennis_shot_events.py`: proyectan a
  `schemas/tennis/shot_event.schema.json`, conservan `raw_ref`, hash,
  `transform_chain` y tokens desconocidos, y el router solo lo selecciona para
  un Project IR activo/verified del dominio `tennis`.
- Se registró el primer episodio verificable del lane: proyecto
  `mak-tennis-decision-lab-fixture-20260820`, episodio
  `episode-tennis-shot-fixture-20260820`, 4 eventos, hash de fixture y 2
  tokens desconocidos preservados; `network_calls=0` y sin contrafactuales.
- El probe de ruta del mismo proyecto selecciona
  `tennis_shot_event_consumer` y queda registrado como
  `episode-tennis-consumer-probe-20260820`; prepara un comando local acotado,
  no lo ejecuta ni escribe salida generada.
- Scraping y deep learning ya tienen consumidores acotados: `research_source_capture.py`
  separa plan/captura y registra una sola URL con hash en `SourceCorpusStore`;
  `deep_learning_gate.py` exige labels, holdout independiente, agrupación
  anti-leakage y validador, pero nunca autoriza entrenamiento por sí solo.
- La evidencia física de Research 4 quedó enlazada al Project IR como proyecto
  `mak-research-capture-job4-20260820` y episodio
  `episode-research-capture-job4-20260820`: 4 fuentes capturadas, hashes y
  etapas verificadas; licencia pendiente; el consumidor simbólico queda sujeto
  a revisión humana y no afirma crecimiento biológico.
- Research 4 ya tiene un consumidor `research_simulation_consumer`:
  `knowledge/research_simulations/job4_lsystem_candidate_20260820.json` usa
  reglas explícitas, límite de símbolos y alcance `visual_grammar`; la salida
  se etiqueta `simulated`/`model_not_reality` y no se interpreta como biología.
- El dataset existente de logo-clean quedó enlazado como
  `mak-logo-clean-learning-gate-20260820`; su episodio
  `episode-deep-learning-gate-logo-clean-20260820` abstiene correctamente:
  solo hay 3 ejemplos y no existe holdout independiente, por lo que no se
  autoriza entrenamiento.
- `tests/test_system_status.py` cubre resolución local, redacción de secretos
  y ausencia de escrituras. El cambio de `providers.provider_registry()` hace
  que un entorno explícito no cargue silenciosamente otro `.env`.
- `web/src/components/HubDashboard.tsx` muestra el estado unificado antes del
  ledger, y `web/src/api/flujoApi.ts` consume `/api/status` como fuente única;
  las páginas generadas de `context/` fueron reconstruidas con Node 24.19.0.
- La consulta actual del ledger devuelve `attention` con 2 asuntos accionables
  y 2 informativos: cuatro proyectos en revisión, tres episodios sin evidencia,
  abstención segura y falta de holdout independiente. Los 59 contratos,
  incluido Blender y el puente de memoria, quedaron verificados.
- Research job 4 sobre `JARDINES_INTERPRETATIVOS.md` capturó cuatro fuentes,
  extrajo claims, relaciones, contexto e interpretación y dejó el siguiente
  paso en `simulate`; el runner histórico no tenía una función ejecutable para
  ese paso (`interpretive_simulation_callables=[]`,
  `research_router_simulation_callables=[]`), pero ahora existe el consumidor
  local simbólico `research_simulation_consumer`; el resultado permanece
  marcado como modelo y no como hecho. No se clonaron ni instalaron repos
  candidatos; la licencia y la revisión humana siguen pendientes.
- La revision de procedencia P versus NP incorporó
  `knowledge/math_targets/p_vs_np_official_statement_capture_2026-08-20.json`,
  con la pagina oficial de Clay, hash de la nota canonica y estado `Unsolved`.
  El artefacto formal local tiene hash completo y ambos hashes se guardan en la
  capsula; la fidelidad semantica permanece `UNTRUSTED` y el kernel sigue
  bloqueando cualquier promocion de verdad.
- La base local ignorada `data/mak_knowledge.db` contiene ocho episodios
  elegibles en cuatro proyectos; incluye el fixture verificado, el probe del
  consumidor de tenis. La política medida es `abstain` con razón
  `no_independent_holdout`, `eligible_examples=8`, `train_count=8` y
  `holdout_count=0`. No se promovió ninguna regla.
- La contradicción detectada en el handoff fue eliminada: ya no se escribe un
  total fijo de tests ni se recicla el conteo antiguo del learner.
- Se declaró en `web/package.json`, `web/package-lock.json` y
  `web/README.md` el requisito real `Node >=20.19.0`; con el Node 24.19.0
  disponible en MAK los builds reproducibles pasan.
- Los cambios de esta tanda se publicaron en `main` mediante el commit
  `7674c49` y el push normal a `origin/main`; la evidencia generada dentro de
  `data/mak_knowledge.db` sigue siendo estado local ignorado. La
  evidencia generada dentro de `data/mak_knowledge.db` es estado local
  ignorado; los writes explícitos fueron el refresh de contratos y la
  ingestion verificada del caso de memoria descrito arriba.
- Se retiraron Watsonx, AWS y Azure de la superficie operativa activa. Se eliminaron
  sus adaptadores, alias, capacidades, rutas de fallback, opciones CLI, UI y
  políticas de proveedores en `cultura/mak_plataforma/providers.py`,
  `cultura/mak_research/research_lib.py`, `research.py`, `refutar.py`,
  `cultura/mak_codex/codex_lib.py`, `cultura/mak_plataforma/hub.py`,
  `iskvw/editor.html`, `src/flujo/autonomia.py` y `src/flujo/cli.py`.
  Research queda con Groq -> Gemini -> Ollama; Cerebras permanece solo como
  opcion explicita porque el probe real devuelve HTTP 402. Codex conserva
  NVIDIA NIM -> Ollama; vision del portafolio queda local con el lector
  Ollama existente.
- Las herramientas Watson exclusivas se movieron, sin borrarlas, a
  `/home/mak/_archive/watsonx-retired-20260820/`: cuatro sondas/benchmarks y
  copias protegidas de `n8n-local/research.env` y `research/research.env` antes
  de retirar sus líneas Watson/AWS. No se tocaron `/home/mak/WIN`, ledgers,
  productos ni resultados históricos.
- Se retiró `boto3` de `pyproject.toml` y `requirements.txt`. La matriz y el
  mapa ahora describen los proveedores retirados como evidencia histórica, no
  como capacidad disponible. `python3 -m compileall` terminó con exit 0,
  `./.venv/bin/python -m pytest -q` terminó con exit 0 (warnings existentes de
  Pillow), y `git diff --check` quedó limpio.
- Se verificó el reemplazo de proveedores en el runtime y sus espejos. El
  adaptador Gemini usa `gemini-3.6-flash`, carga solo `GEMINI_API_KEY` y
  `GEMINI_MODEL` desde el `.env` secundario, y devuelve texto y JSON válidos.
  Los probes foreground de Groq, Gemini y Ollama devolvieron texto no vacío;
  Firecrawl capturó `https://example.com` mediante el backend configurado
  (`167` caracteres). El probe explícito de Cerebras devolvió HTTP 402
  `payment_required`, por lo que no participa en la cadena automática.
  Azure no conserva llamadas ni configuración activa; las coincidencias que
  quedan son comentarios, vocabulario de arqueología o resultados históricos.
  La copia vieja de `research_lib.py` y el workflow n8n retirado siguen
  preservados en `/home/mak/_archive/provider-retirement-20260820/`.
- El adaptador estructurado de `cultura/mak_plataforma/providers.py` fue
  endurecido para no truncar JSON cuando el llamador pide un presupuesto muy
  pequeño; su probe Gemini devolvió un objeto JSON válido. La suite completa
  pasó después de actualizar el test que aún esperaba Cerebras al frente de
  la ruta de riesgo alto.
- Se probó la regla arquitectónica "salir del espacio de soluciones" con dos
  fallos reales. Primero, una respuesta Gemini simulada con
  `finishReason=MAX_TOKENS` y sin `content.parts` no obligó a reparar Gemini:
  `LLM.call` la clasificó como vacía y continuó con Ollama (`status=ok`).
  Segundo, Firecrawl capturó la documentación oficial de Gemini con `236737`
  caracteres de navegación y contenido; una selección acotada de ventanas
  relevantes redujo la evidencia a `3119` caracteres y Ollama identificó
  `MAX_TOKENS` y la decisión de rechazar el resultado truncado. La conclusión
  es que la captura funciona y la dependencia que debe cambiar es el paso de
  evidencia-a-análisis, no Firecrawl. Este experimento fue read-only y no
  cambió código ni datos.
- En el primer lote de apuestas predictivas se eligieron dos verificaciones de
  alto aprendizaje y bajo costo. El contrato de proveedores (`PROVIDER_ORDER`,
  `PROVIDER_CAPABILITIES`, `PROVIDER_ENV_KEY` y métodos `LLM._*`) quedó
  consistente (`all_provider_contracts_consistent=true`). La búsqueda de
  interfaces antiguas solo encontró un comentario de endpoint legacy,
  resultados históricos y tres copias bajo `/home/mak/rollback/`; no encontró
  un consumidor activo roto. Ambas predicciones se descartan sin parche.
  El lote confirma que la unidad útil es `prediccion -> prueba barata ->
  descarte o patron`, no volumen de archivos.
- Se compararon los enfoques externo y resiliente. En la ruta externa,
  Firecrawl capturó la página oficial de precios de Cerebras (`4053`
  caracteres; ventana relevante `1424`), pero el resumen Ollama inventó un
  crédito de `$5`; la salida fue rechazada por falta de evidencia. La fuente
  confirma solo tier Free `$0` y límites menores, mientras el probe local real
  sigue en HTTP 402. La conclusión es `captura externa -> evidencia acotada ->
  validación`, nunca `captura -> verdad`.
- En la ruta resiliente se encontró y corrigió un bug real en
  `cultura/mak_plataforma/providers.py`: `TASK_CAPABILITIES["research"]`
  pedía la capacidad inexistente `research`, por lo que el router devolvía
  `local_deterministic` aun con proveedores disponibles. Ahora Research usa
  la capacidad declarada `hypothesis` y enruta `Groq -> Gemini -> Ollama`.
  Se agregó `test_research_route_uses_declared_hypothesis_capability`; el test
  enfocado y la suite completa terminaron con exit 0, y `git diff --check`
  quedó limpio.
- Se inició el experimento dual de depuración sobre Research/proveedores
  reutilizando `src/flujo/diagnostics.py` y el comando `flujo diagnose`, sin
  crear otro framework. Para el agente externo se generaron dos paquetes
  `mak-diagnostic-v1` read-only: ambos rutearon a Research, redacted datos
  sensibles, excluyeron WIN y entregaron contrato, rutas existentes, gate y
  reproducción. El primer postprocesador falló con `python: command not found`;
  al repetirlo con `.venv/bin/python`, el diagnóstico terminó con exit 0.
- El mismo slice para MAK validó `route_task("research")` como
  `hypothesis`, `Groq -> Gemini -> Ollama`, y simuló una respuesta Gemini sin
  `content.parts`: la salida pasó a Ollama sin bloquearse. El paquete Research
  tenía además una ruta inexistente (`src/flujo/research`); se eliminó de
  `src/flujo/diagnostics.py` y `context/diagnostics/domains.json`, y se agregó
  una regresión que exige `missing_read_paths=[]`. Tests enfocados, suite
  completa y compileall terminaron con exit 0; no se inició ningún servicio.
- Se agregó `src/flujo/index/code_index.py` y el comando `flujo code-index`.
  Construye `mak-code-structure-v1` con AST, símbolos, imports, consumidores,
  entradas, efectos y hashes, sin guardar texto fuente. Excluye `WIN`,
  `.agents`, `.codex`, `.claude`, entornos, caches y builds. El índice real
  `context/code_structure_index.json` contiene 781 módulos Python, 8552
  símbolos, 186593 líneas declaradas y cero errores de sintaxis; ocupa
  2671255 bytes. `--query` devuelve un `mak-code-brief-v1` acotado para que
  un agente abra solo candidatos relevantes. Se agregó regresión para
  consumidores relativos y errores de sintaxis aislados, y se sincronizaron
  `MAPA.md`/`context/comandos.json` con el generador oficial.
- El primer push del índice expuso dos fallos de portabilidad en CI: una ruta
  histórica con el usuario Windows real y un test que exigía un artefacto
  formal guardado fuera del clon. Se anonimizó la ruta en
  `context/fases.migracion.md` y `tests/test_math_kernel.py` ahora valida el
  hash si el artefacto externo existe, pero hace `skip` explícito en clones
  limpios. `./.venv/bin/python -m flujo verify` y la privacidad local pasan;
  el commit `6743467` se publicó y CI #22/seguridad de ese SHA terminaron en
  `success`.

## Open integration items

| Item | Path | Status | Proof required |
| --- | --- | --- | --- |
| Python learning layer | `src/flujo/knowledge/learning_policy.py` | verified, published | full pytest exit 0; py_compile exit 0; diff check exit 0 |
| Web source | `web/` | verified, published | Node 24.19.0: `npm ci`, audit 0 vulnerabilities, typecheck and all three builds exit 0 |
| Documentation contract | `CAPACIDADES.md`, `docs/MAK_CURRENT_STATE.md`, this file | verified, published | docs hygiene included in full pytest exit 0 |
| Watson/AWS/Azure retirement and provider replacement | provider registries, research/codex chains, Hub/UI, env files, `pyproject.toml`, `requirements.txt`, `/home/mak/research/` | verified and published in `90f92be`; live runtime reloaded | full pytest exit 0; compileall exit 0; Groq/Gemini/Ollama/Firecrawl probes pass; Cerebras HTTP 402; recoverable archive present; `/api/status` after the Hub restart no longer reports watsonx |
| Operational status | `src/flujo/knowledge/system_status.py`, `cultura/mak_plataforma/hub.py`, `tools/mak_status.py`, `web/` | verified, published in `90f92be` and reloaded at 8900; lane registry included read-only | focused pytest; temporary/live `/api/status` HTTP 200; eleven components; read-only endpoint |
| Python structure index | `src/flujo/index/code_index.py`, `context/code_structure_index.json`, `tests/test_code_index.py` | published in `90f92be`; index regenerated from the published tree (783 modules, 8565 symbols, 0 syntax errors) | focused/full pytest exit 0; CLI probe; zero syntax errors; diff check exit 0 |
| Source learning bridge | `src/flujo/knowledge/source_learning.py`, `tools/source_learning_bridge.py`, `knowledge/learning_cases/`, `schemas/knowledge/source_learning_case.schema.json` | verified locally and recorded; published in `7674c49` | source roots/files/messages/claim boundaries pass; Project IR episode verified; no truth promotion |
| Cultural-first math kernel | `src/flujo/knowledge/math_kernel.py`, `tools/math_kernel.py`, `knowledge/math_targets/`, `schemas/knowledge/math_*.schema.json` | verified locally; one bounded metadata request queued; published in `7674c49` | capsule validation, common Project IR domains, sealed ResultCard guard and truth-promotion block |
| Cross-domain lane registry | `knowledge/lane_registry/`, `tools/project_lanes.py`, `schemas/knowledge/cross_domain_lane_registry.schema.json` | published in `90f92be`; 19 lanes, 3 priority-0 lanes, no new consumer claimed for proposals; `lanes` component ready in the live Hub | registry validation, common first-layer rule, evidence refs, guardrails and next gates |
| Tennis MCP first slice | `src/flujo/tennis/mcp.py`, `tools/tennis_mcp_ingest.py`, `tests/test_tennis_mcp.py` | verified locally; conservative parser and hash-linked JSONL projection; no external acquisition | focused pytest, syntax check, diff check; feeds the shot-event consumer |
| Tennis shot-event consumer | `src/flujo/tennis/shot_events.py`, `tools/tennis_shot_events.py`, `schemas/tennis/shot_event.schema.json` | verified locally; router-selected read-only consumer with explicit uncertainty and provenance; first episode recorded | schema validation, Project IR route test, focused pytest, verified episode; next is an independent second fixture |
| Tennis Project IR probe | `tools/project_gate.py`, `src/flujo/knowledge/episode_runner.py` | verified locally; route selects tennis consumer and probe status is `succeeded` without executing it | read-only project gate, recorded probe episode; next is independent evidence |
| Research source capture | `tools/research_source_capture.py`, `cultura/mak_research/source_pipeline.py` | verified locally; existing Research 4 capture linked, license remains pending, no broad crawl | 4 source hashes, verified capture/extract/interpret results; next is license review |
| Research simulation | `src/flujo/knowledge/research_simulation.py`, `tools/research_simulation.py`, `schemas/knowledge/research_simulation_manifest.schema.json` | verified locally; bounded symbolic trajectory, model-not-reality marker, no external calls | manifest schema, deterministic trajectory, budget abstention and Project IR route; next is human review |
| Deep-learning task gate | `src/flujo/knowledge/deep_learning_gate.py`, `tools/deep_learning_gate.py`, `schemas/knowledge/deep_learning_task_gate.schema.json` | verified locally; logo-clean episode abstains on 3-row/no-holdout evidence, training remains disabled | manifest schema, gate tests, Project IR episode; next is an independent holdout |
| Research learning | `/home/mak/research/jobs/4/` | captured/interpreted; bounded symbolic simulate consumer available; license review pending | review candidate grammar and license; no candidate install |
| Publication | `main` -> `origin/main` | verified at `90f92be`; remote CI green | `git rev-parse HEAD` equals `git ls-remote origin refs/heads/main`; CI, seguridad and Git topology guard all `success` |

## Tool and dependency verification matrix

| Surface | Command | Current result |
| --- | --- | --- |
| Python suite | `./.venv/bin/python -m pytest -q` | exit 0; warnings only from existing Pillow deprecation |
| Learning policy | `./.venv/bin/python tools/project_learning.py --db data/mak_knowledge.db` | exit 0; abstain; 8 eligible in 4 projects; no independent holdout |
| Source learning | `PYTHONPATH=src ./.venv/bin/python tools/source_learning_bridge.py knowledge/learning_cases/mak_pnp_search_ecology_2026-08-19.json --db data/mak_knowledge.db --record` | exit 0; 2 roots, 9 artifacts, 9 messages, 5 learning units; verified ingestion only |
| Python syntax | `./.venv/bin/python -m py_compile ...` | exit 0 |
| Diff hygiene | `git diff --check` | exit 0 after code-index and map synchronization |
| Python structure index | `./.venv/bin/python -m flujo code-index --root . --output context/code_structure_index.json --query "research provider route" --format json` | exit 0; 781 modules, 8552 symbols, 0 syntax errors; source-free index; 20 bounded query matches |
| Python dependencies | `./.venv/bin/python -m pip check` | exit 0; no broken requirements |
| Provider replacement probes | foreground `LLM(groq|gemini|ollama)` + platform `providers.call(gemini, response_format=json)` | exit 0; all text responses non-empty; Gemini structured response parsed as JSON object |
| Firecrawl capture | foreground `capture_url("https://example.com", backend="firecrawl")` | exit 0; backend `firecrawl`; 167 captured characters |
| Cerebras availability | foreground explicit `LLM(cerebras)` probe | expected failure; HTTP 402 `payment_required`; excluded from automatic route |
| Azure runtime audit | `rg` over active provider/runtime surfaces | no active Azure call/configuration; remaining matches are historical/comments/vocabulary |
| Web typecheck/build | `NODE_BIN=.../node ./node_modules/typescript/bin/tsc --noEmit`; `NODE_BIN=.../node ./node_modules/vite/bin/vite.js build`; `NODE_BIN=.../node scripts/copy-context.mjs` | exit 0 with Node 24.19.0; 1840 modules; `dist/index.html` 777.98 kB |
| Math Kernel cycle | `PYTHONPATH=src ./.venv/bin/python tools/math_kernel.py cycle --db data/mak_knowledge.db --target knowledge/math_targets/p_vs_np_target_capsule_2026-08-19.json --iterations 1 --compute-units 1 --max-expanded-cost 100` | exit 0; `mak-math-ledger-v1`; target `UNTRUSTED`; one `METADATA_ONLY` request; truth promotion blocked |
| Lane registry | `PYTHONPATH=src ./.venv/bin/python tools/project_lanes.py validate` | exit 0; `mak-cross-domain-lane-registry-v1`; 19 lanes; common `cultural_research_first` layer; read-only |
| Tennis MCP slice | `PYTHONPATH=src ./.venv/bin/python -m pytest -q tests/test_tennis_mcp.py tests/test_project_lanes.py` | exit 0; parser preserves raw notation, unknown tokens, source hash and `ANNOTATED` status |
| Tennis shot-event route | `PYTHONPATH=src ./.venv/bin/python -m pytest -q tests/test_tennis_mcp.py tests/test_project_router.py tests/test_project_contracts.py` | exit 0; schema-shaped events, unknowns/provenance preserved, Project IR selects `tennis_shot_event_consumer` |
| Scraping/deep-learning/simulation gates | `PYTHONPATH=src ./.venv/bin/python -m pytest -q tests/test_research_source_capture.py tests/test_deep_learning_gate.py tests/test_research_simulation.py` | exit 0; default scraping is plan-only, deep-learning gate abstains without independent holdout, simulation is bounded/model-labelled |
| Unified status CLI | `./.venv/bin/python tools/mak_status.py --db data/mak_knowledge.db --json` | exit 0; `mak-system-status-v1`; 11 components, including valid 19-lane registry; `render=ready`, no Blender process; 2 actionable and 2 informational ledger items; read-only; 59 contracts audited |
| Unified status HTTP | temporary `ThreadingHTTPServer` + live `127.0.0.1:8900` -> `GET /api/status` | HTTP 200 in both; `mak-system-status-v1`; `read_only=true`; temporary server shut down; live Hub active |
| Catalog federation | `src/flujo/knowledge/catalog_federation.py`, `tests/test_catalog_federation.py`, `data/mak_knowledge.db` | verified locally and integrated additively; 7 read-only sources, 124 tables, 2,075,337 observed rows, 0 copied; integrity and FK checks pass |
| Operational DB bridge | `src/flujo/knowledge/operational_bridge.py`, `tests/test_operational_bridge.py`, `data/mak_knowledge.db` | verified locally and refreshed; 6,132 normalized records, 106,895 curation links, exact package/project/fund links; source rows copied 0; integrity and FK checks pass |
| Web/DB audit gate | `tools/repo_audit.py`, `tests/test_repo_audit.py`, `.github/workflows/ci.yml`, `Makefile` | verified locally; 36 web modules, 35 reachable, 0 dead, 0 stale active references; four DBs have resolved consumer paths and integrity `ok`; published in `69e7fba` |
| RD live/standalone projection | `src/flujo/rd/panel.py`, `tools/gen_rd_standalone.py`, `web/src/data/rdDbEmbebida.json` | verified locally; generated and tracked JSON are equal (6 records, identical SHA-256); generator now accepts absolute output paths |
| SSD application intake | `tools/build_application_intake.py`, `/home/mak/labs/portable-ssd-index-20260813/archivo_index.sqlite` | verified in `/tmp`; 917 projects scanned, 3 bounded Fondart packages emitted, derived SQLite integrity `ok`; status remains `draft_with_evidence_gaps` |
| DB -> Research -> Curatoria -> Postulacion | temporary foreground pipeline using existing Research corpus, Curatoria diagnostic and `tools/build_application_intake.py` | exit 0; Research 5,179 applications/14 captures; Curatoria 917 projects/13,121 families/45,536 members; Postulacion emitted `drefgira-fondart` with explicit evidence gaps; source trees untouched |
| RD event fixture | read-only query over `operational_records` and `operational_curation_links` | exit 0; 7 events retain producer, raw date, venue and flyer/source evidence; 0 false ISO dates; 0 orphan curation links |
| Contract audit refresh | `PYTHONPATH=src ./.venv/bin/python -m flujo.knowledge.contract_registry --db data/mak_knowledge.db audit --root . --record --run-id simulation_consumer_20260820` | exit 0; 59/59 verified; Blender, source-learning bridge, math kernel, tennis, scraping, deep-learning and simulation consumers resolved |
| Hub smoke | `./.venv/bin/python scripts/hub_smoke.py --port 0 --timeout 20` | exit 0; temporary port 48545; no persistent hub |
| Remote parity | `git rev-parse HEAD` vs `git ls-remote origin refs/heads/main` | equal when the commands return the same value |

## Conflicts and risks

- `abstain` is intentional. Eight eligible episodes now span four projects, but
  the deterministic split still produced no independent holdout; promoting a
  general route policy would overstate the evidence.
- `data/mak_knowledge.db` and generated research SQLite/report files are local
  operational state and are not Git inventory. Their current state is noted,
  not copied into the web repo.
- Historical phase documents and recovered sessions remain evidence. They are
  not the current handoff and must not override this file.
- A green local check does not prove external GitHub Actions or provider
  credentials. The push completed normally and remote parity was checked;
  external CI remains an independent gate.
- The official P versus NP capture is a normalized curator note, not a
  verbatim source transcript or semantic-equivalence certificate. It supplies
  provenance and hashes but intentionally cannot change `UNTRUSTED`.
- The current `attention` state is intentional and concrete: two ledger
  evidence gaps plus two informational safety states. Do not silence it by
  deleting episodes or promoting same-project data. The Blender dependency is
  no longer an open gap; its fresh audit is verified.
- Watsonx, AWS and Azure historical labels remain in preserved ledgers, old
  visual records, comments and legacy triangulation filenames. They are data
  provenance, not executable integrations. Do not delete or reinterpret those
  records as current provider health. Cerebras remains configured only for
  explicit diagnostic use; its current billing response is HTTP 402 and it is
  not part of the default chain.

## Active cleanup audit — 2026-08-21

Se depuro la configuracion activa para que MAK Linux no presente superficies
Windows obsoletas como si fueran runtime. Se retiraron los lanzadores
`abrir_hub.bat`, `instalar.bat`, `launch-flujo.bat`, `launch-flujo.ps1`, el
puente `tools/bridge_issue_render.py`, sus helpers SendTo y su e2e, y el
workflow Claude deshabilitado. Sus copias historicas siguen en
`/home/mak/WIN` o en la evidencia recuperada. Se retiro solo el test que
ratcheaba esos lanzadores; se conservaron el mirror y los tests de seguridad
que aun tienen consumidores reales.

XIO fue corregido durante la auditoria: no es basura ni se elimina. Se
restauro `.github/workflows/build-xio-apk.yml` como build manual diferido y
se documento como integracion futura Chataigne/OSC para shows, venues y VJ.
No se ejecuta en cada CI ni se confunde con la ruta diaria de FLUJO/RD.

Tambien se actualizaron `CAPACIDADES.md`, `docs/MAK_CURRENT_STATE.md`,
`docs/FLUJO_AREAS_EVENTOS_SUPLEMENTOS.md`, `src/flujo/web/hub.py`, los
paneles web de automatizaciones/eventos, `Makefile`, `pyproject.toml` y los
tests afectados. Se regeneraron `tests/fixtures/idioma_baseline.txt`,
`context/code_structure_index.json` y los HTML de `context/`.

Validacion en primer plano:

- `./.venv/bin/python -m pytest -q` -> exit 0; suite completa, skips esperados.
- Tests focalizados de higiene, contratos Git/web, mirror, GPU, idioma,
  code-index y status -> exit 0.
- `npm run typecheck` en `web/` -> exit 0.
- `npm run build:context` -> exit 0; Node 18 emitio advertencia porque el
  requisito declarado es Node >=20.19, pero el bundle se genero.
- `git diff --check` -> exit 0.

Se agrego `tools/repo_audit.py` como gate read-only del arbol web y las cuatro
SQLite locales. La auditoria real devuelve 36 modulos, 35 alcanzables, 0
muertos, 0 referencias activas obsoletas; `data/rd.db` tiene 20 tablas/7,585
filas, `data/rd_datos.db` 3/0, `data/mak_knowledge.db` 30/369,157 y
`data/flujo.db` 1/6; las cuatro pasan `integrity_check` y todas sus rutas de
consumidor existen. Se corrigio el mapa para no declarar `src/flujo/rd/panel.py`
como lector de `data/rd.db`: el panel lee JSON/YAML canonicos y solo proyecta.

La validacion de `gen_rd_standalone.py` genero en `/tmp` los mismos 6 registros
que `web/src/data/rdDbEmbebida.json`, con SHA-256 identico; el unico fallo
encontrado era el reporte de una ruta absoluta externa y quedo corregido sin
alterar la salida. El intake real uso el indice fuente
`/home/mak/labs/portable-ssd-index-20260813/archivo_index.sqlite`, no el
`intake.sqlite` derivado: con limite 3 y fondo Fondart produjo tres paquetes
`drefgira-fondart`, `felina-logo-fondart` y
`descargas-hasta-rdflyer-2050-fondart` en `/tmp/mak-intake-audit-20260821`.
La salida queda correctamente en `draft_with_evidence_gaps`; no se escribio
la DB de aprendizaje ni se modifico la fuente del SSD.

Riesgos conservados deliberadamente: `tools/mak_ops/check_mak_mirror.py`
todavia contiene una ruta SSH historica y requiere una fase separada de
reemplazo local; `src/flujo/version.py` y `docs/recovered/` conservan
referencias de changelog/evidencia, no runtime. No se borraron `/home/mak/WIN`,
XIO, bases, artefactos ni cambios ajenos.

## Post-publication runtime sync — 2026-08-21

El commit `90f92be` ("chore: publish provider and cross-domain runtime")
publico en un solo commit atomico los tres conjuntos que quedaban fuera de
`69e7fba`: retiro de Watsonx/AWS/Azure, write set cross-domain completo y la
correccion del paquete de diagnostico Research. 81 archivos, +2172/-1905.
`main` y `origin/main` quedaron sincronizados en `90f92be`; el CI remoto pasa
en los tres jobs: `CI` (run 32454523320), `seguridad` (32454523238) y
`Git topology guard` (32454523301). Los cuatro tests que estaban rojos en
`268ef4b` pasan: `test_tools_en_registro`,
`test_registro_sin_herramientas_fantasma`,
`test_no_new_file_carries_spanish_comments` y
`test_the_manifest_is_not_stale_against_the_real_cli`. La causa raiz fue
publicar artefactos derivados generados desde un worktree sucio mientras sus
fuentes quedaban sin stagear; no volver a publicar `CAPACIDADES.md`,
`context/comandos.json`, `idioma_baseline.txt` o el code index sin las fuentes
que describen.

Resolucion del Grupo 4, sin consultar: en `src/flujo/version.py` se revirtio
el unico hunk que falsificaba evidencia temporal, de modo que el incidente de
claves de 2026-07-16 conserva sus proveedores reales
(Tavily/Groq/Cerebras/Azure); `tests/test_privacidad_repo.py` volvio al estado
publicado porque su exencion nueva no tenia sujeto
(`context/fases.migracion.md` ya fue anonimizado en `6743467` y hoy tiene 0
coincidencias). Las versiones de worktree quedaron en
`/home/mak/_archive/group4-reverted-20260821/`.

El indice `context/code_structure_index.json` se regenero desde el arbol
publicado: 783 modulos Python, 8565 simbolos, 187046 lineas declaradas, 0
errores de sintaxis, sin texto fuente. Ya no declara los cuatro modulos
watsonx y `lane_registry` resuelve su consumidor real
(`imported_by = src.flujo.knowledge.system_status`).

El Hub existente `mak-hub.service` es un unit de usuario
(`systemctl --user`), no de sistema; su launcher
`/home/mak/plataforma/hub.py` es una proyeccion que carga la implementacion
canonica `cultura/mak_plataforma/hub.py` del repo. Se reinicio solo ese
servicio. Evidencia del reload: antes del reinicio `/api/status` aun
mencionaba `watsonx`; despues menciona `gemini` y ya no `watsonx`. GET
verificados: `/health` 200 (`mak-hub-health-v1`), `/api/status` 200
(`mak-system-status-v1`, `read_only=true`, 11 componentes, `status=attention`
con 2 accionables y 2 informativos, componente `lanes` `ready` y valido),
`/api/research/catalog` 200, `/api/project/learning` 200, `/api/rd/summary`
200 y `/api/rd/crosswalk` 200. `/api/rd-db` devuelve 404
`ruta_api_no_encontrada`: esa ruta no existe, las reales son `/api/rd/*`. No
se llamo ningun mutador y no se inicio ningun servicio nuevo;
`mak-codex.service` y `mak-research.service` siguen activos sin tocarse.

Proveedores probados una sola vez en primer plano con los adaptadores
existentes: `research_lib.LLM` devolvio texto no vacio para `groq`, `gemini` y
`ollama`; `cerebras` devolvio HTTP 402 `payment_required`;
`providers.call("gemini", response_format="json")` devolvio JSON valido; y
`source_pipeline.capture_url("https://example.com", backend="firecrawl")`
capturo 167 caracteres con backend `firecrawl`. El registro
`faro-provider-registry-v1` lista groq, gemini, cerebras y ollama como
`configured`, sin Watsonx, AWS ni Azure. `route_task("research")` resuelve
capacidad `hypothesis` con proveedor `groq`.

## Continuity after Claude quota interruption — 2026-08-21

Claude Code agoto su cuota despues de publicar `4c12bba` mientras anunciaba
el inicio de la validacion del slice de portabilidad/pipeline. No quedo un
comando de intake, render, pytest ni Blender corriendo. El archivo temporal
`/tmp/mak_continuation_result.json` es evidencia de una ejecucion anterior y
termina en `9841cc8`; no usarlo como estado actual ni como fuente para repetir
trabajo.

Estado fisico comprobado en primer plano: `main == origin/main == 4c12bba`,
worktree limpio; `mak-hub.service`, `mak-research.service` y
`mak-codex.service` siguen activos como unidades de usuario existentes. GET
read-only de Hub `/health`, `/api/status`, `/api/research/catalog`,
`/api/project/learning`, `/api/rd/summary` y `/api/rd/crosswalk` devolvieron
HTTP 200. Research `8890` y Codex `8891` devolvieron HTTP 200 en su raiz.

Validacion actual, sin mutar fuentes: `route_task` devolvio las cadenas
automaticas `groq -> gemini -> ollama` para research, curation y review;
judge resolvio `ollama -> local_deterministic`; Cerebras solo aparece cuando
el caller lo nombra explicitamente. Tests de intake, puente operativo,
source-learning y tandas pasaron (`pytest`, exit 0). Integridad read-only de
`data/rd.db`, `data/rd_datos.db`, `data/mak_knowledge.db` y `data/flujo.db`
devolvio `ok` en las cuatro bases. `compileall` y `git diff --check` pasaron,
exit 0. No se modificaron archivos del runtime durante esta comprobacion.

Advertencia de evidencia CORREGIDA el 2026-08-21: esa afirmacion era falsa.
El indice fisico externo si esta presente en
`/home/mak/labs/portable-ssd-index-20260813/archivo_index.sqlite`
(175689728 bytes, 2026-08-13). El generador de intake se re-ejecuto y el
pipeline quedo medido de punta a punta; ver la seccion
`Pending-slice closure` mas abajo. No usar la advertencia anterior como razon
para no medir.

Riesgo residual: el nombre historico `PROVIDER_ORDER` aun contiene Cerebras
para poder mostrarlo en el registro diagnostico; esto no lo vuelve fallback,
porque `provider_plan` lo excluye sin `available=["cerebras"]`. No cambiarlo
sin actualizar el contrato de registro y sus tests.

Archivos modificados en esta continuidad: solo este handoff dentro del repo.
Fuera del repo se agrego una fuente de evidencia acotada bajo
`/home/mak/curatoria_inbox/tennis_sources/2026-08-21/` y se agrego de forma
append-only el Project IR/episodio correspondiente a `data/mak_knowledge.db`.
No hubo borrado, instalacion ni nuevo servicio.

## Independent tennis evidence — 2026-08-21

La segunda fuente independiente ya fue ingerida y validada. Fuente publica:
`https://raw.githubusercontent.com/JeffSackmann/tennis_MatchChartingProject/master/charting-m-points-2020s.csv`.
El archivo completo quedo fuera del repo en
`/home/mak/curatoria_inbox/tennis_sources/2026-08-21/charting-m-points-2020s.csv`
con SHA-256
`2cd43f73e0530a47ac02b99dae40177ca6d58a8ccf9189358eb05dffb4be9a`.
La licencia y atribucion CC BY-NC-SA 4.0 estan registradas en
`SOURCE_MANIFEST.json`; no se permite uso comercial.

Se extrajeron solo dos filas reales del partido
`20260521-M-Roland_Garros-Q3-Jesper_De_Jong-Michael_Zheng` a
`charting-m-points-2020s-extract.csv`, hash
`ac618e8222d02aa051b6d92dfd6414796974bc90fe362c65067f0c031faea822`.
`tools/tennis_shot_events.py` produjo 11 eventos; el validador JSON Schema
paso, el hash del extracto se propago a cada evento y 35 tokens desconocidos
se conservaron sin inferencia.

Project IR `mak-tennis-decision-lab-external-20260821` quedo `active` con
episodio verificado `episode-tennis-external-mcp-20260821`. La primera ruta
abstuvo correctamente porque el proyecto fue etiquetado tambien como
`research`; al corregir su dominio a solo `tennis`, la ruta selecciono
`tennis_shot_event_consumer` con `execute_read_only`. El aprendizaje global
se consulto en modo read-only: `status=abstain`, `eligible_examples=9`,
`holdout_count=0`, `recordable=false`; la nueva evidencia no se transformo en
entrenamiento ni en regla promovida.

## RD thematic integration — 2026-08-21

La seccion RD de `flujo serve` ahora separa la proyeccion canonica en cinco
temas read-only: operacion en terreno, calendario/red de eventos, testeo y
evidencia, productos/activos de entrega y puentes con Cultura/Portfolio. La
separacion es una vista, no una segunda base: `data/rd.db` sigue siendo la
proyeccion canonica y `data/rd_datos.db` sigue vacia como frontera de runtime.

Se agrego el contrato `mak-rd-topics-v1` en `src/flujo/departments.py` y se
expuso en los dos servidores locales: `flujo serve` (`/api/rd/topics`) y el
Hub 8900 (`/api/rd/topics`). `flujo serve` tambien recupero `/api/rd-db` y
los logos en GET read-only, por lo que la interfaz RD ya no queda desconectada
cuando se abre por el servidor stdlib. El panel muestra los cinco temas y los
puentes sin habilitar mutaciones.

Validacion de esta fase:

- `./.venv/bin/pytest -q tests/test_serve_api.py tests/test_departments.py tests/test_rd_db_logos.py tests/test_tarifa_una_sola_fuente.py`: exit 0, 46 tests.
- `./.venv/bin/pytest -q --disable-warnings`: exit 0, suite completa.
- `npm run typecheck`: exit 0.
- `npm run build:context`: exit 0; warning no bloqueante: Node 18.20.4 esta bajo el minimo recomendado por Vite 7.
- `npm run build:rd`: primero exit 1 por `import.meta.dirname` en `copy-rd-share.mjs`; corregido con `fileURLToPath`, segundo intento exit 0.
- servidor temporal de `flujo serve`: `/api/rd/topics`, `/api/rd/summary`, `/api/rd-db` y HTML respondieron HTTP 200; se detuvo al terminar.
- `git diff --check` y `compileall`: exit 0.

Write set: `src/flujo/departments.py`, `src/flujo/serve/`,
`src/flujo/web/hub.py`, `cultura/mak_plataforma/hub.py`,
`web/src/components/RdDbPanel.tsx`, `web/scripts/copy-rd-share.mjs`, pruebas y
los HTML compilados de `context/`. No se modificaron bases, WIN, README/SVG
protegido ni se dejaron servicios nuevos.

## Pending-slice closure — 2026-08-21

Se retomaron exclusivamente los slices que quedaron abiertos en la sesion
interrumpida por cuota. Los slices ya cerrados (`a5b1900`, `1f474e7`,
`4c12bba`, `7f99a50`, `2a6e2e0`, `5d915cb`) no se repitieron ni se revirtieron.

Estado verificado antes de tocar nada: `main == origin/main == 5d915cb`,
worktree limpio. Cerebras: `route_task` devolvio `groq -> [gemini, ollama]`
para research, curation y review, y `ollama -> [local_deterministic]` para
judge; `OPT_IN_PROVIDERS == {'cerebras'}`. Guards de proyecciones, proveedores
y hub: exit 0. Ese conjunto ya estaba cerrado y solo se comprobo.

Defecto real encontrado y reparado: el mismo par de bugs que se habia
corregido en `cultura/mak_plataforma/hub.py` seguia intacto en
`src/flujo/web/hub.py`, el hub de `flujo serve`. Publicaba
`registry: "research/jardines_interpretativos/jardines_interpretativos.sqlite"`,
una ruta relativa que no resuelve desde ningun directorio de trabajo porque el
registro vive fuera del repo, y `/api/research/job` sin `id` devolvia el
`ValueError` crudo de `int()`. Reparar una sola superficie fue lo que permitio
que el bug sobreviviera, asi que ahora
`tests/test_research_registry_contract.py` fija el contrato en las dos y
compara sus respuestas campo por campo.

Segundo defecto real: `system_status` mantenia su propia lista de candidatos de
Node que terminaba en `PATH` mas un runtime de codex, por lo que informaba
`node available` para el 18.20.4 de `PATH` mientras `web/package.json` declara
`>=20.19.0` y en la misma maquina existen 20.20.2 y 24.x sin listar. La
resolucion se unifico en `runtime_tools` (`node_candidates`, `resolve_node`,
`declared_node_minimum`, que lee el minimo del manifiesto en vez de copiarlo) y
`flujo doctor` ahora nombra el binario que cumple en lugar de dejar que el
build avise y el llamador adivine. Se retiro el `import shutil` que quedo
muerto en `system_status`.

Comandos exactos y codigos de salida:

- `./.venv/bin/python -m pytest -q tests/test_physical_projections.py tests/test_mak_tandas.py tests/test_mak_hub_salud.py -rs`: exit 0.
- `./.venv/bin/python -m pytest -q tests/test_research_registry_contract.py -rs`: exit 0.
- `./.venv/bin/python -m pytest -q tests/test_node_runtime_requirement.py -rs`: exit 0.
- `./.venv/bin/python -m pytest -q tests/`: exit 0, suite completa.
- `./.venv/bin/python scripts/hub_smoke.py --port 0 --timeout 25`: exit 0, puerto efimero 60831, detenido.
- servidor temporal de `flujo.web.hub` en puerto efimero: `/api/research/catalog` HTTP 200 con ruta absoluta y `registry_exists=true`; `/api/research/job` sin `id` HTTP 400 `id_requerido`; `?id=4` HTTP 200; `?id=abc` HTTP 400 `id_requerido`; servidor detenido y thread confirmado muerto.
- `./.venv/bin/python -m flujo doctor`: exit 0; fila `node` avisa que `/usr/bin/node` v18.20.4 esta bajo `>=20.19.0` y nombra un v24.19.0 local.
- `./.venv/bin/python -m flujo diagnose --area research`: exit 0; `route_contract=True`, `local_hub_8900=True`.
- `./.venv/bin/python -m flujo verify --no-pytest`: exit 0; hub smoke en puerto efimero 38231, detenido.
- `flujo health`, `flujo version`, `flujo rd-db packs|eventos|venues|productora creamfields`, `flujo knowledge list`: exit 0 cada uno.
- `tools/research_job_router.py ... --db <temp>`: exit 0; `job_id=5`, `validation=PASS`, `external_calls=0`; la politica emitida dice `Groq o Gemini`, lo que valida el fix de proveedores de punta a punta.
- `tools/execute_research_job.py --job-id 5 --db <temp> --max-sources 1`: exit 0; captura firecrawl con hash, `model_calls=0`, `license_policy` exige revision humana.
- `cultura/mak_curatoria/diagnostico_proyectos.py --db <copia temp> --out <temp>`: exit 0; 45536 miembros, 917 proyectos, cinco salidas derivadas.
- `tools/build_application_intake.py --source-index <SSD real> --out-dir <temp> --fund Fondart --candidate-limit 3 --mak-db data/mak_knowledge.db`: exit 0; tres paquetes `drefgira-fondart`, `felina-logo-fondart`, `descargas-hasta-rdflyer-2050-fondart`; `learning_materialized=[]`; el paquete es `mak-application-package-v1` con `status=draft_with_evidence_gaps`, `readiness=90.0`, fondo `candidate_unverified`, `gaps` con severidad `blocking` y `next_action` explicito; SHA-256 del indice fuente identico antes y despues (`d3afb072fe163312...`).
- `tools/repo_audit.py`, `compileall -q src tools tests`, `pip check`, `git diff --check`: exit 0 los cuatro.
- `npm run typecheck` en `web/` con el Node local v24.19.0: exit 0, sin el aviso de version.

Archivos modificados: `src/flujo/web/hub.py`,
`src/flujo/knowledge/runtime_tools.py`,
`src/flujo/knowledge/system_status.py`, `src/flujo/cli.py`,
`tests/test_research_registry_contract.py` (nuevo),
`tests/test_node_runtime_requirement.py` (nuevo) y este handoff. No se tocaron
bases, WIN, README/SVG, XIO ni el mirror SSH. No se instalo nada y no quedo
ningun servicio ni proceso nuevo: los unicos servidores fueron temporales en
primer plano y se detuvieron.

Riesgos: (1) `PATH` sigue resolviendo Node 18.20.4, asi que un build hecho sin
`NODE_EXE` seguira emitiendo el aviso de Vite; el arreglo hace visible el
binario correcto, no cambia el `PATH` del sistema. (2) `PROVIDER_ORDER` sigue
nombrando Cerebras a proposito para poder mostrarlo en el registro
diagnostico; `provider_plan` lo excluye sin `available=["cerebras"]` y dos
tests lo fijan. (3) Las tres unidades de usuario `mak-hub`, `mak-research` y
`mak-codex` siguen sirviendo el codigo anterior en memoria hasta que se
reinicien; esta fase no las reinicio porque solo cambio `flujo serve`, que no
es un servicio permanente.

## Next concrete action

Continuar desde el commit publicado por esta fase y no repetir ningun slice
cerrado. Los slices de proveedores, contratos de hub, rutas de registro,
proyecciones fisicas, portabilidad de entrypoints, pipeline
DB -> Research -> Curatoria -> Postulacion y requisito de Node estan medidos y
cerrados; releerlos no aporta evidencia nueva.

La accion ejecutable siguiente es reiniciar de forma controlada las tres
unidades de usuario existentes (`mak-hub.service`, `mak-research.service`,
`mak-codex.service`) para que el runtime en memoria pase a servir el codigo ya
publicado, y verificar despues con GET read-only que `/api/research/catalog`
devuelve la ruta absoluta del registro y que `/api/research/job` sin `id`
devuelve `id_requerido`. No crear servicios nuevos.

Fuera de alcance y deliberadamente pendientes, porque dependen de licencia,
decision humana o hardware externo: la licencia de Research 4
(`result.license_review = pending`), el holdout independiente del gate de deep
learning (`abstain` con 9 elegibles y holdout 0), XIO (solo
`workflow_dispatch`), el mirror SSH historico
(`tools/mak_ops/check_mak_mirror.py`) y cualquier promocion de verdad
matematica (`MILLENNIUM-PNP-001` sigue `UNTRUSTED`).

## Previous completed checkpoint

The operational DB bridge is complete for the current source contracts. The
master now carries a normalized projection without replacing source authority:
RD events/producers/venues, Fondart v5 applications, intake projects/funds/
packages, and the existing `mak_links` curation surface. The real bridge
returned exit 0, wrote 6,132 normalized records, transferred 106,895 curation
links, copied 0 source rows, and a foreground SQL check resolved
`SCD package -> SCD project -> Fondart -> 12 curation links`.

The foreground `DB -> Research -> Curatoria -> Postulacion` check is complete:
Research exposed 5,179 applications and 14 captures read-only; Curatoria
processed 917 projects, 13,121 families and 45,536 members in a temporary
SQLite copy; Postulacion generated `drefgira-fondart` with explicit evidence
gaps. Exit was 0 and source trees were untouched. Preserve unknown dates as
`date_raw`, accept exact source-key joins as exact, and retain candidate venue
links with confidence.

The DB pipeline and RD event fixture are green. The next action belongs to the
separate operational audit: run the next real consumer/event fixture only if
it represents a different path, and fix only a runtime blocker. Do not start
autonomy, deep learning, broad reindexing or another database until the
declared current consumers are green.

## Last verified

2026-08-21 America/Santiago — cierre de los slices que quedaron abiertos por la
interrupcion de cuota. Se comprobo primero que Cerebras ya estaba solo como
opt-in y que los guards de proyecciones pasaban (exit 0), y solo se
modifico lo que seguia roto: los dos contratos de `src/flujo/web/hub.py` (ruta
de registro relativa y `id` sin validar), que eran el mismo defecto ya
corregido en el hub de plataforma pero nunca replicado; y la resolucion de Node,
que informaba `available` para el 18.20.4 de `PATH` mientras el manifiesto
declara `>=20.19.0` y en la maquina hay 20.20.2 y 24.x. Suite completa exit 0;
typecheck web exit 0 con el Node local v24.19.0 y sin aviso de version;
`repo_audit`, `compileall`, `pip check` y `git diff --check` exit 0; hub smoke y
un servidor temporal de `flujo.web.hub` en puertos efimeros, ambos detenidos.
Pipeline medido de punta a punta contra fuentes reales con salidas temporales:
Research `job_id=5` `validation=PASS` con politica `Groq o Gemini`, captura
firecrawl con hash y `model_calls=0`, Curatoria 917 proyectos / 45536 miembros
sobre copia temporal, y Postulacion con tres paquetes Fondart en
`draft_with_evidence_gaps`, `gaps` bloqueantes explicitos y el SHA-256 del
indice SSD identico antes y despues. Se corrigio en este archivo la afirmacion
falsa de que el indice SSD no estaba visible: si lo esta.

2026-08-21 America/Santiago — continuidad posterior a la cuota verificada y
publicada en `7f99a50`: `main == origin/main`, worktree limpio, servicios de
usuario activos, cuatro SQLite integras, tests focalizados exit 0 y segunda
fuente de tenis verificada con ruta `tennis_shot_event_consumer`. El learner
sigue en `abstain` por `holdout_count=0`; no se promovio aprendizaje.

2026-08-21 America/Santiago — publicacion `90f92be` y sincronizacion del
runtime verificadas. Validado antes del commit en un clon git limpio con el
patch staged aplicado, no en el worktree sucio: pytest completo exit 0,
`flujo verify` exit 0 con hub smoke en puerto efimero, typecheck web exit 0 con
Node 24.18.0, `npm run build:context` exit 0, `gen_archivo_iskvw` exit 0,
`tools/repo_audit.py` exit 0, compileall exit 0, `pip check` exit 0 y
`git diff --check` exit 0. `main` == `origin/main` == `90f92be`; CI, seguridad
y Git topology guard en `success`. Despues de publicar: indice regenerado (783
modulos), Hub de usuario reiniciado y sirviendo el codigo publicado, cinco
familias de GET verificadas read-only, y cinco proveedores auditados con una
sola llamada cada uno. Abiertos confirmados sin fabricar evidencia: Research 4
`license_pending` (`result.license_review = pending` en
`/home/mak/research/jobs/4/verified_result.json`); gate de deep learning
`abstained` con `rows=3`, `independent_holdout=false` y
`training_permitted=false`, y el learner en `abstain` por
`no_independent_holdout` con 9 elegibles y holdout 0; tenis
segunda fuente independiente verificada en
`/home/mak/curatoria_inbox/tennis_sources/2026-08-21/`; XIO diferido en
`workflow_dispatch`;
mirror SSH intacto y fuera de alcance.

2026-08-21 America/Santiago — web/DB cleanup gate and bounded intake verified;
published in commit `69e7fba` and pushed to `origin/main`:
the active web graph has 36 modules, 35 reachable and 0 dead; stale active
references are 0; `rd.db`, `rd_datos.db`, `mak_knowledge.db` and `flujo.db`
pass read-only integrity checks with all declared consumers present. RD live
and standalone projections are equal by SHA-256. The source-index intake used
the physical SSD index, emitted three bounded Fondart packages in `/tmp`, and
left the source and learning DB untouched. The only runtime defect found was
the standalone generator's absolute-output display path; it was fixed and
focused tests passed. The remaining worktree changes are intentionally outside
that commit and must be handled by the next bounded slice.

2026-08-20 America/Santiago — Python structure index and dual debugging slice
verified: `flujo code-index` generated the source-free 781-module index,
consumer resolution and bounded query brief; focused and full pytest passed,
map synchronization passed, compileall and diff check passed. Watsonx/AWS/Azure
retirement and provider
replacement verified: active registries/chains/UI/configuration removed,
Gemini 3.6 Flash works in both LLM and structured platform adapters, Groq,
Ollama and Firecrawl probes pass, Cerebras returns HTTP 402 and is opt-in only,
four exclusive tools and two env snapshots archived, boto3 dependency removed,
compileall exit 0, full pytest exit 0, pip check exit 0 and diff check clean.
Historical WIN/ledgers/results preserved. Official
P versus NP source/formal hashes
recorded without changing `UNTRUSTED`, Research 4 capture and bounded
simulation were checked without biological claims, 59-contract audit refreshed,
source-learning case preserved, 19-lane cross-domain registry validated
locally, tennis MCP parser/shot-event route and fixture episode passed,
Research 4 capture and logo-clean abstention were linked to Project IR, live
status and full pytest rechecked, and the published baseline remains
`7674c49`/`17ccff7`. The cross-domain write set is not yet published.

2026-08-20 America/Santiago — catalog federation slice verified: focused
tests `3 passed`, py_compile exit 0, diff check exit 0; real metadata-only
federation exit 0; 7 sources, 124 tables, 2,075,337 observed rows, 0 copied;
master integrity `ok`, foreign-key issues `[]`, orphan tables/links `0`.
Added source/target contract files; full suite `./.venv/bin/python -m pytest -q`
completed at 100% with exit 0 (warnings only); no source database contents were
rewritten and no commit or push has been made for this slice.

2026-08-20 America/Santiago — operational bridge slice verified: focused
bridge tests `2 passed`, py_compile and diff check exit 0; real refresh exit 0;
6,132 normalized records and 106,895 curation links; source rows copied `0`;
master integrity `ok`, foreign-key issues `[]`; SQL pipeline sample resolved
application package `SCD` to project `SCD`, fund `Fondart` and 12 curation
links. Seven RD event records retain producer/venue/source payloads; non-ISO
date strings remain unnormalized. Full repository suite completed at 100% with
exit 0; only existing deprecation warnings were emitted.

2026-08-20 America/Santiago — foreground pipeline verified: Research read-only
source exposed 5,179 Fondart applications and 14 captures; Curatoria ran on a
temporary SQLite backup and produced 917 projects, 13,121 families and 45,536
members; Postulacion ran against the existing index and emitted
`drefgira-fondart` with status `draft_with_evidence_gaps`; all commands exit 0,
temporary outputs only, no source mutation. Operational closure comes before
the autonomy phase.

2026-08-20 America/Santiago — RD event fixture audit verified read-only: 7
events all retain producer, raw date, venue and flyer/source evidence; 0 were
forced into ISO dates and 0 curation links are orphaned. No source mutation or
new process remained.
