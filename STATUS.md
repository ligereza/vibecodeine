# STATUS

Snapshot vivo de coordinación y mantenimiento de `LIBELULA`, director de
moscas. Este archivo se reescribe completo: no es una bitácora ni acumula
historia.

## Coordinación actual

- **Responsable:** `LIBELULA`
- **Fase:** primera simplificación visual del Hub aplicada; queda revisar la
  nomenclatura interna de Research y la integración de paneles secundarios
  `:8900` y saneamiento de referencias ausentes en MICELIO completados, sobre la base de la
  auditoría de salud MAK/FLUJO/XIO y limpieza de RD ya verificada. La
  separación autónoma de FLUJO ya está publicada; XIO sigue siendo un repo
  externo: XIO-RD consume la única proyección RD del host mediante ruta
  explícita o snapshot revisado; XIO-FOH consume el contexto VJ/portfolio de
  la superficie `iskvw`/ISKVW mediante contexto de solo lectura.
- **Directorio de trabajo:** `/home/mak`
- **Fuente de mapa:** `/home/mak/REPOS.md`
- **Contrato raíz repuesto desde historia Git:** `/home/mak/AGENTS.md`
- **Nomenclatura específica leída:** `/home/mak/WACHUMA/NOMENCLATURA.md`
- **Nomenclatura global:** el vocabulario transversal está en
  `DECISIONES.md` y `AGENTS.md`; no existe un archivo global separado llamado
  `NOMENCLATURA`.
- **Criterio:** conservar la autoridad de MAK, preservar cambios locales y
  distinguir sistema, clon, repositorio Git, contenido, fuente, observación,
  medición y representación.
- **Última actualización:** `2026-09-14T19:50:48-03:00`

## Orden operativo vigente

1. `FLUJO` autónomo (`/home/mak/flujo`) y su frontera con XIO/MAK.
2. `MAK` (`/home/mak`) y su historia VIBECODEINE.
3. `XIO` (`/home/mak/XIO`) y la procedencia auxiliar `XIO-IMPORT`.
4. `MOSAIK`, `LUCIDA`, `PUPILA` y `FARMAKSIA`.
5. `VIZZ`, `WACHUMA`, `IRIS` y `bucle`.
6. `MAT-SI` y las superficies de evaluación; después los repositorios de
   soporte.

La actualización Git realizada fue conservadora: se ejecutó `git fetch
--all` en los checkouts con remoto; se hizo fast-forward solo en el checkout
limpio `ml-mobileclip`; no se sobrescribió trabajo local ni se resolvieron
divergencias por fuerza.

## Estado operativo medido

- **Comando:** `/home/mak/.venv/bin/python /home/mak/tools/mak_status.py
  --json` — salida generada correctamente, solo lectura.
- **Estado global del Hub:** `attention`; 3 atenciones y 1 aviso informativo
  en `/api/status` (11 componentes). El comando CLI autónomo agrega además la
  comprobación de almacenamiento y registra 4 atenciones; esa diferencia de
  superficie queda identificada para una próxima unificación del contrato.
- **Servicios alcanzables:** Hub MAK `127.0.0.1:8900` y SearXNG
  `127.0.0.1:8888`; Research y Codex están activos detrás de sockets Unix
  privados del Hub.
- **Atenciones vigentes:** cuota actual de Google Drive; runner de eventos sin
  proceso activo y entrega externa no verificada; 6 proyectos requieren
  revisión y existen 13 episodios abiertos que requieren revisión o evidencia.
- **Dependencias observadas:** Python 3.11.2, Node disponible y Blender en
  `/home/mak/blender/blender`.
- **MAK Hub:** `:8900` respondió 200 en `/health`, `/api/ping`, `/api/status`,
  `/api/departments`, las cuatro rutas RD principales, diagnóstico, archive
  view y las superficies HTML de FLUJO/ISKVW. Research, Codex y Hub están
  vivos; `cola` y `xio_monitor` no están ejecutándose en este momento.
- **Auditoría del Hub — funcionalidad:** las 10 superficies activables, los 6
  recursos de soporte y las rutas API que alimentan sus paneles cargaron en un
  smoke test real; Research, Codex y Portafolio también cargaron sus iframes.
  No hubo errores ni advertencias en la consola del navegador.
- **Auditoría del Hub — jerarquía:** cinco superficies principales quedan
  visibles y las cinco operativas restantes más seis recursos viven en `más`;
  el menú se abre, marca la superficie activa y se cierra al volver al núcleo.
  Research y Codex siguen siendo aplicaciones completas dentro de iframes, por
  lo que el Hub conserva solo su selector exterior.
