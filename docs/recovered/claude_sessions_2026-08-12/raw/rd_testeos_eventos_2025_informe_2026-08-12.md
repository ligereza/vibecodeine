# Integración de testeos en eventos — base 2025

Generado: 2026-08-12

## Resultado

Se preservó la fuente `Testeo 2025.xlsx` y se construyó una integración separada con 42 pestañas, 42 eventos-fuente, 1761 filas no vacías de fuente (de ellas, 1646 quedan clasificadas como datos y 115 como datos con anomalías) y 5394 observaciones de reactivo/resultado.

La fuente no se interpretó como una tabla de composición. Cada registro conserva su pestaña y fila original; las normalizaciones son candidatas para revisión humana.

## Regla sanitaria y semántica

> Los testeos colorimétricos registran una señal de presencia compatible con ciertos compuestos o familias. No demuestran identidad definitiva, pureza, potencia, cantidad ni seguridad.

Por eso la integración usa `contains_signal_only` y conserva el texto original de cada resultado.

## Puente futuro

La conexión queda preparada sin inventar vínculos:

`test_id -> event_id -> venue_id / producer_id`

- `event_id` identifica la pestaña-fuente, no una venue ni una productora.
- `venue_id` y `producer_id` quedan vacíos hasta contar con evidencia explícita.
- `Link Queue` contiene dos enlaces pendientes por evento: evento-venue y evento-productora.
- Se conserva `evidence_ref`, `confidence`, `status` y `review_status` para una futura vinculación humana.

## Hallazgos de calidad

- Filas de datos incluyendo anomalías: 1831
- Filas no vacías sin encabezados repetidos: 1761
- Filas clasificadas como datos: 1646
- Grupos de pestañas con contenido idéntico: 3
- Filas con sustancia ausente o no resuelta: 115
- Etiquetas de sustancia no resueltas: 4
- Etiquetas de reactivo no resueltas: 8

El nombre del archivo dice 2025, pero algunas pestañas contienen tokens de fecha que parecen corresponder a 2026. No se eliminaron: quedaron marcadas en `Events` para confirmar el periodo antes de publicar agregados.

## Archivos

- Fuente preservada: `Testeo 2025.source.xlsx`
- Evidencia machine-readable: `rd_testeos_eventos_2025_evidence_2026-08-12.json`
- Libro integrado: `rd_testeos_eventos_2025_integrated_2026-08-12.xlsx`
- Esta síntesis: `rd_testeos_eventos_2025_informe_2026-08-12.md`

## Próxima revisión humana

1. Confirmar qué pestañas pertenecen efectivamente a 2025.
2. Revisar duplicados exactos y decidir si se excluyen solo de agregados públicos.
3. Resolver sustancias y reactivos marcados como candidatos o no resueltos.
4. Vincular cada evento con venue/productora usando evidencia, sin inferir desde el nombre de la pestaña.
5. Aprobar el lenguaje público de cada resultado antes de llevarlo a la matriz o a un POST.
