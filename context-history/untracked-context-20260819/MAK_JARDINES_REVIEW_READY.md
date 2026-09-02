# Expediente review_ready: Jardines interpretativos

Estado: `review_ready` como expediente documental interno. No significa
`published`, `submitted` ni `funding_approved`.

## Fuente y procedencia

- Fuente principal: `/home/mak/curatoria_inbox/funding-lab/JARDINES_INTERPRETATIVOS.md`
- Hash verificado: `a35070350df210568c9f33827cbaea4d7768d1582a033cf4fa68c21c285418cc`
- Artifact MAK: `15057` en `/home/mak/flujo/data/mak_knowledge.db`
- Base especializada: `/home/mak/research/jardines_interpretativos/jardines_interpretativos.sqlite`
- Reporte determinista: `/home/mak/research/jardines_interpretativos/JARDINES_INTERPRETATIVOS_RESEARCH.md`
- Reconciliacion: `/home/mak/flujo/context/MAK_JARDINES_RECONCILIATION.md`

## Tesis

Construir un laboratorio que transforme fuentes cientificas, tecnicas o
culturales en interpretaciones visuales, analogicas y generativas. La web
publica es vitrina; la infraestructura privada conserva fuentes, claims,
relaciones, contexto, incertidumbre y resultados.

## Separacion semantica

- `documented_fact`: tesis y afirmaciones explicitamente sostenidas por el
  documento.
- `design_decision`: SQLite, pipeline offline-first, adaptadores de dominio y
  limite entre funding-lab y jardin.
- `hypothesis`: traducciones posibles entre analogia, simulacion y forma
  visual; no son hechos biologicos ni sociales.
- `reference_candidate`: herramienta externa mencionada, aun no dependencia
  aprobada.
- `curatorial_decision`: seleccion posterior; requiere revision humana.

## Modelo de salida

```text
source -> claim -> entity/relation -> context -> interpretation -> state/result
```

Proceso declarado: `discover -> capture -> extract -> normalize -> relate ->
contextualize -> interpret -> simulate -> validate -> curate -> publish ->
audit`.

## Correlaciones principales

- `knowledge_model -> research_pipeline`: claims y procedencia alimentan la
  memoria de investigacion.
- `analogy_interpretation -> garden_simulation`: la analogia se vuelve regla o
  campo, nunca hecho.
- `garden_simulation -> visual_generation`: estados y trayectorias producen
  comportamiento visual.
- `research_pipeline -> reference_tools`: la herramienta se selecciona por
  etapa, entrada, salida, licencia, plataforma y mantenimiento.
- `product_economics -> portfolio_publication`: el dossier y la obra prueban
  una posible oferta, no garantizan financiamiento.

## Herramientas candidatas

Las 12 referencias quedan como candidatas: Algorithmic Botany, GroIMP,
OpenAlea, Recogito, p5.js, Omeka S, Scalar, Gephi, nodegoat, GAMA,
Semantic MediaWiki y Wikidata. No se instalan ni se presentan como usadas.

## Evidencia disponible

- 40 URLs declaradas por la fuente, aun pendientes de captura/verificacion.
- 22 claims en la base especializada.
- 9 entidades y 4 relaciones.
- 12 procesos semanticos.
- 8 restricciones, incluyendo procedencia, punto de quiebre de analogias,
  limites de sustancias y frontera publico/privado.
- Dry-run de router: dominio `plants`, job `planned`, `discover`, 12 pasos,
  borrador JSON/Markdown, `external_calls=0`.
- Gate live: 8900 y 8890 respondieron HTTP 200 en GET-only.

## Pendientes que bloquean publicacion

- Capturar y verificar las URLs oficiales, conservando URL, hash y fecha.
- Extraer claims con evidencia exacta y separar automatico de revisado.
- Elegir una primera herramienta por compatibilidad, licencia y consumidor.
- Definir prototipo visual reproducible y resultado observado.
- Completar presupuesto, FUP, cronograma, colaboraciones y revision humana.

## Decision de integracion

Este expediente se conecta a MAK mediante el router de Research y el gate de
Cultura. No se fusiona la base especializada con `mak_knowledge.db`, no se
copian arboles y no se publica ningun contenido privado.