- **Auditoría del Hub — redundancias candidatas:** `laboratorio` se solapa
  semánticamente con Research aunque su función real son jobs persistentes;
  `ideas` funciona como bandeja de entrada pero repite acciones que también
  aparecen en Micelio; `render`, `decisiones`, `diagnóstico` y parte de
  `áreas` son superficies operativas de baja frecuencia y no deberían pesar
  igual que los consumidores principales. No se elimina ninguna todavía.
- **Inconsistencias detectadas y corregidas:** la tarjeta de estado mostraba
  `Research 8890` y `Codex bridge 8891` en atención porque el diagnóstico
  consultaba los listeners TCP retirados. Ahora comprueba los sockets Unix
  privados y ya no presenta esos puertos como arquitectura actual.
  Permanecen como deuda visual `salud proveedores` sin datos y `No
  configurado` en nodos de Research, que puede confundirse con servicio caído
  aunque la configuración efectiva viva en el runtime.
- **Corrección aplicada:** el contrato compartido de estado ahora prioriza
  `/home/mak/.cache/mak/research.sock` y
  `/home/mak/.cache/mak/codex.sock`, etiqueta ambos consumidores sin puertos
  retirados y conserva TCP solo como fallback explícito de ejecución aislada.
  Se actualizó el espejo usado por el Hub y el checkout autónomo de FLUJO; la
  prueba dirigida quedó en `7 passed`, se reinició solo `mak-hub.service` y

  el smoke real volvió a confirmar las 10 superficies activables. La regresión dirigida del
  Hub, salud y contrato de estado cerró en `28 passed`.
- **Navegación simplificada:** la barra principal conserva cinco superficies
  de uso frecuente —Research, jardines/jobs, Codex, Ideas y Portafolio— y
  agrupa en `más` las cinco superficies operativas restantes y los seis
  recursos de soporte. La prueba real confirmó apertura, selección, cierre del
  menú y retorno a Research; la regresión del Hub quedó en `29 passed`.
- **CODEX/RESEARCH → Hub:** `:8900` es el único listener TCP del stack y
  responde 200 en `/research/`, `/codex/`, `/api/micelio`,
  `/api/research/catalog` y `/api/research/jobs`. RESEARCH y CODEX son
  procesos internos aislados en `/home/mak/.cache/mak/research.sock` y
  `/home/mak/.cache/mak/codex.sock`; no existe conflicto de bind. RESEARCH →
  CODEX y la solicitud de reindexado atraviesan las rutas del Hub, por lo que
  el consumidor trabaja sobre una sola cara.
- **MICELIO auditado:** el índice tiene 5.275 chunks y 1.863 rutas únicas;
  1.819 fuentes estaban presentes y 44 ya no existían antes de la limpieza.
  Tras el reindexado incremental: 5.809 chunks, 1.911 rutas únicas, 0 fuentes
  ausentes; 223 piezas de `~/codex/piezas` y 34 revisiones de
  `~/codex/revisiones` comparten el índice. El grafo publica
  `fuente_estado`/conteos de disponibilidad y las UIs ya interpretan el 404
  sin abrirlo como contenido.
- **Autosync semántico:** los jobs exitosos de CODEX solicitan reindexado al
  Hub; la unidad persistente `mak-research.service` tiene
  `MAK_REINDEX_AFTER_JOB=1`. La operación es best-effort y coalescida: una
  caída temporal de MICELIO no invalida una pieza ya escrita.
- **FLUJO Hub:** con `FLUJO_RD_DB=/home/mak/data/rd.db`, `:8765` respondió 200
  en ping, RD summary/topics/read-only-context, RD panel, VJ events,
  dashboard y SVG. El read model VJ regenerable quedó construido con 7
  eventos, 3 venues y 21 productoras.
- **XIO:** smoke real local del runtime `xio/new/server.py` en puerto de prueba
  cargó 29 plugins; `rd_field` respondió con 42 eventos del host y
  `foh_monitor` con 10 eventos VJ. La suite XIO dio `37 passed`; el launcher
  de host ya no busca una DB inexistente dentro del checkout autónomo FLUJO.
