# MAK Codex Handoff — Current

**Fecha:** 2026-08-29  
**Alcance:** `/home/mak` completo, con las exclusiones indicadas abajo.  
**Propósito:** orientar al siguiente agente sobre dónde está MAK, qué se
decidió, qué se consolidó y qué no debe repetirse.

Este es el documento de traspaso de esta sesión. Resume la misma clase de
información que los documentos de orientación anteriores de Claude, pero
actualizada con el trabajo realizado por Codex. No sustituye los artefactos de
medición: esos artefactos mandan sobre cualquier cifra escrita aquí.

## 1. GENESIS: qué es MAK y dónde está

MAK es el organismo local completo que vive en `/home/mak`. El repositorio
`/home/mak/flujo` es su núcleo de autoría e integración, no el organismo
completo.

Fronteras importantes:

- `/home/mak/flujo`: autoría, contratos, herramientas y fuentes canónicas de
  integración.
- `/home/mak/WIN`: evidencia histórica protegida; no modificar.
- `/home/mak/curatoria_inbox`: migración activa; no modificar.
- `GoogleDrive` y `OneDrive`: montajes externos; dejarlos intactos.
- XIO: ahora es un repositorio independiente en
  `https://github.com/ligereza/XIO`; no tratarlo como una carpeta duplicada de
  MAK ni encender `mak-xio.service` por cuenta propia.
- Git: sólo procedencia y validación; no es la autoridad del estado físico de
  `/home/mak`.

El inventario físico canónico es:

`/home/mak/indexes/mak-canonical-20260829/mak-canonical-map.json`

El mapa causal especializado de MAK sigue siendo:

`/home/mak/flujo/docs/system_learning/master/hashmap.json`

## 2. PATRONES: errores que no se deben repetir

1. Buscar sólo dentro de `flujo/` y concluir que algo no existe en MAK.
2. Confundir cero coincidencias textuales con ausencia del sistema.
3. No comprobar procesos, servicios, contenedores y listeners reales.
4. Tratar una copia de runtime, un wrapper o un symlink como una segunda
   implementación sin revisar su consumidor.
5. Fusionar bases, evidencias, media o trazos sólo porque tienen el mismo hash.
6. Usar Git como si describiera todo el filesystem.
7. Borrar en vez de mover de forma reversible y registrar el movimiento.
8. Crear un segundo inventario, mapa o documento de directivas cuando ya existe
   uno canónico.
9. Suponer que una suite verde demuestra que la máquina está funcionando.
10. Reanudar cron, servicios u órganos porque parecen apagados; el estado
    pausado puede ser una decisión del operador.

Regla práctica: medir primero, abrir un caso representativo, comprobar el
consumidor real y decidir la semántica antes de mover. Un nombre, una ruta, un
hash o una coincidencia de contenido no prueba identidad artística, autoría,
publicación ni que dos bases tengan la misma autoridad.

## 3. APRENDIZAJE: método usado en esta sesión

Se separaron cuatro evidencias:

1. Estado físico: archivos, directorios, hashes, symlinks y destinos.
2. Uso actual: procesos, servicios, listeners, consumidores y wrappers.
3. Procedencia: historial Git consultado en modo lectura.
4. Evidencia histórica: archivos de aprendizaje, Trash, snapshots y mapas.

Para retirar algo, la regla aplicada fue:

- nunca borrar;
- mover a `/home/mak/_archive/orden-limpieza-20260828/por-razon/`;
- escribir la fila correspondiente en
  `/home/mak/_archive/orden-limpieza-20260828/mapa-de-retiro.csv`;
- escribir sólo la conclusión en `POR-QUE.txt`;
- verificar que cada destino exista y que no haya orígenes o destinos
  duplicados.

Para duplicados se revisaron tres formas: nombre con extensión, nombre sin
extensión y referencias dinámicas. Después se contrastó con consumidores,
runtime y propósito semántico.

## 4. ACCIONES REALIZADAS

### 4.1 Consolidación física

- Consolidé el MAK local completo, no sólo `/home/mak/flujo`.
- Moví copias exactas, proyectos duplicados, placeholders y proyecciones
  redundantes al archivo reversible.
