# Research y workflow: Jardines interpretativos

> Fuente analizada: `/home/mak/curatoria_inbox/funding-lab/JARDINES_INTERPRETATIVOS.md`
> Generado: `2026-08-17T05:17:51+00:00` | schema `1.0` | SHA-256 `a35070350df210568c9f33827cbaea4d7768d1582a033cf4fa68c21c285418cc`

## Resultado ejecutivo

Jardines interpretativos no debe implementarse como otra wiki, otro dashboard ni un chatbot de resumen. Su unidad de valor es una cadena trazable que convierte una fuente especializada en una interpretacion visual o generativa, declarando que es evidencia, que es inferencia, que es metafora y que fue decidido por curaduria.

La arquitectura recomendada es un laboratorio local offline-first con SQLite como registro de procedencia, un pipeline por etapas y salidas separadas. La web y las piezas visuales consumen derivados validados; no son la base de verdad.

## Separacion de temas

| Tema | Funcion | No confundir con | Salida principal |
|---|---|---|---|
| `core_thesis` | Tesis y posicionamiento | Laboratorio de traduccion entre conocimiento y experiencia. | registros y decisiones del tema |
| `knowledge_model` | Modelo de conocimiento | Fuentes, claims, entidades, relaciones y procedencia. | registros y decisiones del tema |
| `analogy_interpretation` | Analogia e interpretacion | Correspondencia, lectura, quiebre y limites. | registros y decisiones del tema |
| `garden_simulation` | Simulacion de jardin | Reglas, semillas, ambiente, estados y trayectorias. | registros y decisiones del tema |
| `domain_adapters` | Adaptadores de dominio | Plantas, alimentos y sustancias como dominios diferenciados. | registros y decisiones del tema |
| `research_pipeline` | Pipeline de investigacion | Idea, precedentes, herramientas, prototipo, resultado y obra. | registros y decisiones del tema |
| `visual_generation` | Generacion visual | SVG, imagen, animacion, 3D, simulacion y web. | registros y decisiones del tema |
| `reference_tools` | Mapa de herramientas | Herramientas externas clasificadas por funcion, no por moda. | registros y decisiones del tema |
| `risks_ethics` | Riesgos y etica | Incertidumbre, danos, licencias, opacidad y limites de uso. | registros y decisiones del tema |
| `product_economics` | Producto y economia | Servicios, subvenciones, residencias, mantenimiento y obra. | registros y decisiones del tema |
| `portfolio_publication` | Portafolio y publicacion | Evidencia publica, pieza, dossier y trazabilidad. | registros y decisiones del tema |
| `existing_funding_lab` | Funding lab separado | Consumidor adyacente de reglas y ledgers; no es parte del jardin. | registros y decisiones del tema |

### Limite importante: funding-lab

`funding-lab` queda como consumidor adyacente. Su torneo de hipotesis, reglas deterministas y ledger pueden reutilizar el contrato de `source`, `claim`, `method`, `constraint` y `result`, pero no se fusiona semánticamente con plantas, analogias o generacion visual. Esta separacion evita que una logica financiera de papel sea interpretada como conocimiento cultural.

## Semantica por proceso

| Proceso | Entrada | Salida | Tipo | Regla |
|---|---|---|---|---|
| `discover` (descubrir) | idea o pregunta | candidates | `candidate` | No afirmar existencia; registrar consulta y cobertura. |
| `capture` (capturar) | URL o archivo | source_snapshot | `source` | Conservar URL, hash, fecha y tipo de fuente. |
| `extract` (extraer) | fuente capturada | claims, entities, citations | `extracted_fact` | Marcar automatico y guardar evidencia exacta. |
| `normalize` (normalizar) | entidad o termino | canonical entity | `canonical_entity` | No inferir significado por similitud nominal. |
| `relate` (relacionar) | entidades + evidencia | typed relation | `inferred_relation` | Toda relacion necesita base, confianza y fuente. |
| `contextualize` (contextualizar) | relacion + tiempo/lugar/dominio | context | `contextualized_claim` | Separar el contexto de la interpretacion. |
| `interpret` (interpretar) | contexto + correspondencia | interpretation hypothesis | `hypothesis_or_metaphor` | Declarar correspondencia, quiebre y no-equivalencia. |
| `simulate` (simular) | reglas + semilla + ambiente | states and trajectories | `observed_model_result` | El comportamiento del modelo no prueba el mundo real. |
| `validate` (validar) | claim, relation o experimento | decision | `validated_or_uncertain` | Usar pass, fail o uncertain; nunca completar vacios con prosa. |
| `curate` (curar) | material validado o incierto | selection and decision | `curatorial_decision` | La seleccion humana queda separada de la extraccion automatica. |
| `publish` (publicar) | seleccion + assets | public work or dossier | `published_artifact` | Publicar evidencia suficiente sin exponer secretos ni datos privados. |
| `audit` (auditar) | todos los eventos | provenance ledger | `audit_event` | Cada salida debe poder volver a fuente, proceso y version. |