- **RD:** `/home/mak/data/rd.db` está íntegra (`integrity_check=ok`), tiene 40
  tablas no-sistema, 8.040 filas de datos y ningún duplicado exacto ni clave
  lógica duplicada en las tablas operativas. `rd_datos.db` estaba íntegra pero
  vacía (0 filas); se retiró de la ruta activa y quedó recuperable en
  `/home/mak/rd-archive-20260914/rd_datos-empty-20260914.db`.
- **Pruebas:** FLUJO pasó `1.631` pruebas marcadas (`200` quedan fuera por
  clasificación/entorno); el conjunto dirigido de MAK RD/Hub/ISKVW/XIO pasó;
  no se encontraron archivos ni cuerpos de tests duplicados. Se corrigió el
  generador de `docs/CATALOGO_RD.md`, que dejaba una línea en blanco extra al
  finalizar una regeneración. La regresión dirigida de memoria, interfaz,
  proxy y CODEX pasó completa después de la integración, incluida la prueba
  de disponibilidad de fuentes. `runtime_preflight` y `capabilities` quedaron
  sin errores para el transporte Unix; queda un único fallo conocido en una
  prueba que todavía exige que el checkout autónomo `/home/mak/flujo` sea un
  worktree del repo padre, contradiciendo la separación Git vigente.

## Resultado Git posterior al fetch

Los cambios se expresan como `M` (modificado), `D` (eliminado) y `??` (sin
rastrear), según `git status --porcelain`. `A/B` indica commits delante/detrás
respecto de la referencia upstream actual.

| Superficie | Ruta | Rama | Upstream / relación | Cambios locales | HEAD |
|---|---|---|---|---:|---|
| MAK | `/home/mak` | `main` | `vibecodeine-legacy/main` — 0/0 | `M91 D0 ??94` | `4703f101` — `docs: record single RD projection wiring` |
| FLUJO autónomo | `/home/mak/flujo` | `main` | `origin/main` → `ligereza/flujo` — 0/0 | limpio | `32c54b34` — `chore(rd): retire legacy field boundary` |
| FLUJO worktree legado preservado | `/home/mak/flujo-vibecodeine-legacy-20260914` | `integration/flujo-canonical-20260911` | `vibecodeine-legacy/integration/flujo-canonical-20260911` — 0/0 | `M57 D0 ??31` | `f2d08916f823` — 2026-09-12 — `fix(rd): guard complete database reproducibility` |
| XIO | `/home/mak/XIO` | `integration/xio-field-20260911` | `origin/integration/xio-field-20260911` — 0/0 | `M0 D1 ??3` | `ff661cd68120` — `fix(rd): point host launcher at MAK projection` |
| FARMAKSIA | `/home/mak/FARMAKSIA` | `fix/provenance-integrity` | `origin/fix/provenance-integrity` — 0/0 | `M3 D1 ??0` | `779ccd621241` — 2026-09-07 — `docs: leave a NEXT.md with open work, observations and what was not audited` |
| VIZZ | `/home/mak/VIZZ` | `fix/readme-honesty` | `origin/fix/readme-honesty` — 0/0 | `M5 D0 ??7` | `0e72bf0a4636` — 2026-09-07 — `docs: leave a NEXT.md with open work, observations and what was not audited` |
| PUPILA | `/home/mak/PUPILA` | `fix/ambiguity-consistency` | `origin/fix/ambiguity-consistency` — 0/0 | `M0 D0 ??0` | `8e921790ba53` — 2026-09-07 — `docs: leave a NEXT.md with open work, observations and what was not audited` |
| LUCIDA | `/home/mak/LUCIDA` | `docs/next` | `origin/docs/next` — 0/0 | `M0 D0 ??0` | `8a707ab9ffb5` — 2026-09-07 — `docs: leave a NEXT.md with open work, observations and what was not audited` |
| IRIS | `/home/mak/IRIS` | `postulacion/fondart-regional-2027` | `origin/postulacion/fondart-regional-2027` — 0/0 | `M3 D0 ??0` | `e4cafd9887ff` — 2026-09-08 — `docs(iris): add a technical transfer note for the published commit` |
| WACHUMA | `/home/mak/WACHUMA` | `postulacion/fondart-investigacion-2027` | `origin/postulacion/fondart-investigacion-2027` — 0/0 | `M2 D0 ??0` | `4507a29b75cf` — 2026-09-08 — `docs(wachuma): point the transfer note at the commit it actually describes` |
| MOSAIK | `/home/mak/mosaik` | `codex/obras-experimental-rehearsal-mosaik-root` | `origin/codex/obras-experimental-rehearsal-mosaik-root` — 0/0 | `M4 D0 ??1` | `1ab2076cbfb6` — 2026-09-08 — `feat: project semantic lighting to Resolume and Titan` |
| MAT-SI | `/home/mak/MAT-SI` → `/home/mak/Escritorio/MAT-SI` | `main` | `origin/main` — 0/0 | `M0 D0 ??0` | `f7cf473b58e7` — 2026-09-14 — `integrate selective KINO research into MAT-SI` |
| bucle | `/home/mak/bucle` | `main` | `origin/main` — 0/0 | `M0 D0 ??0` | `90ecdf5573fc` — 2026-07-18 — `Merge pull request #3 from miskirabit/arena/019f74a1-bucle` |
| mwb-linux | `/home/mak/src/mwb-linux` | `main` | `origin/main` — 0/2 | `M5 D0 ??0` | `6c3fab3a34f9` — 2026-08-03 — `build(deps): bump actions/setup-go from 6 to 7 (#38)` |
| ml-mobileclip | `/home/mak/src/ml-mobileclip` | `main` | `origin/main` — 0/0 | `M0 D0 ??0` | `48faa0fea4b0` — 2026-09-11 — `Update root files` |
| XIO-IMPORT | `/home/mak/curatoria_inbox/XIO-IMPORT` | `integration/xio-field-20260911` | `origin/integration/xio-field-20260911` — 0/34 | `M41 D1 ??0` | `42495e76512d` — 2026-09-11 — `Initialize RD operational schema for XIO bridge` |
| DIMENSIONES DEL ORDEN | `/home/mak/curatoria_inbox/DIMENSIONES DEL ORDEN` | `master` | sin commits ni upstream | `M0 D0 ??92` | sin commit inicial |
| zorin-desktop-themes | `/home/mak/Escritorio/zorin-desktop-themes` | `master` | `origin/master` — 0/0 | `M0 D0 ??0` | `1b4c77f4c781` — 2026-03-24 — `Bump to version 5.2.3` |
| zorin-icon-themes | `/home/mak/Escritorio/zorin-icon-themes` | `master` | `origin/master` — 0/0 | `M0 D0 ??0` | `0d9e56a9be0b` — 2026-06-24 — `Bump to version 4.0.8` |