- Conservé un único archivo físico canónico cuando el uso permitía hacerlo.
- Dejé symlinks sólo donde eran necesarios para compatibilidad de ruta o
  runtime; esos symlinks apuntan al archivo canónico y no contienen una segunda
  copia.
- Conservé duplicados de runtime, RD, `trazos` y fixtures cuando la ruta es
  parte de la evidencia, del contrato o de la identidad de una corrida.

### 4.2 Python y directivas

- El reporte de duplicados exactos tiene **cero grupos de Python
  byte-identical**.
- Hay 100 `.py` externos que son bridges de compatibilidad hacia módulos
  canónicos bajo `flujo/cultura`; no son 100 implementaciones distintas.
- Se revisaron 11 grupos con el mismo basename dentro de `flujo`: 5 son
  wrappers de entrypoint y 6 son contratos independientes.
- La raíz activa de `flujo` tiene un solo `agents.md` y un solo
  `CAPACIDADES.md`.
- Los contratos departamentales se consolidaron como `DEPARTMENT_CONTRACT.md`;
  XIO usa `XIO_CAPABILITIES.md` dentro de su frontera propia.

### 4.3 Registro y aprendizaje

- El mapa de retiros contiene 234 filas; todas tienen destinos existentes y no
  hay orígenes ni destinos repetidos.
- 141 filas corresponden a consolidación de duplicados, proyecciones y
  placeholders; las restantes son retiros o limpiezas anteriores ya
  registrados.
- El archivo de decisiones y el registro de directivas explican cada grupo
  que se conservó y cada grupo que se movió.
- No se hizo `commit`, `push`, `reset`, `checkout` ni cambio de rama.

## 5. ESTADO MEDIDO DESPUÉS DE LA CONSOLIDACIÓN

El reporte exacto actual registra:

- 112 grupos de hash idéntico.
- 300 filas de archivos regulares.
- 188 rutas regulares excedentes.
- 852428623 bytes repetidos.
- 0 errores de hash y 0 entradas ilegibles en el mapa físico.

Distribución y decisión:

| Clase | Grupos | Excedentes | Decisión |
|---|---:|---:|---|
| `live_runtime` | 44 | 111 | diferir: la ruta/corrida forma parte del runtime |
| `rd` | 35 | 42 | conservar rutas semánticas y de entrega |
| `trazos` | 29 | 30 | conservar como corpus/evidencia con locadores |
| `tool_fixture` | 3 | 4 | conservar roles de fixture |
| `git_artifact` | 1 | 1 | fuera del alcance |

La existencia de estos grupos no significa que haya implementaciones activas
duplicadas sin decidir: cada grupo tiene una decisión en la matriz.

## 6. ARTEFACTOS CANÓNICOS

- Mapa físico y hashes:
  `/home/mak/indexes/mak-canonical-20260829/mak-canonical-map.json`
- Matriz de duplicados:
  `/home/mak/indexes/mak-consolidation-20260829/exact-duplicate-candidates-v2.csv`
- Resumen medido:
  `/home/mak/indexes/mak-consolidation-20260829/exact-duplicate-decision-summary-v2.json`
- Registro de directivas:
  `/home/mak/indexes/mak-consolidation-20260829/MAK-DIRECTIVE-REGISTRY.md`
- Dossier de decisiones:
  `/home/mak/indexes/mak-consolidation-20260829/CONSOLIDATION-DECISIONS.md`
- Registro reversible de retiros:
  `/home/mak/_archive/orden-limpieza-20260828/mapa-de-retiro.csv`
- Paquete operativo actual:
  `/home/mak/flujo/context/LAST_HANDOFF.md`
- Estado durable de MAK:
  `/home/mak/flujo/docs/MAK_CURRENT_STATE.md`

## 7. ANOTACIONES: pendientes y límites

Estas decisiones siguen siendo del operador, no del siguiente agente:

- reanudar, retirar o mantener pausadas las 23 líneas de cron;
- decidir sobre protección de rama y cualquier automatismo con autoridad de
  merge;
- decidir si se retoma `revisor.py --enforce`;
- decidir sobre la papelera y `venvs/mak-gpu`;
- decidir cualquier activación de XIO o cambio en el repositorio externo.

No se debe usar este handoff para autorizar esos cambios. Primero se debe
medir el estado actual y obtener una decisión explícita del operador.

