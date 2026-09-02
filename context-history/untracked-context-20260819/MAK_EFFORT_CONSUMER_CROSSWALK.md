# Crosswalk de esfuerzo hacia consumidores Research/Cultura

Este reporte no convierte un residuo estadistico en una decision de
limpieza o postulacion. Solo conecta la senal con evidencia de ruta y
declara donde el inventario aun no prueba consumo runtime.

- base: `/home/mak/flujo/data/mak_knowledge.db`
- documentos con esfuerzo: **598**
- documentos con entidad directa: **598**
- relaciones `possibly_consumed_by` directas desde Research: **0**

## Lectura de la evidencia

Los JSON de esfuerzo estan vinculados a la entidad de departamento
`research`, pero el inventario no contiene relaciones estaticas
`possibly_consumed_by` desde esos JSON hacia un consumidor. Por eso
el ranking sirve para priorizar revision, mientras que el consumo real
se prueba con la interfaz 8890, el proxy 8900 y el gate de Cultura.

## Consumidores candidatos conocidos

| componente | estado de evidencia | consumidor/ruta |
|---|---|---|
| `tools/research_job_router.py` | contract_checked; runtime gate probado | `GET /api/cultura/opportunity-gate` en 8900 |
| `cultura/mak_research/source_pipeline.py` | componente presente; captura separada | gate offline; no proveedor llamado |
| `cultura/mak_research/fondart_corpus.py` | componente presente; corpus separado | gate offline; propuesta queda en draft |
| `cultura/mak_research/interfaz.py` | canonico/proyeccion hash-validado | servicio interno 8890, proxied by 8900 |
| `cultura/mak_plataforma/hub.py` | entrypoint activo | hub 8900; APIs Cultura/Research |

## Candidatos priorizados por residuo

| residuo | modo | ruta | tema | metrica | valor | esperado | entidad directa |
|---:|---|---|---|---|---:|---:|---|
| 39.000 | `informes` | `research/informes` | ¿Cuáles son las estrategias de marketing alternativas que podrían ser más efectivas que la retórica  | `profundidad_cadena` | 2.000 | 1.000 | department:research [active] |
| 16.714 | `informes` | `research/informes` | test1 | `fuentes` | 3.000 | 6.000 | department:research [active] |
| 16.714 | `informes` | `research/informes` | test1 | `fuentes` | 3.000 | 6.000 | department:research [active] |
| 10.058 | `informes` | `research/informes/archive` | Investigacion cultural DESCRIPTIVA (historia, estetica, derecho, contexto social; nada operativo, na | `errores` | 10.000 | 0.000 | department:research [active] |
| 10.000 | `checkpoints` | `research/checkpoints` | Donde puedo encontrar informacion oficial sobre el evento SFERA Experience 2024 | `consultas` | 2.000 | 1.000 | department:research [active] |
| 10.000 | `checkpoints` | `research/checkpoints` | codex-piezas | `consultas` | 2.000 | 1.000 | department:research [active] |
| 9.750 | `informes` | `research/informes` | latido: la gramatica del telar como sistema generativo de patrones (field, border, medallion) | `errores` | 1.000 | 0.000 | department:research [active] |
| 9.750 | `informes` | `research/informes` | ¿Cómo se puede mejorar la precisión de la memoria visual de los mapas urbanos con la realidad aument | `errores` | 1.000 | 0.000 | department:research [active] |
| 9.750 | `informes` | `research/informes` | ¿Cómo se mide o evalúa la 'tensión subyacente' mencionada en relación con la imposición de un orden  | `errores` | 1.000 | 0.000 | department:research [active] |
| 9.750 | `informes` | `research/informes` | ¿Cuáles son las estrategias de marketing alternativas que podrían ser más efectivas que la retórica  | `errores` | 1.000 | 0.000 | department:research [active] |
| 9.724 | `informes` | `research/informes` | ¿Cómo se puede involucrar efectivamente a la comunidad en la evaluación y toma de decisiones sobre l | `duracion_ms` | 411959.000 | 84341.000 | department:research [active] |
| 9.691 | `informes` | `research/informes` | ¿Cuáles son los principales desafíos para integrar la memoria visual con la planificación participat | `duracion_ms` | 410866.000 | 84341.000 | department:research [active] |
| 9.559 | `informes` | `research/informes/archive` | Qué patrones y significados nuevos pueden revelarse al aplicar el paradigma indiciario en la arqueol | `duracion_ms` | 598541.000 | 72042.500 | department:research [active] |
| 9.430 | `informes` | `research/informes/archive` | Falta de datos sobre la prevalencia y el impacto del consumo de drogas de diseño en la cultura elect | `duracion_ms` | 591416.000 | 72042.500 | department:research [active] |
| 9.052 | `informes` | `research/informes/archive` | Investigacion cultural DESCRIPTIVA (historia, estetica, derecho, contexto social; nada operativo, na | `errores` | 9.000 | 0.000 | department:research [active] |

## Consumidores estaticos encontrados por el inventario

| tipo | nombre | ruta | estado |
|---|---|---|---|
| `tool_candidate` | `fondart_corpus` | `/home/mak/flujo/cultura/mak_research/fondart_corpus.py` | `unclassified` |
| `interface_candidate` | `interfaz` | `/home/mak/flujo/cultura/mak_research/interfaz.py` | `unclassified` |
| `tool_candidate` | `interfaz` | `/home/mak/flujo/cultura/mak_research/interfaz.py` | `unclassified` |
| `tool_candidate` | `source_pipeline` | `/home/mak/flujo/cultura/mak_research/source_pipeline.py` | `unclassified` |
| `tool_candidate` | `research_job_router` | `/home/mak/flujo/tools/research_job_router.py` | `unclassified` |
| `interface_candidate` | `interfaz` | `/home/mak/research/interfaz.py` | `unclassified` |
| `tool_candidate` | `interfaz` | `/home/mak/research/interfaz.py` | `unclassified` |

## Decision de fase

El siguiente slice no debe ser un informe con residuo alto aislado:
debe ser el gate `opportunity -> research job -> draft proposal`,
porque es el unico tramo que ya tiene componente, ruta 8900, contrato
offline y rollback claro. Los outliers de `errores`, `duracion_ms` y
`profundidad_cadena` quedan como evidencia para mejorar ese proceso, no
como motivo para descartar documentos o herramientas.
