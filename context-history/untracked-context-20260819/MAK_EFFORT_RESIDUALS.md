# Residuos robustos de esfuerzo MAK

Calculado desde `data/mak_knowledge.db` con el contrato adjunto de `esfuerzo.py`.
La agrupacion respeta el modo y la ruta de Research; tema y ruta se conservan
en cada fila para triangulacion posterior.

- calculado: `2026-08-18T16:54:50+00:00`
- documentos con metricas: **598**
- filas metricas materializadas: **4484**
- filas puntuadas: **4422**
- CSV: `/home/mak/flujo/context/MAK_EFFORT_RESIDUALS.csv`

## Metodo

Se usa la mediana del grupo y la escala MAD. Si MAD es cero, se usa
la desviacion absoluta media escalada; si el grupo es constante, la fila
queda sin puntuar. Con menos de tres valores comparables no se fabrica
una escala. `fuentes` invierte signo porque menos fuentes implica mayor
resistencia; las demas metricas conservan signo positivo.

## Cobertura

| metrica | presente | puntuadas | grupo menor a 3 | grupo constante |
|---|---:|---:|---:|---:|
| `iteraciones` | 561 | 561 | 0 | 0 |
| `llamadas_llm` | 567 | 564 | 3 | 0 |
| `profundidad_cadena` | 567 | 560 | 3 | 4 |
| `errores` | 571 | 561 | 3 | 7 |
| `timeouts` | 0 | 0 | 0 | 0 |
| `consultas` | 579 | 579 | 0 | 0 |
| `deriva_consultas` | 487 | 448 | 2 | 37 |
| `fuentes` | 581 | 581 | 0 | 0 |
| `duracion_ms` | 571 | 568 | 3 | 0 |

## Mayores residuos positivos

| residuo | modo | ruta | tema | metrica | valor | esperado |
|---:|---|---|---|---|---:|---:|
| 39.000 | `informes` | `research/informes` | ¿Cuáles son las estrategias de marketing alternativas que podrían ser más efecti | `profundidad_cadena` | 2.000 | 1.000 |
| 16.714 | `informes` | `research/informes` | test1 | `fuentes` | 3.000 | 6.000 |
| 16.714 | `informes` | `research/informes` | test1 | `fuentes` | 3.000 | 6.000 |
| 10.058 | `informes` | `research/informes/archive` | Investigacion cultural DESCRIPTIVA (historia, estetica, derecho, contexto social | `errores` | 10.000 | 0.000 |
| 10.000 | `checkpoints` | `research/checkpoints` | Donde puedo encontrar informacion oficial sobre el evento SFERA Experience 2024 | `consultas` | 2.000 | 1.000 |
| 10.000 | `checkpoints` | `research/checkpoints` | codex-piezas | `consultas` | 2.000 | 1.000 |
| 9.750 | `informes` | `research/informes` | latido: la gramatica del telar como sistema generativo de patrones (field, borde | `errores` | 1.000 | 0.000 |
| 9.750 | `informes` | `research/informes` | ¿Cómo se puede mejorar la precisión de la memoria visual de los mapas urbanos co | `errores` | 1.000 | 0.000 |
| 9.750 | `informes` | `research/informes` | ¿Cómo se mide o evalúa la 'tensión subyacente' mencionada en relación con la imp | `errores` | 1.000 | 0.000 |
| 9.750 | `informes` | `research/informes` | ¿Cuáles son las estrategias de marketing alternativas que podrían ser más efecti | `errores` | 1.000 | 0.000 |
| 9.724 | `informes` | `research/informes` | ¿Cómo se puede involucrar efectivamente a la comunidad en la evaluación y toma d | `duracion_ms` | 411959.000 | 84341.000 |
| 9.691 | `informes` | `research/informes` | ¿Cuáles son los principales desafíos para integrar la memoria visual con la plan | `duracion_ms` | 410866.000 | 84341.000 |
| 9.559 | `informes` | `research/informes/archive` | Qué patrones y significados nuevos pueden revelarse al aplicar el paradigma indi | `duracion_ms` | 598541.000 | 72042.500 |
| 9.430 | `informes` | `research/informes/archive` | Falta de datos sobre la prevalencia y el impacto del consumo de drogas de diseño | `duracion_ms` | 591416.000 | 72042.500 |
| 9.052 | `informes` | `research/informes/archive` | Investigacion cultural DESCRIPTIVA (historia, estetica, derecho, contexto social | `errores` | 9.000 | 0.000 |

## Limites

- Un residuo es una senal de esfuerzo relativo, no una calidad ni una
  recomendacion automatica de proyecto.
- Los temas se leen desde el JSON cuando existe una clave declarada; si
  no existe, se conserva el slug del archivo y se marca implicitamente
  como inferencia de ruta.
- `largo_informe`, presente en algunas filas de la base, queda fuera del
  puntaje porque no pertenece al mapa `METRICAS` del contrato adjunto.
- La base no contiene una decision de postulacion; esa decision sigue
  requiriendo evidencia, consumidor y revision humana.