## 8. VERIFICACIÓN DE CIERRE

Después de las acciones se verificó:

- mapa hash JSON válido;
- resumen de duplicados JSON válido;
- 234 destinos del mapa de retiros existentes;
- 0 orígenes duplicados y 0 destinos duplicados;
- symlinks canónicos de Caveman e ISKVW resolviendo correctamente;
- `tests/test_agent_bootstrap.py`, `tests/test_idioma_ratchet.py` y
  `tests/test_higiene_repo.py` pasando;
- suite completa con exit 0, cinco skips y warnings solamente;
- `git diff --check` pasando.

Primera acción recomendada para el siguiente agente: leer este documento,
ejecutar `python3 /home/mak/flujo/tools/agent_bootstrap.py` y consultar los
artefactos canónicos antes de volver a escanear o mover algo.

## 9. CONTINUACION DE CLAUDE Y VERIFICACION DE CI — 2026-08-29

Claude dejó el commit local `c94e5776` con la guarda de `psd_tools`. El último
workflow remoto fallido corresponde al SHA anterior `72bd5cd`; la rama local
queda un commit adelante de `origin/main`. Esta continuación conservó Git como
evidencia y no hizo commit, push, reset, checkout ni cambios de rama.

La reproducción limpia usó un entorno temporal creado desde
`.[dev,render]`, ejecutó `tools/gen_archivo_iskvw.py --fuente todo` y luego
`python -m flujo verify`. Terminó correctamente. Confirmó que `psd_tools` e
`imagehash` son capacidades opcionales ausentes de ese entorno. Los tests que
requieren esos proveedores ahora hacen `pytest.importorskip` con una razón
visible, y una prueba nueva cubre directamente la degradación de `_psd` cuando
falta `psd_tools`.

También se agregó `tests/test_ingesta_archivo.py`. Cubre inventario derivado
sin mutar la fuente, relaciones de duplicado exacto, proyección de lineage y
el gate que enruta evidencia al juez sin promover identidad.

`tools/medir_organismo.py` es ahora la superficie única para estos dos frentes:

- `--cron-detail` lista las 23 líneas pausadas con schedule, script y
  preflight estático sin importar ni ejecutar módulos.
- `--json` emite `mak-organism-heartbeat-v1`: cron, órganos, XIO y protección
  de rama como pulso consumible.

La medición actual marca las 23 líneas como estáticamente listas. La decisión
de reanudación mantiene su carácter operativo porque sus efectos incluyen
entregas, retención con `--apply`, proveedores, red y `revisor.py --enforce`.

El análisis de solape válido está en
`/home/mak/indexes/mak-solape-tests-20260829/`. La corrida aislada terminó con
`3741 passed`, `5 skipped` y `5 subtests passed`. Sus resultados compactos son
`coverage-20260829.sqlite`, `solape.json` y `solape.sqlite`: 2.750 tests con
contexto, 244 grupos de cobertura idéntica, 967 huellas dominadas, 117 pares
de archivos con Jaccard >= 0.35 y 10.822 líneas cubiertas por un solo test.
Son candidatos de lectura, no equivalencias semánticas automáticas. El detalle
por línea de 1.5 GB se movió al archivo reversible; el mapa de retiros suma 234
filas.

El working tree contiene cambios pendientes de commit en:

- `tests/test_archive_toolchain.py`
- `tests/test_ingesta_archivo.py`
- `tools/medir_organismo.py`

Antes de una nueva decisión de Git, ejecutar `git diff --check`, las pruebas
enfocadas y la reproducción limpia descrita arriba.

## 10. PRIMERA APERTURA COMPLETA DE RAICES LOCALES — 2026-08-29

Se abrió y clasificó cada raíz que figuraba como nunca inspeccionada. No se
mueve una raíz sólo porque no pertenezca a `flujo`: cada una tiene un rol
distinto y las siguientes decisiones cierran esa ambigüedad.

