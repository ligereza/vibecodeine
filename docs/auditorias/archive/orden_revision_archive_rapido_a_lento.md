# Orden de revisión de `_archive`: rápido → lento

**Objetivo:** encontrar valor o ahorro de trabajo con el menor costo de análisis. Es una priorización de revisión, no una orden de borrar.

## 1. Conteo y lectura de metadatos — minutos

Revisar rutas, tamaños, fechas, extensiones y carpetas de origen. Sirve para detectar concentraciones anómalas y separar binarios, logs, datos, código y visuales sin abrirlos.

**Salida esperada:** mapa de volumen y primeros grupos sospechosos.

## 2. Residuos técnicos evidentes — minutos a decenas de minutos

Priorizar los 3 `.deb`, 16 `.exe`, `.gz`, `.so`, archivos numéricos (`.0`, `.2`, `.11`) y caches de `orden-limpieza`. Confirmar si son instaladores, librerías o artefactos reproducibles y si tienen versión/procedencia excepcional.

**Valor probable:** ahorro de espacio. **Riesgo:** bajo, salvo que documenten un entorno irrepetible.

## 3. Logs, reportes y manifiestos pequeños — decenas de minutos

Leer `.log`, `.md`, `.csv` pequeños y manifiestos. Buscar decisiones, errores, rutas de entrada/salida, estados `pending`, nombres de jobs y referencias a archivos ausentes.

**Valor probable:** ahorrar búsquedas posteriores y reconstruir qué ocurrió.

## 4. Datos estructurados — decenas de minutos a horas

Revisar los 856 `.json`, 50 `.jsonl`, 44 `.csv` y manifiestos por esquema, no uno a uno. Agrupar por claves, proyectos, fechas, `source_ref`, estados y rutas. Comparar derivados para detectar si son copias, variantes o salidas de una misma ejecución.

**Valor probable:** muy alto; puede reemplazar muchas horas de inspección manual.

## 5. Bases SQLite/DB/DuckDB — horas

Abrir solo el esquema y consultas de resumen: tablas, conteos, relaciones, fechas, referencias y estados. Después revisar las tablas que conectan entidades con archivos o proyectos. No exportar toda la base ni interpretar cada registro sin contexto.

**Valor probable:** muy alto para descubrir relaciones no visibles por nombre de archivo.

## 6. Evidencia histórica de `root-preserve`, `quarantine` y `rollback` — horas

Reconstruir cada campaña como secuencia: estado anterior, motivo, acción, reversa y resultado. Distinguir copia técnica de evidencia de decisión. Priorizar archivos que mencionen retiros, restauraciones, conflictos o cambios de estructura.

**Valor probable:** máximo para entender el archivo. **Riesgo:** confundir historia de proceso con verdad sobre una obra o autoría.

## 7. `merge-20260831` y snapshots de integración — horas a un día

Separar fuentes, salidas generadas, conflictos y ensamblajes. Comparar manifests y rutas; identificar qué rama/proveedor aporta cada pieza y qué quedó solo en el archivo.

**Valor probable:** alto para recuperar trabajo y entender divergencias.

## 8. Código propio, builds y dependencias — uno o varios días

Revisar primero puntos de entrada y scripts referenciados por manifiestos; después módulos y tipos. Separar código fuente útil de copias vendorizadas, stubs, `.pyi` y builds. El volumen de `.py` hace ineficiente leerlo linealmente.

**Valor probable:** variable; alto si contiene herramientas no presentes fuera, bajo si es entorno duplicado.

## 9. Material visual y creativo — uno o varios días

Validar firma real, dimensiones, capas, texto extraíble y relación con entregables. Agrupar SVG/PNG/JPG por proyecto y comparar previews con fuentes. No confiar en `.ai`, `.svg` o nombres: ya se detectó al menos un `.ai` cuyo contenido era PDF.