## Correlaciones operativas

Las correlaciones no significan que dos temas sean iguales. Son rutas de trabajo que deben conservar fundamento y confianza.

| Desde | Hacia | Relacion | Base | Confianza |
|---|---|---|---|---:|
| `knowledge_model` | `research_pipeline` | `feeds` | claims and provenance become the memory of research | 0.98 |
| `analogy_interpretation` | `garden_simulation` | `maps_to` | an analogy can become a rule or field, never a fact | 0.95 |
| `garden_simulation` | `visual_generation` | `drives` | states and trajectories become visual behavior | 0.92 |
| `research_pipeline` | `reference_tools` | `selects` | tools are selected by pipeline stage and constraints | 0.93 |
| `risks_ethics` | `domain_adapters` | `constrains` | the substance domain requires hard safety and non-operationalization rules | 0.99 |
| `product_economics` | `portfolio_publication` | `proves` | public work and dossier provide evidence of a service | 0.84 |
| `portfolio_publication` | `visual_generation` | `exposes` | the portfolio presents the result, not the entire private corpus | 0.89 |
| `existing_funding_lab` | `research_pipeline` | `consumes` | funding-lab demonstrates deterministic rules and ledgers but stays separate | 0.81 |
| `domain_adapters` | `knowledge_model` | `instantiates` | plant, food and substance domains share a schema but retain local constraints | 0.91 |
| `analogy_interpretation` | `risks_ethics` | `limits` | metaphor needs a declared break point to avoid false equivalence | 0.96 |

## Modelo de datos

La base SQLite contiene `documents`, `sources`, `topics`, `claims`, `entities`, `relations`, `contexts`, `interpretations`, `states`, `results`, `tools`, `process_semantics`, `correlations`, `constraints`, `experiments` y `audit_events`. La forma minima de una afirmacion es:

```text
source -> claim -> entity/relation -> context -> interpretation -> state/result
```

El campo `kind` de `claims` es obligatorio: `documented_fact`, `design_decision` o `hypothesis`. El workflow puede ampliar luego a `automatic_extraction`, `inferred_relation`, `metaphor`, `curatorial_decision` y `observed_result` sin perder compatibilidad.

## Herramientas: como entran al sistema

Las referencias del documento quedan registradas como candidatos, no como dependencias instaladas. La seleccion real se hace por etapa, entrada, salida, licencia, plataforma, mantenimiento y restriccion. En esta primera corrida se conservaron todas las URLs declaradas para no perder genealogia.

| Familia | Herramienta | Uso posible | Estado |
|---|---|---|---|
| `annotation` | Recogito | annotation and entity linking | `reference_candidate` |
| `botanical_modeling` | Algorithmic Botany | plant modeling and visualization | `reference_candidate` |
| `botanical_modeling` | GroIMP | rule-based 3D plant modeling | `reference_candidate` |
| `botanical_modeling` | OpenAlea | plant architecture analysis | `reference_candidate` |
| `creative_coding` | p5.js | browser visual prototyping | `reference_candidate` |
| `digital_collections` | Omeka S | collection and API layer | `reference_candidate` |
| `digital_publication` | Scalar | nonlinear publication | `reference_candidate` |
| `graph_visualization` | Gephi | network exploration | `reference_candidate` |
| `research_database` | nodegoat | research data modeling | `reference_candidate` |
| `simulation` | GAMA | agent-based simulation | `reference_candidate` |
| `structured_knowledge` | Semantic MediaWiki | semantic page annotations | `reference_candidate` |
| `structured_knowledge` | Wikidata | structured multilingual reference | `reference_candidate` |

## Contratos de seguridad y calidad

- **evidence_levels** (`global`, `high`): Documented fact, automatic extraction, inferred relation, hypothesis, metaphor, curatorial decision and observed result are different types.
- **analogy_break_point** (`interpretation`, `high`): Every analogy declares correspondence, interpretation, break point, sources and uncertainty.
- **substance_harm** (`domain_adapters`, `critical`): Research about drugs or substances must not operationalize, normalize or optimize harmful use.
- **provenance_required** (`global`, `high`): Claims and relations without source or explicit status remain uncertain.
- **model_is_not_reality** (`garden_simulation`, `high`): A generative garden is a model of relations, not evidence of biological or social reality.
- **license_boundary** (`reference_tools`, `high`): A tool is a candidate until license, maintenance, platform and data restrictions are checked.
- **public_private_boundary** (`portfolio_publication`, `high`): Public outputs are derived artifacts; private raw sources and credentials stay outside publication.
- **funding_lab_boundary** (`existing_funding_lab`, `medium`): The paper trading/funding experiment is an adjacent consumer, not a semantic merge with cultural interpretation.