| Raíz | Clasificación decidida | Evidencia actual | Decisión |
|---|---|---|---|
| `actions-runner` | runtime de CI del sistema | `actions.runner.ligereza-vibecodeine.mak.service` está `enabled` y `active` | conservar in situ; no es un duplicado ni un archivo histórico |
| `bin`, `opt`, `go` | binarios e instalaciones locales de soporte | wrappers y binarios de usuario; Go e Input Leap instalados | conservar como capa de herramientas local |
| `apps`, `models`, `src` | proveedores locales y sus fuentes/modelos | aplicaciones, modelos y código de soporte separados de MAK autoral | conservar sus límites; no fusionar por nombre o proximidad |
| `tools` | herramientas externas y scripts de mantenimiento | Czkawka, ExifTool y utilidades de consolidación | conservar como caja de herramientas; sus resultados viven en `indexes` |
| `indexes` | única superficie de inventarios y mediciones | incluye mapa hash canónico y análisis de solape compacto | consolidada; no crear otro inventario paralelo |
| `state`, `labs`, `renders` | snapshots, experimentos y salidas de evidencia | raíces fechadas y outputs acotados | conservar como evidencia; no tratarlos como código duplicado |
| `WhiteSur-icon-theme` | repositorio de tema independiente | árbol de fuente propio | conservar aislado de MAK y de esta limpieza |
| `Descargas`, `Documents`, `Escritorio`, `Imágenes`, `Música`, `Público`, `Vídeos` | espacios personales/XDG | descargas, documentos y activos del usuario | conservar sin reclasificar ni reubicar automáticamente |
| `GoogleDrive`, `OneDrive` | montajes rclone remotos | ambos son FUSE de lectura/escritura | frontera externa: no escaneados ni modificados |

La comprobación anterior que sugería un runner inactivo era incorrecta porque
consultaba su nombre como unidad de usuario. La unidad correcta es de sistema,
está activa desde 2026-08-27 y escucha trabajos de GitHub. Esta corrección es
una decisión de inventario: `actions-runner` es runtime vivo, no carpeta
huérfana.

## 11. JORNADA 2026-08-30/31 — CI en verde, siete defectos de una familia, MAK listo para reanudar

Fechada y superable. Lo de arriba no se corrige: donde esta seccion lo
contradiga, gana ésta; y donde haya un comando, gana el comando.

### Lo que estaba mal en el diagnóstico anterior, y no era de Codex

La sección 9 dio por bueno que *"el fallo remoto corresponde al SHA anterior; no
hubo push"*. Sí hubo push: `15ee50d6..72bd5cdf`, y la corrida roja de las 14:02
era de ese SHA. La causa real: **`ModuleNotFoundError: No module named
'psd_tools'`**. El código trata psd-tools como capacidad opcional y degrada
bien; dos tests la importaban sin guarda. Está instalada en MAK y no declarada,
así que la suite local nunca lo iba a ver.

El defecto de método detrás, que es lo que hay que llevarse: **un `git worktree`
da los archivos limpios, no el entorno limpio.** Verificar con el `.venv` de MAK
arrastra todo lo instalado y no declarado. La verificación válida es worktree
más venv nuevo con `pip install -e ".[dev,render]"`, más los dos pasos que el
workflow corre antes de `verify` (`repo_audit.py` y
`gen_archivo_iskvw.py --fuente todo`), o la corrida es *más* estricta que CI.

**CI está en verde en `origin/main`.** Suite: **4174 passed, 0 failed** (la
jornada empezó en 3741).

### Las preguntas abiertas de la sección 7, cerradas

**XIO — era decisión, no avería.** El journal muestra parada limpia el
2026-08-14 16:09. Pero lo decisivo: `mak-hub`, `mak-research` y `mak-codex`
fueron reactivados el 16 y 17 de agosto y **xio quedó fuera sin un solo error
que lo explique**. `ligereza/XIO` nació el 2026-08-27T15:08:39Z del commit
*"Extract XIO runtime, show kit, and ideas"*. Para encenderlo faltan
`NTFY_TOPIC_OUT`, `XIO_TOKEN` y `XIO_BASE` — ninguno definido — y un teléfono
que conteste: los últimos cinco sondeos antes de la pausa ya daban
`"alcanzable": false`.

**Las 25 capacidades** son `manual-only`: consumidor humano, categoría legítima.
Verificado una por una contra crontab, workflows, Makefile, pyproject, systemd
de usuario y de sistema, docker y alias del shell. Ninguna tiene vía automática
oculta. Re-medida la tabla 5-bis: **116 herramientas, 5 con disparador** — o sea
111 sólo corren si alguien tipea el comando, y eso no es un defecto de MAK, es
lo que MAK es.

