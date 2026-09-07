# Comparación `_archive` contra `/home/mak` externo

**Corte:** 2026-09-03 · operación interna, sin tocar archivos fuera de `_archive`.

## Resultado de la operación

Se creó [`_archive/duplicados exactos/`](./_archive/duplicados%20exactos/) y se trasladaron allí **16.675 archivos** con coincidencia confirmada de tamaño y SHA-256 contra un archivo fuera de `_archive`. El movimiento conserva la carpeta de procedencia dentro de `duplicados exactos/`; no se eliminó ningún byte.

Los lotes principales procesados fueron los tres orígenes de `merge-20260831`, `rollback`, `quarantine`, `root-preserve`, `orden-limpieza` y campañas pequeñas. El peso de la carpeta de duplicados es aproximadamente **1,9 GiB**.

## Qué quedó fuera de `duplicados exactos`

Lo que permanece en las carpetas originales no debe llamarse automáticamente exclusivo: incluye archivos sin copia externa localizada, archivos con mismo nombre/tamaño pero hash diferente y material cuyo equivalente puede tener otro nombre. Las campañas aún conservan, entre otros, 20.156 archivos en `orden-limpieza`, 1.497 en `quarantine`, 1.491 en `merge`, 806 en `rollback` y 87 en `root-preserve`.

## Criterio aplicado

Para cada lote se compararon candidatos por **nombre de archivo + tamaño** y solo después se calculó el **SHA-256 completo**. Solo una igualdad de hash autorizó el traslado. Las copias quedaron bajo subcarpetas que identifican su campaña/origen.

## Límite importante

Esta operación confirma duplicados cuando existe fuera un archivo con el mismo nombre y tamaño. No demuestra que no exista una copia renombrada, ni que cada archivo restante sea único. Tampoco clasifica por sí sola “diferente existente” frente a “sin equivalente” cuando no hay candidato de mismo nombre/tamaño. Para un inventario forense completo de equivalentes renombrados se requiere un índice externo por hash de todo `/home/mak`, una operación separada y más costosa.

## Lectura

`duplicados exactos` ya contiene copias seguras para apartar, pero no es todavía una autorización para borrar: la ruta de origen archivada conserva procedencia y contexto. Los archivos restantes requieren conservarse hasta resolver si son históricos, variantes, fuentes únicas o simplemente residuos.

## Categorización de lo pendiente

Esta clasificación es analítica y provisional: usa carpeta de origen, nombres, formatos, peso y patrón de uso. No convierte una inferencia en identidad autoral ni en autorización de descarte.

| Categoría | Evidencia actual | Lectura forense | Prioridad |
|---|---:|---|---|
| **Residuo técnico/reproducible** | `orden-limpieza`; 3 `.deb`, 16 `.exe`, 20 `.gz`, 82 `.so`, además de entornos Python | Instaladores, binarios, librerías o caches probablemente rehacibles. El peso alto no implica valor documental | Baja para investigación; revisar excepciones |
| **Código y entorno de ejecución** | 11.945 `.py`, 6.029 `.pyi`, 291 `.js`, 124 `.html` | Puede contener lógica, parsers, snapshots o reconstrucciones. Hay que separar fuente propia, generado y dependencia vendorizada | Alta por muestras |
| **Evidencia histórica y de proceso** | `root-preserve` (87/93,8 MB), `rollback` (806/30,5 MB), `quarantine` (1.497/34,8 MB) | Mayor probabilidad de explicar decisiones, estados previos, retiros, fallos y reversas. La ruta puede ser evidencia aunque el contenido tenga copias parciales | Muy alta |
| **Datos estructurados y trazabilidad** | 856 `.json`, 50 `.jsonl`, 44 `.csv`, bases y manifiestos | Índices, observaciones, clasificaciones, rutas y relaciones. Es la zona con mayor potencial de ahorrar trabajo de revisión manual | Muy alta |
| **Material creativo o fuente visual** | 721 `.svg`, 77 `.png`, 11 `.jpg` | Potencialmente reutilizable o documental. La extensión no basta: un `.ai` ya resultó ser PDF, por lo que hay que validar firma, capas, dimensiones y relación con entregables | Muy alta |
| **Integraciones, builds y snapshots** | `merge` (1.498/240 MB), `.pack`, logs y salidas HTML/JS | Probables ensamblajes entre ramas, proveedores o ejecuciones. Pueden ser redundantes en bytes pero útiles para reconstruir secuencia | Alta |

