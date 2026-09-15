# STATUS

Snapshot vivo de coordinación y mantenimiento de `LIBELULA`, director de
moscas. Este archivo se reescribe completo: no es una bitácora ni acumula
historia.

## Coordinación actual

- **Responsable:** `LIBELULA`
- **Fase:** auditoría y preparación del frente de Deep Learning para IRIS/
  Portafolio, sobre la integración ya verificada de MAK, FLUJO y XIO. El
  corpus del usuario es la entrada explícita; IRIS ordena, relaciona y
  propone formatos propios del artista, sin inferir autoría ni buscar una
  precisión universal. FLUJO es autónomo; XIO sigue siendo externo:
  XIO-RD consume la única proyección RD del host y XIO-FOH consume el contexto
  VJ/portfolio de `iskvw`/ISKVW en solo lectura.
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
- **Última actualización:** `2026-09-15T11:36:21-03:00`

## Orden operativo vigente

1. `FLUJO` autónomo (`/home/mak/flujo`) y su frontera con XIO/MAK.
2. `XIO` (`/home/mak/XIO`) y la procedencia auxiliar `XIO-IMPORT`.
3. `MAK` (`/home/mak`) y su historia VIBECODEINE, sólo como estación y
   consumidor de los dos frentes anteriores.
4. Auditoría de fuentes hermanas: `X-ANA-X`, `LUCIDA`, `PUPILA`, `FARMAKSIA`,
   `VIZZ`, `WACHUMA`, `IRIS`, `MAT-SI` y `MOSAIK`.
5. Portar únicamente una mejora que tenga consumidor explícito en FLUJO o
   XIO; los demás repos quedan fuera del alcance activo.

Este corte se recalculó después de `git fetch --all` en los checkouts con
remoto. No se hizo fast-forward, reset, merge ni sobrescritura; los cambios
locales y las divergencias quedan visibles para una decisión posterior.

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
- **Auditoría del Hub — redundancias candidatas:** `jobs` se solapa
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
- **Corrección aplicada:** el contrato compartido de estado prioriza
  `/home/mak/.cache/mak/research.sock` y
  `/home/mak/.cache/mak/codex.sock`, etiqueta ambos consumidores sin puertos
  retirados y conserva TCP solo como fallback explícito de ejecución aislada.
  Se actualizó el espejo usado por el Hub y el checkout autónomo de FLUJO; se
  reinició solo `mak-hub.service` y la regresión dirigida del Hub, salud y
  contrato de estado cerró en `29 passed`.
- **Navegación simplificada:** la barra principal conserva cinco superficies
  de uso frecuente —Research, jardines/jobs, Codex, Ideas y Portafolio— y
  agrupa en `más` las cinco superficies operativas restantes y los seis
  recursos de soporte. La prueba real confirmó apertura, selección, cierre del
  menú y retorno a Research; la regresión del Hub quedó en `29 passed`.

## Frente Deep Learning / IRIS — medición actual

- **Estado de la línea:** `deep_learning_micelio` está en `partial`; su
  siguiente gate exige un holdout independiente para `logo-clean` y ejecutar
  su validador. La compuerta mantiene `training_permitted=false`, incluso si
  una tarea resulta elegible.
- **Cómputo disponible:** MAK tiene una NVIDIA GeForce GTX 1650 de 4 GB;
  PyTorch con CUDA está disponible en `/home/mak/.venv` (`2.13.0+cu130`) y en
  el runtime de Plataforma (`2.14.0+cu130`). Esto permite inferencia local y
  experimentos pequeños/adaptadores, no entrenamiento grande ni cómodo desde
  cero.
- **MobileCLIP:** `/home/mak/models/mobileclip/mobileclip_s0.pt` existe, pesa
  `215934653` bytes y su hash coincide con el índice. El código fuente
  upstream está limpio en `/home/mak/src/ml-mobileclip` (`main`, commit
  `48faa0f`). El checkpoint es legible por PyTorch. El entorno dedicado
  `/home/mak/venvs/visual-index-pilot` tiene `mobileclip`, `open_clip`,
  `faiss-cpu` y CUDA; una prueba real cargó el encoder, generó un vector de
  512 dimensiones y leyó el índice de 100 unidades. El runtime de
  Plataforma/Hub no tiene esas dependencias pesadas: el builder no debe
  ejecutarse desde el servicio web, sino desde ese worker explícito.
- **Índice visual existente:** el índice FAISS/JSON fue generado el
  `2026-08-10` con `MobileCLIP-S0`, 512 dimensiones, `100` unidades, `345`
  vecinos elegibles y `455` abstenciones. Cubre una selección histórica de
  Instagram (`213` medios), no los `7044` elementos del inbox actual; el
  worker puede regenerarlo, pero debe tratarse como proyección derivada y
  vencida hasta refrescarlo con un snapshot actual.