## Frente XIO y relación con FLUJO

- **Separación Git:** `ligereza/flujo` ya está publicado en `main` y la raíz
  contiene `AGENTS.md`, `README.md`, `STATUS.md`, `MAPA.md` y `MIGRATION.md`
  como contrato de entrada. XIO fue excluido físicamente; el puente de datos
  RD queda en `src/flujo/rd/` y la pestaña FOH/ISKVW declara a XIO como
  consumidor externo.
- **Topología remota:** VIBECODEINE conserva `main` como única rama operativa
  permanente y `historia` como referencia histórica. Se retiraron 10 ramas de
  trabajo/checkout (`DIRECTOR`, `FLUJO`, `MAK`, `integration/*`, etc.) después
  de crear tags remotos `archive/legacy-20260914/...` con sus SHAs exactos.
  GitHub muestra además ramas temporales `dependabot/*`, aceptadas por la
  guarda de topología; no son ramas de dominio ni checkouts alternativos.
- **Preservación:** el worktree original de VIBECODEINE fue movido y queda
  intacto en `/home/mak/flujo-vibecodeine-legacy-20260914`, con su rama,
  cambios locales y procedencia. La ruta activa `/home/mak/flujo` ya no es un
  worktree del monorepo.

- **XIO-RD → FLUJO/RD:** `rd_field` usa el catálogo/eventos de la única
  proyección RD canónica del host (`/home/mak/data/rd.db` en esta instalación),
  o una copia de sesión revisada bajo `XIO_RD_PERSIST`. El checkout autónomo de
  FLUJO no versiona ni crea por defecto una segunda SQLite: se configura con
  `FLUJO_RD_DB=/home/mak/data/rd.db`. En FLUJO corresponde al perfil/workspace
  `rd`; no es una escritura directa desde el teléfono ni una conexión implícita
  a la UI.
- **XIO-FOH → FLUJO/ISKVW:** `foh_monitor` usa un contexto VJ de solo lectura
  compuesto desde el read model VJ de FLUJO y las autoridades de portfolio de
  MAK. En FLUJO corresponde al perfil `iskvw`/etiqueta `ISKVW`, cuyas vistas
  incluyen show kit, mapping, Resolume y portfolio.