### Orden recomendado

1. Datos estructurados y evidencia histórica: localizar relaciones, estados y referencias.
2. Material visual y `merge`: distinguir fuente editable, entregable, preview y derivado.
3. Código propio y snapshots: distinguir herramienta original de entorno reproducible.
4. Residuo técnico: revisar solo excepciones con valor de versión o procedencia.

### Conclusión

El pendiente no es homogéneo. El volumen está concentrado en `orden-limpieza`, pero la mayor densidad de valor está en `root-preserve`, `rollback`, `quarantine`, los datos estructurados, `merge` y las fuentes visuales. La señal de ahorro de trabajo no sería borrar binarios: sería explotar manifiestos, bases y salidas estructuradas para saber qué es fuente, qué es derivado y qué quedó sin equivalente externo. La categorización prioriza la revisión, pero todavía no permite declarar “basura real” archivo por archivo.

## Corte adicional: divergencias reales de `merge`

El manifiesto identifica 813 rutas con `variants_all_preserved`. No son 813 archivos necesariamente únicos: son rutas donde se conservaron alternativas de uno o más orígenes. La distribución revela dónde está la señal:

- 298 SVG: el mayor bloque de divergencias está en piezas vectoriales, especialmente contraportadas y salidas de suplementos. Aquí puede haber valor editable, cambios de diseño o versiones de entrega.
- 207 Python, 76 Markdown, 42 HTML, 35 JSON y 25 JavaScript/TypeScript: son diferencias de implementación, documentación y datos, no residuos intercambiables por tamaño.
- Por árbol, `iskvw` reúne 256 divergencias, `docs` 78, `tests` 76, `projects` 67, `tools` 55, `cultura` 51 y `src` 50. El conflicto afecta sistema, documentación y herramientas además del material artístico.
- Entre los más pesados aparecen `rd_testeos_eventos_2025_evidence`, ocho SVG de contraportadas, `MANIFEST.json`, `data/rd.db`, `code_structure_index.json`, `rd_firecrawl*`, `micelio.json` y `archivo.json`. Son mejores candidatos que un barrido por extensión porque combinan peso, estructura y divergencia.

**Lectura forense:** la divergencia de `merge` es evidencia de estados alternativos preservados, no prueba de que una versión sea correcta. La revisión debe comparar primero los SVG de contraportadas y las bases/manifiestos, y después seguir sus referencias hacia `projects`, `docs` e `iskvw`.

### Verificación del bloque de contraportadas SVG

Se compararon los ocho SVG de `svg/suplementos_rd/09_contraportadas_dark/`. En todos, `runner-vibecodeine` y `active-flujo` tienen el mismo tamaño y el mismo SHA-256 abreviado; `win-flujo` no aporta archivo en esa ruta. Por tanto, estas 8 divergencias no son dos diseños distintos: son **presencia en dos orígenes y ausencia en un tercero**.

Los SVG son documentos reales con `viewBox="0 0 2000 2800"`, estilos y trazados vectoriales; tienen potencial editable. El hallazgo útil no es una variante visual entre runner y active, sino que el origen WIN carecía de esa familia y que el archivo conservado en los otros dos orígenes constituye la fuente vectorial disponible.

### Corrección tras leer el registro de hashes del manifiesto