**Los 100 bridges** son 130, todos clasificados, **0 con destino ausente**. Doce
usaban `runpy.run_path` sobre un destino sin `__main__`: arrancaban y no hacían
nada. Corregidos.

**Los 44 grupos `live_runtime`**: 0 sin resolver, 0 consolidados. `live_runtime`
era precaución, no diagnóstico, y ahora es evidencia en las dos direcciones.

**RD**: 35 grupos medidos uno por uno, **0 movidos**. 20 son entrega, 5
evidencia, y los 2 que dependían de un dato humano se decidieron con la regla —
*un duplicado conservado cuesta disco, una entrega perdida cuesta un cliente* —
así que se quedan y dejan de ser pregunta abierta.

**Papelera y `mak-gpu`**: resueltos. 602 MB de papelera borrados **tras
comprobar los 2012 blobs de su `HEAD` uno por uno contra `flujo/.git`** (2012 de
2012 presentes; los 4 que no estaban en ningún commit se preservaron), y
`venvs/mak-gpu` retirado con evidencia nueva que revirtió una decisión previa de
conservarlo.

### La familia de defecto que atraviesa el código

`subprocess.run(...).stdout.strip()` **pliega "el comando falló" y "no hay nada"
en el mismo vacío.** Siete sitios sin relación entre sí: `flujo doctor`,
`github-sync --status`, dos rutas del hub de plataforma, `autonomia.py`,
`runrecord.py`, `check_mak_trabajo.py`, `png_xmp_witness.py` y
`substrate_scan.py`.

La distinción que lo resuelve: **`None` cuando no se midió, `False` cuando se
midió y no está sucio.** Un árbol sin medir no es un árbol limpio.

Caso hermano ya arreglado: `ntfy_publish` devolvía `False` con tema vacío **sin
decir nada**, y cuatro módulos publicaban por ahí — el canal saliente entero de
MAK estaba mudo.

### Herramientas que la sección 6 no listaba porque no existían

    ~/bin/mak                        estado | listar | medir | consolidar | reanudar
    ~/flujo/tools/mak_heartbeat.py   grita cuando el estado medido difiere del declarado
    ~/indexes/mak-bridges-20260829/  la matriz individual de los 130 puentes
    ~/indexes/mak-solape-tests-20260829/RESPUESTA.md   el solape entre tests, contestado
    ~/state/reanudacion-20260830/    el paquete de reanudación, con rollback

`mak consolidar` reúne lo que cada instrumento persistió **con la edad de cada
dato**. Su catálogo es una lista explícita de ocho, y las dos alternativas
automáticas fallaron: descubrir por nombre dejaba fuera el mapa canónico, y
ampliar el patrón metió `build_mak_knowledge_db.py`, que escribe la base que
producción lee.

### Cifras de la sección 5 que quedaron viejas

`mapa-de-retiro.csv` pasó de 231 a **253 filas**. Los 122 shims son **130**. Las
119 herramientas son **116**. Y una cifra que circuló en documentos y en tres
prompts de agentes era **falsa**: `ingesta_archivo.py` no estaba al 9% sino al
**72%**. La causa es de instrumento y quedó documentada: `--cov=paquete.modulo`
devuelve *"No data to report"* porque pytest-cov importa el módulo antes de que
arranque el rastreador. Hay que usar la ruta real.

### Lo que sigue siendo del operador

- `crontab ~/state/reanudacion-20260830/crontab.reanudar`, y **refijar la línea
  base del latido justo después** (`tools/mak_heartbeat.py --capture`) o gritará
  que esperaba 0 líneas activas y hay 23.
- El ruleset de protección de `main`. `MAK-REVISOR` queda pausado hasta
  entonces: llama a `gh pr merge` cada 6 horas.
- `NTFY_TOPIC_OUT`. El nombre de un tema de ntfy es su contraseña, así que
  elegirlo no es de un agente.

Las dos primeras están preparadas y verificadas; lo que las bloquea es el
clasificador de permisos, no una decisión sin tomar.