- **Separación:** RD y FOH son dialectos del mismo runtime XIO, con dominios,
  eventos y persistencias distintas. El contrato FOH no acepta ni escribe
  `eventRef` de RD. La conexión confirmada es de procedencia/contexto y debe
  conservarse como adaptador explícito; no equivale a que XIO controle la
  pestaña de FLUJO directamente.

## Hitos y decisiones actuales

- Se restauró `/home/mak/AGENTS.md` desde la restauración Git `c8937f96`,
  porque `CONTRIBUTING.md`, `MAPA.md` y `DECISIONES.md` lo declaran el
  contrato raíz.
- Se restauró `/home/mak/README.md` exactamente desde `HEAD`, eliminando la
  eliminación local que contradecía la orden activa y la superficie protegida.
- Se corrigió `ORDEN_NOCTURNA_REPOS_20260914.md`: MOSAIK usa
  `/home/mak/mosaik`, KINO es el núcleo integrado en MAT-SI y la rama pública
  de MOSAIK ahora está verificada en `origin`.
- LUCIDA e IRIS ahora resuelven correctamente sus upstream `origin/*`; sus
  fetchspec fueron corregidos para incluir las ramas activas.
- MOSAIK ahora rastrea su rama pública `origin/*`; el remoto
  `windows-bundle` queda como transferencia auxiliar.
- `ml-mobileclip` avanzó por fast-forward de `aecfb545` a `48faa0f` y quedó
  limpio, recibiendo la eliminación remota de `CODE_OF_CONDUCT.md` y
  `CONTRIBUTING.md`.
- Se corrigió el CLI en las superficies `MAK` y `FLUJO`: `doctor` y
  `github-sync --status` resuelven el remoto del upstream actual, incluyendo
  `vibecodeine-legacy`, en vez de exigir el nombre `origin`.
- FLUJO autónomo pasó `1571` pruebas de motor, `30` pruebas de
  higiene, `compileall`, `python -m flujo --help`, `git diff --check`,
  frontend `typecheck` y build Vite. No contiene `xio/`, bases SQLite,
  `context-history`, worktrees de agentes ni secretos versionables.
- La verificación dirigida pasó 26 pruebas en `MAK` y 28 en `FLUJO`; la
  colección completa de pruebas de `MAK` también terminó con código 0.
- `XIO` activo pasó 37 pruebas con `pytest` y las 10 suites directas de
  `showcontrol`, todas con código 0; la verificación es off-device y no cubre
  teléfono, red ni ADB.
- `codex/xio-transport` (`144b2a4461e5`) diverge de la rama activa en
  `58/1` commits y cambia 216 archivos, añadiendo `XIO_LAYER` pero eliminando
  las superficies RD/FOH actuales; queda como candidato para revisión de
  consumidor, no como merge automático.
- La extracción aislada de `codex/xio-transport` pasó 152 pruebas
  `unittest`; sus 13 módulos de prueba validan `XIO_LAYER`, pero la rama no
  contiene las aplicaciones `projects/rd-field` ni `projects/foh-monitor`.
- `codex/xio-interface-layer` pasó 13 pruebas aisladas y conserva solo el
  núcleo mínimo de eventos, snapshots, replay, transporte, acción y auditoría;
  elimina handoff, sesiones y conectividad.
- `codex/xio-lucida-input-contract` (`cd3b4d3aef33`) pasó 179 pruebas
  aisladas y añade `XIO_LAYER/adapters/lucida_input.py`, con resumen acotado y
  redacción para un futuro reducer LUCIDA; tampoco contiene RD/FOH.
- `codex/semantic-light-field` (`6d505cc79662`) pasó 13 pruebas de `pytest` y
  11 directas; ofrece un renderer determinista de propuestas DMX/OSC con
  `proposal_only=true` y `calibration_status=not_calibrated`, sin `XIO_LAYER`.
- `codex/xio-import-review` (`da945d34182b`) pasó 32 pruebas de su superficie
  XIO y 179 de `XIO_LAYER`, pero su worktree `/home/mak/XIO-import-review`
  ya tenía cambios locales; contiene RD y visión, no FOH.
- `XIO/main` no se actualizó: está divergente de `origin/main` en `4/3`
  commits; la rama activa `integration/xio-field-20260911` sigue en `0/0` y
  conserva las aplicaciones actuales.
- `MOSAIK` pasó 299 pruebas, omitió 1 por alcance, validó 47 schemas con 44
  referencias y completó los replays `plugin-bridges` y
  `semantic-light-field` sin efectos externos; `pyserial 3.5` quedó instalado
  desde su requisito declarado.