El manifiesto conserva metadatos de `win-flujo` aunque algunas rutas de origen ya no estén físicamente en su ubicación original. Esos metadatos muestran que la lectura anterior de “WIN ausente” era incompleta: para los ocho SVG, WIN sí tenía una variante registrada, con tamaño y SHA distintos; `runner-vibecodeine` y `active-flujo` coinciden entre sí. Por tanto, el bloque contiene **una variante WIN real frente a una pareja runner/active idéntica**, no una simple ausencia.

El mismo patrón aparece en `rd_testeos_eventos_2025_evidence`, `MANIFEST.json`, `rd_firecrawl*`, `micelio.json`, `archivo.json`, `data/rd.db` y `context/flujo_hub.html`: WIN difiere, mientras runner/active coinciden en varios casos. Estos son los primeros archivos que deben compararse semánticamente, porque pueden representar una línea de trabajo distinta y no solo un conflicto de montaje.

### Resultado semántico de los primeros JSON

### Lectura forense del `MANIFEST.json` de sesiones

La variante WIN no es solo un manifiesto con otra ruta: declara `evidence_sanitized_candidate_material` y registra una regla de sanitización (`windows_user_home_to_local_user_home`). Active/runner declara `evidence_preserved_candidate_material` y conserva la fuente Windows original. Ambos listan 76 archivos y 21.223 exclusiones, pero los registros de archivo difieren: WIN conserva `source_bytes`/`source_sha256` y un tamaño/hash de salida sanitizada, mientras active conserva el tamaño/hash original.

Esto es una diferencia de **tratamiento probatorio**. WIN puede ser más portable, pero sus bytes de salida no son necesariamente los bytes originales; active es mejor para autenticidad de fuente. Ninguno debe reemplazar al otro: hay que conservar WIN como reconstrucción sanitizada y active como referencia preservada.

Al comparar los objetos JSON completos, no solo sus bytes, `rd_testeos_eventos_2025_evidence`, `rd_firecrawl_2026-08-11.json`, `rd_firecrawl_matriz_2026-08-11.json` y `micelio.json` resultaron **estructuralmente iguales** entre WIN y active/runner, pese a tener tamaños y SHA distintos registrados en el manifiesto. En estos casos la divergencia es de serialización, orden/formato o metadatos no representados en la comparación, no evidencia de contenido alternativo.

Esto evita sobrevalorar 4 falsos positivos. En cambio, `data/rd.db`, `archivo.json`, `context/flujo_hub.html` y los SVG siguen requiriendo comparación específica: bases por tablas/filas, HTML por contenido servido y SVG por estructura visual/vectorial.

### Resultado de bases, índices y hub

### Descomposición real de `orden-limpieza`

El peso de esta campaña no es homogéneo. Los instaladores `lm-studio.deb`, `chatgpt_amd64.deb`, `code_...deb`, `GoogleDriveSetup.exe` y `Antigravity.tar.gz` suman aproximadamente 1,6 GB y tienen perfil de software reinstalable. El ZIP de contraportadas (≈65 MB) es una salida regenerable, pero conviene conservarlo si representa una entrega cerrada.

En cambio, los renders `render_issue*`, los respaldos JSONL, los manifiestos de blobs, `archivo.pre-refresh-20260815.json` y los PDFs de propuestas entregadas son evidencia o productos: aunque algunos tengan consumidor externo, no deben mezclarse automáticamente con basura técnica. Los logs de `.remember` y `.playwright-mcp` tienen valor menor por archivo, pero pueden documentar decisiones o navegación si se necesita reconstruir una operación.

**Resultado:** dentro de `orden-limpieza`, la revisión rápida puede marcar instaladores como `reproducible-baja`, pero debe preservar para revisión documental los manifiestos, respaldos, renders y entregables. El peso deja de ser el criterio principal.

