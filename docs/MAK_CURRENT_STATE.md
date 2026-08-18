# Estado actual de MAK

> Fuente canónica de orientación para agentes y colaboradores. Leer primero
> `/home/mak/flujo/agents.md`, luego este archivo y finalmente
> `context/LAST_HANDOFF.md`. Verificado el 2026-08-18, tras la auditoría de
> las fases históricas disponibles hasta Phase 570.

Este documento consolida decisiones durables. No reemplaza la evidencia
histórica, no convierte cada experimento en una obligación y no afirma que una
credencial funcione solo porque existe en un archivo de entorno.

## 1. Autoridad y alcance

- MAK es el equipo Linux Debian 12. La autoridad física empieza en
  `/home/mak/*`.
- `/home/mak/flujo` es el baseline de autoría, integración, documentación y
  publicación web.
- `/home/mak/WIN` es archivo histórico de la antigua máquina Windows. Sirve
  para genealogía y recuperación selectiva; no es runtime ni dependencia del
  flujo Linux.
- Git transporta una proyección revisada. No decide por sí solo qué existe en
  MAK ni sustituye la verificación física.
- El README y su obra SVG actual son activos protegidos. No se reescriben como
  parte de una limpieza.
- Los phase files son evidencia de decisiones y pruebas. Este documento es la
  síntesis operativa y tiene precedencia para el trabajo nuevo.

## 2. Interfaces y procesos actuales

| Superficie | Estado | Uso |
|---|---|---|
| `cultura/mak_plataforma/hub.py` | Activa | Interfaz única de MAK en `127.0.0.1:8900`. Agrupa departamentos y rutas. |
| SearXNG local | Activa | Backend de búsqueda en `127.0.0.1:8888`; no es una interfaz adicional de usuario. |
| `python3 -m flujo app/serve` | Portátil/temporal | FLUJO APP offline, con default histórico `8765`; no debe confundirse con el hub MAK ni dejarse como servicio permanente. |
| GitHub Actions runner `mak` | Activo bajo evento | Ejecuta el workflow de eventos cuando llega una orden externa. |
| `tools/route_idea.py` | Activo | Convierte una idea o incidente en un packet mínimo por área, para que un agente externo no tenga que leer todo el repo. |

No hay que abrir puertos adicionales para las herramientas offline. El puerto
8900 es la interfaz local agrupada; el 8888 es una dependencia interna de
research. La ausencia de un listener en 8765 no implica que el código FLUJO
esté roto: es una ruta portátil distinta y se valida bajo demanda.

## 3. Mapa de departamentos y consumidores

| Área | Owner físico principal | Consumidor y contrato |
|---|---|---|
| RD | `RD/`, `src/flujo/`, `data/rd.db` | Eventos, cotizaciones, packs, suplementos, plano/rider, venues y entregables operativos. |
| Portfolio / ISKVW | `web/`, `iskvw/`, `tools/portfolio/` | Obras, archivo público, piezas SVG, vínculos y presentación autoral. |
| Research | `cultura/mak_research/`, `tools/research_job_router.py`, `tools/execute_research_job.py` | Preguntas por dominio, fuentes, claims, relaciones, hashes, licencias y reportes/propuestas. |
| Curatoria | `curatoria/`, `cultura/mak_curatoria/` | Carpetas caóticas -> clasificación, índice, procedencia, triangulación y dossier. |
| Cultura / MAK | `cultura/mak_plataforma/` | Orquestación local, health, gobierno, backlog, entrega y exposición en 8900. |
| Lenguaje / Vigía | `cultura/mak_lenguaje/`, `cultura/mak_vigia/` | Contratos de idioma y vigilancia de convocatorias sin convertir candidatos en hechos. |
| Venue / SCD | `data/venues/`, `tools/venue*.py`, `tools/venue3d_smoke.mjs` | Ficha de venue, geometría, plano visual y demostración 3D. SCD es un demostrador, no un levantamiento técnico certificado. |

RD y Portfolio comparten entidades y procedencia, pero no pierden su
autoridad propia. Cultura puede investigar para cualquiera de los dos; no
debe duplicar sus bases ni asumir que un candidato ya es un dato confirmado.

## 4. Semántica compartida

Las relaciones entre RD, Portfolio, Curatoria, Research y Venue se expresan
con campos estables, no con nombres ambiguos de carpetas:

- `venue_id`: sala, espacio o lugar de trabajo.
- `project_id`: proyecto, evento, obra o propuesta.
- `asset_id`: imagen, video, documento, SVG, blend o evidencia.
- `provenance`: fuente física y cadena de transformación.
- `confidence`: nivel de confirmación del dato.
- `publico`: si puede salir de la superficie privada hacia un producto público.
- `consumer`: qué herramienta realmente lee el dato.