- `codex/lucida-python-engine` pasó 111 pruebas aisladas. Su reducer produce
  `RenderPlan` y overlay acotado, exige adaptadores explícitos y no ejecuta
  acciones ni abre red, ventanas, Resolume o Adobe.
- `PUPILA` pasó 7 pruebas y el smoke devolvió `CANDIDATES_AVAILABLE → save`
  con `execution=not_performed`; la rama activa quedó en `0/0`.
- `VIZZ` pasó 44 pruebas `unittest` en la rama activa
  `fix/readme-honesty`; la geometría, el gate de medición y la composición
  de contexto conservan el cierre por defecto (`CALIBRATION_REQUIRED` o
  `CALIBRATION_EVIDENCE_REQUIRED`) sin autorizar profundidad métrica. La
  rama está `2/1` frente a `main` y mantiene cambios locales deliberados;
  no se hizo merge.
- `WACHUMA` pasó `pnpm test` y la verificación de release completa con Node
  22: typecheck, lint, 38 tareas de test, build y los 30 gates automatizados
  terminaron en código 0. La política sigue declarando
  `not-ready-for-broad-public-release` por requerir aprobación legal y
  revisión comunitaria; no es un fallo técnico. Se excluyó `.claude/` de
  Git/Prettier para que el worktree legado no contamine el alcance del
  checkout; el directorio físico se conserva sin tocar.
- `IRIS` mantiene el checkout de propuesta separado del runtime IRIS de MAK:
  JSON válido, paquete PDF de 4 páginas y rama `0/0`. Se corrigió la
  referencia de transferencia al HEAD publicado `e4cafd` y se hizo explícita
  la ruta externa del documento canónico de MAK; el expediente queda con
  decisiones de envío pendientes y no se envía nada.
- `bucle` está limpio en `main` `0/0`; sus dos scripts Python compilan y los
  22 SVG existentes pasan análisis XML. No tiene suite automatizada declarada.
- `MAT-SI` está limpio en `main` `0/0`; su suite activa pasó 94 pruebas con
  4 omitidas por fuentes privadas ausentes. KINO está integrado bajo
  `src/matsi/kino/`; no existe un checkout separado que sincronizar.
- `ml-mobileclip` está limpio en `main` `0/0`; se validaron en memoria la
  sintaxis de 26 archivos Python y 25 JSON sin cambiar checkpoints ni
  resultados.
- `mwb-linux` conserva 5 archivos modificados y está `0/2` frente a
  `origin/main`; la suite Go no pudo ejecutarse porque `go` no está instalado
  o disponible en PATH. `XIO-IMPORT` conserva `M41 D1` y está `0/34`; su
  `git diff --check` sigue fallando solo por cambios CRLF/trailing whitespace
  en ese checkout sucio. Ninguno fue reseteado, stasheado o actualizado.
- La auditoría Git final cubre 17 checkouts con `diff --check` limpio y deja
  únicamente `XIO-IMPORT` como excepción de finales de línea. No se hicieron
  commits ni pushes de cambios ajenos; esta fase publicó MAK `d5e2d0d0` en
  `vibecodeine-legacy/main` y FLUJO `d96b9f7` en `origin/main`.
- `FARMAKSIA/codex/iris-farmaksia-integration` validó el adaptador IRIS y su
  contrato; la referencia Node pasó syntax, smoke y regresión tras instalar
  sus dependencias solo en una copia temporal y crear el directorio `work/`.
- `FARMAKSIA/codex/direct-iris-public-scope-20260907` mantuvo el contrato
  IRIS Python y eliminó del alcance público la referencia privada Node y
  WebGazer; el experimento y contrato pasan.
- `mwb-linux` y `XIO-IMPORT` no se actualizaron por tener cambios locales; sus
  divergencias quedan visibles para una intervención posterior con autoridad
  explícita.
- `git diff --check` pasó en 17 checkouts. `XIO-IMPORT` devuelve código 2 por
  finales de línea CRLF interpretados como trailing whitespace en sus cambios;
  al ignorar esos finales, el único cambio de contenido restante es la
  eliminación local de `AGENTS.md`. No se normalizó el checkout sucio.
- En VIBECODEINE se publicó el commit documental `5e61f1a7` y se limpiaron las
  ramas retiradas después de archivarlas por tag. El repo autónomo FLUJO fue
  committeado y publicado; ambos remotos quedaron verificados con sus límites
  explícitos.