- **Micelio textual:** el índice local tiene `5809` chunks, `1911` rutas y
  vectores Nomic de `768` dimensiones. Ollama responde localmente con
  `nomic-embed-text:latest`. Es recuperación semántica/RAG e inferencia de
  embeddings congelados: no hay entrenamiento de IRIS ni conexión actual que
  fusione esos vectores con el re-ranking del copilot.
- **Señal humana disponible:** el audit del Portafolio registra `137` etiquetas
  de triage (`33 work`, `32 record`, `1 review`, `71 discard`) y `6907` piezas
  aún sin etiqueta; hay `20` feedbacks de relaciones, ninguno visual. El
  baseline estructural de IRIS obtiene `0.518248` de accuracy y `0.25` de
  macro-recall, por lo que la automatización sigue desactivada.
- **Aprendizaje existente fuera de Deep Learning:** FLUJO compila `12`
  episodios verificados y produjo un candidato Naive Bayes con `6` ejemplos
  de train y `6` de holdout (`1.0` frente a baseline `0.833333`). Es una
  política categórica de enrutamiento, no un modelo neuronal de imágenes ni
  del portafolio.
- **Dataset real:** `projects/logo_clean_lab/learning/mini_dataset.jsonl`
  valida `3` casos de demostración (`2` aprobados, `1` rechazado), pero no
  existe todavía `logo_clean_results.jsonl`, un manifiesto de tarea real,
  train/holdout ni un modelo ajustado al usuario.

## Condiciones pendientes para trabajar limpio

- **P0 — una sola autoridad de FLUJO:** resuelto para el runtime: el Hub ahora
  prefiere `/home/mak/flujo/src` y solo deja `/home/mak/src/flujo` como fallback
  explícito. El checkout autónomo superó el smoke de MAK con `53 passed` y las
  rutas RD, ISKVW, Research, Portafolio y Codex respondieron `200`. El espejo
  MAK sigue existiendo y difiere en 44 archivos; queda pendiente retirarlo o
  convertirlo en una sincronización declarada.
- **P0 — clasificar MAK:** `/home/mak` tiene `M112 D0 ??80`. No se debe hacer
  otro commit global: tras las exclusiones locales aún tiene `M112 D0 ??80`;
  hay que separar cambios de Hub/MAK, documentación, datos, el árbol XIO
  legado y residuos de worktrees; después se puede publicar por lotes
  coherentes.
- **P0 — duplicado XIO dentro de MAK:** `/home/mak/xio` conserva 160 archivos
  rastreados y 151 elementos locales, mientras `/home/mak/XIO` es el checkout
  externo activo. La decisión operativa es usar `/home/mak/XIO` como única
  fuente de XIO. Todos los paths rastreados del árbol legado existen afuera;
  17 contenidos difieren y deben conservarse/portarse antes de retirar ese
  árbol de MAK.
- **P1 — XIO activo:** resuelto en Git: `integration/xio-field-20260911` está
  `0/0` con su upstream, el contrato de entrada está restaurado, los datos y
  configs runtime quedaron ignorados y los commits `8373940`, `802ea7e` y
  `6e8fa28` están publicados.
- **P1 — política de ramas XIO:** RD y FOH/ISKVW no son ramas separadas hoy;
  son namespaces/plugins (`rd_field` y `foh_monitor`) dentro de la rama de
  integración activa, ahora declarada como canónica. `main` está divergente
  `4/3` y varias ramas `codex/*` son snapshots parciales; queda revisarlas
  antes de archivarlas o integrar una por un consumidor verificable.
- **P1 — contrato ejecutable RD/FOH:** la separación semántica está probada
  off-device —RD usa `eventRef`, FOH usa `eventKey`— y cada modo respondió en
  su superficie. El preflight ya descubre ADB en Linux, pero devuelve `NO-GO`
  porque el dispositivo `8299e66f` no está conectado; siguen pendientes
  teléfono, red, ADB operativo y reconciliación post-show.
- **P2 — estado operativo:** MAK Hub, Research y Codex están activos; `cola`
  y `xio_monitor` no están ejecutándose. Hay que decidir si son opcionales o
  parte del baseline, para que `attention` no mezcle fallas reales con
  servicios deliberadamente apagados.
- **P1 — fuentes hermanas auditadas sin integración:** `X-ANA-X` está limpio
  en `LUCIDA` (`0619057`) y conserva `main`, `PUPILA`, `FARMAKSIA` y `LUCIDA`
  como ramas de dominio. `PUPILA` está limpio y pasa 7 pruebas; `LUCIDA` es
  un checkout documental limpio cuyo código canónico está en
  `X-ANA-X/LUCIDA`; `FARMAKSIA` está limpio, pero su suite se detiene en el
  experimento 039 por `cv2` ausente. No se detectó conflicto con FLUJO o XIO.