- `data/rd.db` tiene las mismas 20 tablas entre WIN y active/runner y casi los mismos conteos. La única diferencia de filas está en `venues`: WIN conserva 3 y active/runner 1. El resto de la base suma 7.587 filas frente a 7.585. Es una diferencia pequeña pero concreta: WIN conserva dos venues adicionales, no una base de conocimiento completamente distinta.
- `archivo.json` no es una sola familia equivalente: hay snapshots con 446/479 piezas y 237/269 vínculos, mientras el snapshot principal registra 1.690 piezas y 4.729 vínculos. La fecha y la ruta son esenciales; no se deben colapsar por nombre.
- `flujo_hub.html` de WIN pesa 719.974 bytes y contiene 24 referencias `/api/`; active/runner pesa 780.019 bytes y contiene 28. Esto demuestra una variante funcional del hub, no solo una diferencia de formato. Requiere revisar qué cuatro rutas/API faltan antes de relegarlo.

Estos resultados suben `data/rd.db` y las variantes de `flujo_hub.html` a revisión prioritaria: tienen diferencias medibles, pequeñas en la base pero potencialmente operativas en la interfaz.

### Qué contienen las dos filas extra de `venues`

WIN conserva `openklub` y `paralelo_89`, además de `espacio_riesco`. Active/runner conserva solo `espacio_riesco`. Las dos filas extra no son especificaciones completas: ambas tienen capacidad `unknown`, requisitos `{}` y notas que exigen confirmar aforo, superficie, servicios y preset con un rider o con el usuario. Su valor es de **cobertura candidata**, no de dato operativo confirmado.

La diferencia de `rd.db` queda así clasificada como **adición estructurada de candidatos con información incompleta**, útil para recuperar contexto de productoras/venues, pero no suficiente para planificar un evento sin validación humana.

### Evolución de `archivo.json`

Los snapshots WIN de 2026-08-04 contienen 479 y 446 piezas; el snapshot WIN de 2026-08-12 contiene 1.690; el snapshot active de 2026-08-29 contiene 2.034. La comparación de IDs muestra que el corte del 12 de agosto está completamente contenido en el del 29 de agosto: comparte 1.690 IDs y active agrega 344. Los cortes del 4 de agosto son más pequeños y solo comparten 227 IDs con el snapshot posterior.

Esto prueba una **secuencia temporal de crecimiento**, no duplicación inútil. El snapshot active del 29 de agosto es el más completo de los encontrados; los anteriores conservan valor histórico para saber qué piezas y vínculos existían en cada fecha.

### Diferencia funcional del hub

La comparación de cadenas API confirma que active/runner incorpora cuatro rutas que no aparecen en WIN: `/api/project/learning`, `/api/project/probe`, `/api/rd/topics` y `/api/status`. WIN conserva las rutas operativas de portafolio, trabajos, packs, show-kit, RD DB y planos, pero no esas capacidades de aprendizaje, sondeo, tópicos y estado.

Esto clasifica el hub WIN como **variante funcional más antigua o recortada**, no como un mero cambio de empaquetado. Su valor depende de si se necesita recuperar la interfaz histórica; para el runtime actual, active/runner contiene más superficie funcional.

### Resultado semántico del bloque SVG

La comparación XML de los nueve SVG principales (ocho productos y `contraportada_cambios.svg`) muestra el mismo `viewBox`, número de elementos, grupos, trazados y textos entre WIN y active. Los textos extraíbles también coinciden. Los SHA y tamaños difieren, pero no aparece una diferencia estructural o textual en esta medición.

Por ahora, el bloque SVG se clasifica como **duplicación/serialización divergente con equivalencia visual-estructural probable**, no como nueve diseños alternativos confirmados. La diferencia puede estar en formato de exportación, espacios, metadatos o contenido vectorial serializado de otra forma; una afirmación visual definitiva requeriría renderizar ambas versiones y comparar imágenes.

### Confirmación por render

Se renderizaron los nueve SVG WIN/active a 500×700 píxeles y se compararon píxel a píxel. Los nueve dieron **cero píxeles diferentes**. Queda confirmado que, para esta resolución y motor de render, las variantes WIN y active son visualmente idénticas; la diferencia de bytes no representa una diferencia visible de diseño. Se conservan como duplicados de procedencia distinta, no como alternativas creativas.