**Valor probable:** máximo cuando exista fuente editable o material no recuperable fuera.

## 10. Equivalencia renombrada y revisión forense profunda — más lento

Construir un índice SHA-256 del resto de `/home/mak` y contrastarlo con los archivos pendientes sin depender del nombre. Luego investigar diferencias semánticas, contenedores, exportaciones y relaciones entre archivos.

**Resultado:** único nivel capaz de afirmar con mucha más seguridad “solo existe en `_archive`” frente a “existe fuera con otro nombre”. Es la operación más costosa y debe hacerse al final, sobre los grupos que sobrevivan las etapas anteriores.

## Prioridad resumida

**Rápido y rentable:** metadatos → residuos evidentes → logs/manifiestos → datos estructurados.

**Mayor valor:** bases → evidencia histórica → `merge`.

**Más lento:** código → visuales → equivalencia global por hash y análisis semántico.

## Primer resultado del embudo

La inspección inicial ya cambia la prioridad:

- `root-preserve/context/python_census_20260901.json` y su copia generada son un par que debe tratarse como **un mismo centro de información**, no como dos hallazgos independientes.
- `quarantine/.../turnos_flujo.jsonl` tiene suficiente tamaño y estructura para reconstruir actividad; merece revisión antes que miles de archivos técnicos.
- `merge/fused/projection3/MANIFEST.json`, `code_structure_index.json`, `root-materialization.json` y los `MANIFEST.json` de sesiones conectan rutas, fuentes y productos; son nodos de alto rendimiento.
- Los JSON de `googleapiclient` y tokenizadores ubicados dentro de `venvs_oi/.../site-packages` tienen perfil fuerte de **dependencia reproducible**, aunque sean grandes; no deben competir con los manifiestos.
- Los conjuntos `rd_*_evidence`, `micelio.json`, `eventos.jsonl` y `grafo_cache.json` forman grupos temáticos que conviene revisar por relación, no por tamaño aislado.

Por tanto, la siguiente revisión efectiva debe comenzar con **manifiestos → índices → bases → logs de proceso → excepciones visuales**. El orden por extensión queda subordinado a la conectividad y a la irreemplazabilidad.

## Evidencia concreta obtenida

- `projection3/MANIFEST.json` no es un simple inventario: registra 5.426 rutas, 3.087 deduplicaciones por igualdad, 813 rutas divergentes y 2.366 variantes. Es el mejor punto de entrada para reconstruir qué se fusionó y qué quedó en conflicto.
- `root-materialization.json` registra 6.214 archivos enlazados, 22 enlaces simbólicos, una colisión preservada y dos conflictos reubicados. Es evidencia de decisiones de materialización, no solo una salida técnica.
- `code_structure_index.json` resume 1.028 archivos Python, 261.767 líneas y 11.404 símbolos; identifica 516 módulos con escritura de filesystem, 75 con base de datos y 69 con red. Permite muestrear código por impacto sin leer 1.028 archivos linealmente.
- `grafo_cache.json` contiene 1.830 nodos y 5.856 relaciones, incluidos 1.366 nodos de imagen, 232 de video, 160 de Codex y 59 informes. Es un índice relacional de alto valor, pero sus etiquetas (`sustrato`, `cultivo`, etc.) son clasificación del sistema, no prueba de autoría o valor artístico.
- `exact-duplicate-candidates.csv` contiene 14.626 filas en 2.167 grupos; 683 filas están marcadas `review_live_alias` y 43 `review_evidence`. Es una cola de revisión ya priorizada: esos casos deben pasar antes que los 11.690 candidatos marcados para archivo.

### Próximo corte recomendado

La revisión inteligente debe producir primero una tabla de **nodos → archivos conectados → estado externo → acción** para esos cinco centros. Solo los archivos que queden sin explicación o que aparezcan como `review_live_alias`, `review_evidence`, divergentes o fuentes visuales pasarán a inspección individual.