- **P1 — alcance de transferencia:** esas fuentes no son consumidores activos
  de MAK. Una mejora sólo se podrá portar a FLUJO o XIO cuando exista un
  contrato de destino, un commit de origen y una prueba reproducible. No se
  copia `X-ANA-X`, `LUCIDA`, `PUPILA`, `FARMAKSIA`, `MAT-SI` o `WACHUMA` dentro
  de MAK para “conectarlos”.
- **P1 — Hub/Portafolio mejorado:** la vista general ahora cachea por firma de
  fuentes, el inbox serializa sus lecturas concurrentes, los errores de inbox
  exponen un HTTP visible, la entrega de media cierra correctamente sus
  archivos y el editor coalesce peticiones simultáneas. Se retiró texto
  repetido de la cabecera y el contrato sin proyecto de evidencia responde
  `200` como `unbound`, en vez de `503`.
- **P1 — Portafolio/IRIS conectado:** el inbox expone `faro-portfolio-corpus-
  context-v1`: el `artist_id` sólo aparece cuando lo declara el operador, el
  `corpus_id` es estable y la pertenencia al corpus no equivale a autoría. Se
  preservan `relative_path`, carpeta y subcarpetas. Las sugerencias de
  Research se rankean sólo con relaciones humanas confirmadas y quedan como
  `candidate_only`; el mapa heredado reutiliza el GTM real y dejó de llamar a
  una ruta 404. `POST /api/portfolio/dispatch` ahora crea un plan Research
  enlazado por `job_relations` en la SQLite existente o encola Codex en la
  cola existente, manteniendo `promotion=false` y la compuerta humana.
- **P1 — importación de carpetas arbitrarias:** resuelto el corte de conexión:
  `cultura/mak_plataforma/portfolio_corpus.py` reutiliza
  `flujo.knowledge.archive_observer` y `POST /api/portfolio/observe-folder`
  ofrece vista previa por defecto o activación explícita. Convierte los
  archivos observados al inbox de IRIS, conserva rutas, carpetas, subcarpetas,
  hashes y snapshot, sirve la media desde el `asset_root` declarado y deja
  una copia recuperable del inbox anterior. No copia ni modifica la carpeta
  fuente, no asigna autoría y no reemplaza el corpus actual sin `activate=true`.
  Queda como mejora de interfaz añadir un selector de carpeta al panel activo;
  el contrato HTTP ya está listo y probado.
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
- **Puente Portafolio → MICELIO:** un plan Research conserva `source_id`,
  `corpus_id` y procedencia en `job_relations`; los jobs de Research/Codex
  también reciben el sobre `portfolio_source`. El reindexado de resultados
  sigue siendo posterior al resultado real, nunca una inferencia adelantada.
- **FLUJO Hub:** con `FLUJO_RD_DB=/home/mak/data/rd.db`, `:8765` respondió 200
  en ping, RD summary/topics/read-only-context, RD panel, VJ events,
  dashboard y SVG. El read model VJ regenerable quedó construido con 7
  eventos, 3 venues y 21 productoras.