## Verificacion externa inicial

La revision web se limita a paginas oficiales o documentacion de cada proyecto. Esto confirma el rol declarado de la referencia, pero no autoriza instalarla ni la convierte en dependencia de MAK.

| Referencia | Hallazgo | Estado | Fuente |
|---|---|---|---|
| Algorithmic Botany | Su grupo declara como foco el modelado, la simulacion y la visualizacion de plantas, junto con herramientas para experimentos simulados. | `official_page_reviewed` | https://algorithmicbotany.org/ |
| OpenAlea | La documentacion lo presenta como proyecto open source para investigacion de plantas, con bibliotecas para analizar, visualizar y modelar arquitectura y crecimiento. | `official_docs_reviewed` | https://openalea.readthedocs.io/en/latest/ |
| Wikidata | Es una base secundaria, libre, colaborativa, multilingue y estructurada; registra afirmaciones, fuentes y conexiones con otras bases. | `official_page_reviewed` | https://www.wikidata.org/wiki/Wikidata:Introduction |
| Semantic MediaWiki | Agrega anotaciones semanticas a una wiki para buscar, organizar, consultar y reutilizar contenido como una base de datos colaborativa. | `official_docs_reviewed` | https://www.semantic-mediawiki.org/wiki/Help:Introduction_to_Semantic_MediaWiki |
| nodegoat | Se presenta como entorno web de investigacion para humanidades, con modelado propio, visualizaciones espacio-temporales y analisis de redes. | `official_page_reviewed` | https://nodegoat.net/ |
| Omeka S | Su API ofrece operaciones de busqueda, lectura, creacion, actualizacion y eliminacion sobre recursos; por eso requiere una frontera explicita entre lecturas y mutaciones. | `official_docs_reviewed` | https://omeka.org/s/docs/developer/api/ |
| Gephi | Es software libre y open source para explorar y manipular redes; sirve como referencia de visualizacion, no como base primaria de claims. | `official_page_reviewed` | https://gephi.org/ |

## Workflow recomendado

1. `discover`: recibir una idea y registrar consultas sin afirmar resultados.
2. `capture`: guardar URL/archivo, fecha, hash y tipo de fuente.
3. `extract`: separar claims, entidades y citas; cada extraccion conserva su evidencia.
4. `normalize`: unificar nombres e identificadores sin inferir significado.
5. `relate`: proponer relaciones tipadas con fundamento y confianza.
6. `contextualize`: agregar tiempo, lugar, dominio y escala.
7. `interpret`: formular analogia o hipotesis con correspondencia y punto de quiebre.
8. `simulate`: convertir reglas y estados en trayectoria visual; registrar que es modelo.
9. `validate`: aceptar, rechazar o dejar incierto; no rellenar vacios.
10. `curate`: seleccionar lo que entra en una obra, dossier o propuesta.
11. `publish`: exportar una pieza o portafolio derivado, sin exponer el corpus privado.
12. `audit`: registrar versiones, fuentes, decisiones, resultados y rollback.

## Orden de implementacion

- **Primero:** SQLite + contratos de semantica + importacion de fuentes y claims.
- **Despues:** correlaciones y busquedas por tema/dominio/estado/certeza.
- **Luego:** adaptadores separados para plantas, alimentos y sustancias.
- **Despues:** simulacion visual y exportacion a SVG/HTML/3D.
- **Al final:** integraciones externas, scraping amplio y publicacion automatica.

La primera prueba concreta no necesita APIs ni navegador: consultar la base, producir un mapa de precedentes y generar una interpretacion marcada como hipotesis. Solo cuando esa cadena sea auditable se conecta una herramienta visual o una fuente remota.

## Conteo de esta corrida

| Registro | Cantidad |
|---|---:|
| topics | 12 |
| claims | 26 |
| sources | 44 |
| tools | 12 |
| entities | 13 |
| relations | 4 |
| interpretations | 2 |
| states | 1 |
| semantics | 12 |
| correlations | 10 |
| constraints | 8 |
| URLs extraidas del documento | 44 |

## Archivos generados

- `jardines_interpretativos.sqlite`: registro local consultable.
- `jardines_interpretativos_correlations.csv`: correlaciones para inspeccion rapida.
- `jardines_interpretativos_process_semantics.csv`: contrato de entradas/salidas.
- `JARDINES_INTERPRETATIVOS_RESEARCH.md`: lectura humana y mapa de decisiones.

## Limite de esta investigacion

Esta corrida modela y ordena el documento completo y conserva sus referencias. No declara que cada herramienta externa este instalada, vigente, licenciada o adecuada para produccion. Ese es el siguiente gate: verificar fuente por fuente y luego probar solo los candidatos que tengan consumidor real en MAK.