Una relación entre Venue y RD puede alimentar un plano/rider; una relación
entre Venue y Portfolio puede alimentar un portafolio o una propuesta visual;
una relación entre Curatoria y Research puede alimentar un dossier o una
postulación. La relación debe quedar tipada y trazable, no fusionarse por
parecido textual.

## 5. Datos y bases de RD

- `data/rd.db` es el catálogo activo de lectura para reactivos, packs,
  productoras, venues y consultas RD. Es una fuente/proyección delimitada; no
  se fusiona a ciegas con otro SQLite.
- `data/rd_datos.db` es un almacén separado de datos de campo/privacidad y está
  vacío por diseño según la verificación documentada. No se rellena con una
  copia del catálogo.
- `data/venues/*.json` conserva la fuente declarativa de venues y sus esquemas.
  Los índices y HTML son salidas derivadas y regenerables.
- Las memorias, credenciales, exports privados, bases protegidas y productos
  grandes permanecen en su dueño físico. El repo guarda contratos, hashes,
  manifiestos o proyecciones seleccionadas, no copias masivas.

## 6. Workflow de eventos y Blender

La cadena productiva actual es:

```text
correo externo -> issue etiquetado -> runner MAK -> download_post
    -> preservación temprana en OneDrive -> clasificación media
    -> renderer MAK de imagen o video -> publicación en OneDrive
```

El tramo correo -> issue vive fuera del repo. Dentro del repo, el workflow
activo es `.github/workflows/issue_descarga_ig.yml`:

- `image`: `tools/render_flyer_mak.py` y el grafo compartido de
  `src/flujo/eventos/blender_nodes.py`.
- `video`: `tools/render_video_sequence_mak.py` y
  `src/flujo/eventos/blender_nodes_video_seq.py`.
- `carousel`: conserva el comportamiento de imagen/poster; no se inventa un
  render de video múltiple.
- tipo desconocido: falla cerrado; no adivina.

El workflow guarda el MP4, poster, metadata y caption antes de iniciar Blender
y conserva logs, manifest y frames parciales aunque el render falle. El issue
solo se cierra cuando el resultado completo se publica correctamente.

### Política visual permanente

- Imágenes: `fitwidth_fade`, proporción preservada, abertura llena en ancho,
  centrado vertical y fade existente.
- Videos: `cover_center`, proporción preservada, centrado X/Y, sin stretch y
  sin barras negras. Se recorta el eje excedente: laterales si la fuente es
  más ancha que el cristal; arriba/abajo si es más alta.
- La decisión usa las dimensiones reales descargadas, no el nombre del archivo
  ni la suposición de que todo reel es 16:9.
- Video: `/home/mak/RD/AUTOMATIZACION/RD.blend`, Blender
  `/home/mak/blender/blender`, Cycles, 128 samples, GPU obligatoria y
  `render_manifest.json` con proporciones, eje de recorte y dispositivo.
- `glass_fitwidth` conserva el experimento de multiplicación, blur, fade y
  filas tipo glass para material cuadrado/horizontal. Es experimental y no
  reemplaza `cover_center` sin una comparación visual explícita.
- El `.blend` no se guarda durante los renders de validación.

La política completa y sus pruebas están en
`context/VIDEO_WORKFLOW_MAK_20260817.md`.

## 7. Research, APIs y límites

Research separa discovery, captura, evidencia, claims, relaciones y
productos. `tools/interpretive_garden_workflow.py` construye el modelo SQLite
y reportes del laboratorio sin llamar APIs; `research_job_router.py` crea un
job persistente por dominio; `execute_research_job.py` ejecuta una captura
acotada y registra estado, hash, licencia y créditos.

La casa tiene un catálogo de integraciones (modelos, búsqueda, scraping,
GitHub, Instagram metadata, Drive, OneDrive, Watsonx y otras rutas
opcionales). La cantidad de claves no equivale a cantidad de APIs operativas:
cada proveedor debe tener una prueba reciente, un consumer, una política de
costo y una salida registrada en el handoff. Una key nunca se copia a Git ni
se imprime en un reporte. Cerebras quedó observado con HTTP 402; los
proveedores retirados por decisión del usuario no se presentan como activos.

Firecrawl/Crawl4AI/SearXNG son herramientas de captura/búsqueda, no fuentes de
verdad. El resultado debe separar fuente oficial, candidato, claim, relación,
fecha, licencia y confianza. Un research puede terminar en informe o borrador
de propuesta, pero una propuesta sigue siendo un producto revisable, no una
escritura automática sobre RD o Portfolio.

## 8. Superficies históricas y exclusiones

Estas rutas se conservan para evidencia, recuperación o uso manual acotado,
pero no son llamadas por el workflow Linux nuevo:

- `src/flujo/eventos/flyer_auto.py`: legado con supuestos Windows/Droplet y
  todavía expuesto por un comando CLI histórico; no borrarlo sin una fase de
  compatibilidad propia.