- **XIO:** smoke real local del runtime `xio/new/server.py` en modos separados:
  `rd` cargó `rd_field` y respondió `200` con 42 eventos del host; `foh` cargó
  `foh_monitor` y respondió `200` con 10 eventos VJ. No se levantaron ambos
  dueños en el mismo proceso. La suite XIO dio `37 passed` y las 10 suites
  directas de `showcontrol` dieron `69 passed`; el launcher de host ya no busca
  una DB inexistente dentro del checkout autónomo FLUJO.
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
| MAK | `/home/mak` | `main` | `vibecodeine-legacy/main` — 0/0 | `M112 D0 ??80` | `a04f7a65` — `feat(portfolio): connect IRIS corpus and research bridges` |
| FLUJO autónomo | `/home/mak/flujo` | `main` | `origin/main` → `ligereza/flujo` — 0/0 | limpio | `fa1eeca` — `fix(portfolio): represent unbound evidence plans` |
| FLUJO worktree legado preservado | `/home/mak/flujo-vibecodeine-legacy-20260914` | `integration/flujo-canonical-20260911` | upstream remoto archivado/desaparecido | `M57 D0 ??31` | `f2d08916f823` — 2026-09-12 — `fix(rd): guard complete database reproducibility` |
| XIO | `/home/mak/XIO` | `integration/xio-field-20260911` | `origin/integration/xio-field-20260911` — 0/0 | limpio | `6e8fa28` — `fix(xio): discover adb on the local host` |
| X-ANA-X | `/home/mak/X-ANA-X` | `LUCIDA` | `origin/LUCIDA` — 0/0 | limpio | `0619057` — `normalize integrated surface identifiers` |
| FARMAKSIA | `/home/mak/FARMAKSIA` | `fix/provenance-integrity` | `origin/fix/provenance-integrity` — 0/0 | `M0 D0 ??0` | `41b2ce8` — `define FARMAKSIA research-only boundary` |
| VIZZ | `/home/mak/VIZZ` | `fix/readme-honesty` | `origin/fix/readme-honesty` — 0/0 | `M5 D0 ??7` | `0e72bf0a4636` — 2026-09-07 — `docs: leave a NEXT.md with open work, observations and what was not audited` |
| PUPILA | `/home/mak/PUPILA` | `fix/ambiguity-consistency` | `origin/fix/ambiguity-consistency` — 0/0 | `M0 D0 ??0` | `5bf9cc6` — `route research output to PUPILA` |
| LUCIDA | `/home/mak/LUCIDA` | `docs/next` | `origin/docs/next` — 0/0 | `M0 D0 ??0` | `ca4e1dc` — `route research output to LUCIDA` |
| IRIS | `/home/mak/IRIS` | `postulacion/fondart-regional-2027` | `origin/postulacion/fondart-regional-2027` — 0/0 | `M3 D0 ??0` | `e4cafd9887ff` — 2026-09-08 — `docs(iris): add a technical transfer note for the published commit` |
| WACHUMA | `/home/mak/WACHUMA` | `postulacion/fondart-investigacion-2027` | `origin/postulacion/fondart-investigacion-2027` — 0/0 | `M2 D0 ??0` | `4507a29b75cf` — 2026-09-08 — `docs(wachuma): point the transfer note at the commit it actually describes` |
| MOSAIK | `/home/mak/mosaik` | `codex/obras-experimental-rehearsal-mosaik-root` | `origin/codex/obras-experimental-rehearsal-mosaik-root` — 0/0 | `M4 D0 ??1` | `1ab2076cbfb6` — 2026-09-08 — `feat: project semantic lighting to Resolume and Titan` |
| MAT-SI | `/home/mak/MAT-SI` → `/home/mak/Escritorio/MAT-SI` | `main` | `origin/main` — 0/0 | `M0 D0 ??0` | `f7cf473b58e7` — 2026-09-14 — `integrate selective KINO research into MAT-SI` |
| mwb-linux | `/home/mak/src/mwb-linux` | `main` | `origin/main` — 0/2 | `M5 D0 ??0` | `6c3fab3a34f9` — 2026-08-03 — `build(deps): bump actions/setup-go from 6 to 7 (#38)` |
| ml-mobileclip | `/home/mak/src/ml-mobileclip` | `main` | `origin/main` — 0/0 | `M0 D0 ??0` | `48faa0fea4b0` — 2026-09-11 — `Update root files` |
| XIO-IMPORT | `/home/mak/curatoria_inbox/XIO-IMPORT` | `integration/xio-field-20260911` | `origin/integration/xio-field-20260911` — 0/35 | `M41 D1 ??0` | `42495e76512d` — 2026-09-11 — `Initialize RD operational schema for XIO bridge` |
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

## Decisiones vigentes

- MAK/VIBECODEINE conserva `main` como rama operativa única; FLUJO es un
  repositorio autónomo en `main`, sin relación de worktree activo con MAK.
- El Hub publica una sola cara TCP en `127.0.0.1:8900`. Research y Codex son
  consumidores internos por sockets Unix privados; `8890/8891` no son puertos
  activos de la instalación persistente.
- RD e ISKVW son perfiles de aplicación, no ramas Git. XIO-RD consume la
  proyección RD canónica `/home/mak/data/rd.db`; XIO-FOH consume el contexto
  VJ/portfolio de ISKVW en solo lectura.
- El worktree legado `/home/mak/flujo-vibecodeine-legacy-20260914` se conserva
  como procedencia y no se actualizará automáticamente; su upstream remoto fue
  archivado.
- `mwb-linux` y `XIO-IMPORT` mantienen cambios locales o divergencias, por lo
  que no se actualizaron durante este corte. `XIO-IMPORT` queda 35 commits
  detrás de su upstream y conserva la excepción CRLF de `diff --check`.
- La simplificación del Hub y el detector de sockets siguen publicados; el
  último endurecimiento del Portafolio quedó en MAK `a04f7a65` y la corrección
  de planes sin proyecto en FLUJO `fa1eeca`; ambas ramas remotas están
  sincronizadas.