- `tools/bridge_issue_render.py`: puente Windows antiguo, manual-only.
- `tools/render_video_rd.py`: ruta H264 manual sobre
  `RD.paravideo.blend`, manual-only; no es el renderer de secuencia MAK.
- `RD.paravideo.blend` y cualquier MP4 histórico: evidencia, no input actual.
- `/home/mak/WIN`: archivo histórico completo, no dependencia de runtime.
- `n8n` y `XIO`: fuera del objetivo operativo actual por decisión del usuario.

La existencia de una herramienta legacy no significa que esté rota; significa
que no debe confundirse con el consumidor actual. Cualquier futura eliminación
requiere demostrar imports, entrypoints, tests, consumidores y rollback.

## 9. Git y publicación web

- `main` es la única rama permanente y el tronco de publicación.
- `archive/house-history` es el único tag de preservación de la topología
  histórica.
- Las ramas de tema son opcionales y cortas (`rd/*`, `portfolio/*`, `mak/*`,
  `tools/*` o `cleanup/*`); se eliminan después de promover a `main`.
- No se crean ramas permanentes por departamento, `source/*`, `work/*`,
  `develop`, `staging` ni release branches.
- Cada cambio debe tener un consumidor, write set acotado, prueba foreground y
  rollback. Se hace `git add` explícito; no se publica un árbol completo por
  accidente.
- Un agente externo puede empezar leyendo solo `agents.md`, este documento,
  `context/OWNER_MANIFEST.md` y el packet producido por `tools/route_idea.py`.
  Luego lee únicamente el handoff o contrato del área que va a tocar.

## 10. Qué se aprendió de las fases históricas

La genealogía completa queda respaldada en `context/PHASE*.md/.csv` y en el
handoff. Sus conclusiones durables se pueden entender por familias:

| Familia | Decisión durable |
|---|---|
| Inventario y genealogía | La autoridad es física (`/home/mak/*`); WIN es historia; Git es transporte. |
| Crosswalk WIN -> MAK | Solo se migra un slice vertical con consumidor real; no se copia un árbol ni se convierte una idea en integración. |
| Ownership y semántica | Cada herramienta tiene owner, consumidor, dependencia, idioma, plataforma, procedencia y estado. |
| RD y datos | `rd.db`, `rd_datos.db`, venues y productos derivados tienen límites distintos; el almacén vacío no se rellena por conveniencia. |
| Research y Curatoria | Discovery, captura, triangulación, claims y propuestas son pasos separados; candidatos no son hechos. |
| Portfolio y Venue | Venue puede unir RD y Portfolio; SCD es una demostración geométrica y no sustituye una ficha técnica certificada. |
| Salud y limpieza | Se valida antes de mover/borrar; basura confirmada se cuarentena de forma reversible; evidencia no se elimina. |
| Git | Se consolidó una sola `main` y un tag histórico; no se conserva un bosque de ramas. |
| Eventos y video | El camino Linux MAK quedó separado de WIN, con preservación temprana, clasificación image/video y composición por proporción. |
| APIs y costo | Una API solo se declara operativa con consumer y prueba reciente; las claves y servicios no son evidencia suficiente. |

## 11. Pendientes reales, sin reabrir lo cerrado

1. Observar un issue real nuevo para confirmar en Actions la preservación
   temprana y la publicación en OneDrive; no inventar ese resultado en local.
2. Ejecutar, cuando corresponda, un smoke acotado de `layout` en un video real
   y revisar su manifest antes de renderizar una secuencia completa.
3. Mantener la matriz de proveedores del handoff actualizada con pruebas,
   costos y fallos; no reactivar proveedores retirados.
4. Hacer una fase separada para retirar o cuarentenar rutas legacy solo si se
   demuestra que no tienen consumidores legítimos.
5. Revisar dominio/hosting del Portfolio en una tarea aparte; no mezclarlo con
   el runtime local ni con el catálogo RD.

El siguiente trabajo seguro por defecto es el punto 1 o un nuevo packet de
idea generado por `tools/route_idea.py`. No hay que volver a leer las 600
fases para cada cambio: esta síntesis, el owner manifest y la evidencia
acotada del área son suficientes.

## Referencias canónicas

- `agents.md`
- `context/LAST_HANDOFF.md`
- `context/OWNER_MANIFEST.md`
- `context/VIDEO_WORKFLOW_MAK_20260817.md`
- `CAPACIDADES.md`
- `MAPA.md`
- `context/PHASE209_FINAL_MAK_ARCHITECTURE_DISPOSITION.md`
- `context/PHASE413_CROSS_DOMAIN_SERVICE_ARCHITECTURE.md`
- sección `Historical checkpoint — Phase 495` y fases posteriores en
  `context/LAST_HANDOFF.md`
