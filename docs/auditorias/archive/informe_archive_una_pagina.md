# Informe ejecutivo — `_archive`

**Fecha de corte:** 2026-09-03 · **modo:** inspección de solo lectura.

`_archive` contiene **40.843 archivos** con un peso total de **5.067.657.656 bytes (≈4,72 GiB)**. No se modificó ningún elemento del archivo.

## Hallazgo central

No es un conjunto homogéneo: es una reserva de estados históricos y procedencias. El 91% del peso está concentrado en `orden-limpieza-20260828` (2,43 GB) y `merge-20260831` (2,19 GB). Los otros bloques relevantes son `quarantine-20260806-20260809` (181 MB) y `rollback-20260811-20260814` (171 MB).

Los cinco elementos más pesados son cuatro instaladores (`lm-studio.deb`, `chatgpt_amd64.deb`, `GoogleDriveSetup.exe`, `code_*.deb`) y una base `mak_knowledge.db`; juntos suman aproximadamente 1,68 GB. Esto cambia la lectura del archivo: el mayor consumo no proviene de imágenes o documentos, sino de binarios, bases y exportaciones.

## ¿Hay algo valioso?

**Sí.** El valor no está donde está el mayor peso. Hay tres núcleos que conviene proteger:

1. **Activos visuales recuperables:** seis propuestas PDF marcadas como entregadas a cliente y el job de contraportadas con `FLYERS8.ai`, SVG editables, PDF, reporte de job, estado y script de regeneración. Este es el material con valor directo de reutilización/entrega.
2. **Evidencia de proyecto:** `ARICA-FONDART-2027` conserva input, observación, unidades, práctica, proyección, plan y dossier en varias corridas. Permite reconstruir y comparar un piloto; no es simplemente una carpeta de resultados.
3. **Memoria y procedencia:** las bases de arqueología, packs Git, logs, snapshots de rollback y documentos de curatoria/plataforma explican decisiones y fallos históricos que probablemente no están en el checkout actual.

Los instaladores y bibliotecas son voluminosos pero de valor secundario: parecen software ya instalado, instaladores no utilizables en Debian o dependencias sin consumidor. Las salidas regenerables y los renders valen como evidencia, no necesariamente como fuente maestra.

## Formatos que explican el peso

Los `.deb` son solo tres archivos, pero aportan 1,23 GB; luego vienen `.json` (3.022; 804 MB), `.svg` (3.202; 376 MB), `.exe` (32; 300 MB), `.sqlite` (7; 259 MB), `.db` (11; 205 MB), `.pdf` (153; 189 MB), `.py` (15.034; 177 MB), comprimidos `.gz` (165 MB) y bibliotecas `.so` (160 MB). También hay 189 PNG, 619 JPG, 4 DuckDB, 347 JSONL, 5.197 Markdown y 325 HTML.

## Relaciones principales

Hay **275 grupos de igualdad SHA-256** entre archivos de al menos 100 KiB, con **858 archivos involucrados**. Las coincidencias más significativas vinculan: las corridas del piloto `ARICA-FONDART-2027`; las copias de `rd_fuentes/testeo_eventos_2025_evidence.json` entre worktrees y sesiones recuperadas; familias SVG de `suplementos_rd` entre varios orígenes/worktrees; tres copias del PDF municipal de fondos concursables; y dos copias del censo Python en `root-preserve`.

También hay familias relacionadas aunque no necesariamente idénticas: `active-flujo`, `runner-vibecodeine` y `win-flujo` contienen árboles paralelos; `quarantine` conserva worktrees de esos mismos materiales; y `rollback` conserva capturas/recuperaciones. En `ARICA-FONDART-2027`, los nombres de corrida (`baseline`, `enriched`, `technical-surface`) funcionan como capas de un mismo proceso, mientras que la igualdad de bytes solo se confirmó en los grupos indicados.

## Lectura operativa

El archivo mezcla instaladores y dependencias, bases de datos y WAL, código fuente, documentación, imágenes, piezas SVG/AI/PDF, registros de sesiones y salidas de pilotos. La duplicación parece responder principalmente a preservación de procedencia, worktrees, rollback y distintas corridas, no a una sola colección editorial. Por eso este informe no recomienda borrar ni fusionar: igualdad de bytes demuestra copia, pero no establece cuál contexto debe conservarse ni reemplazarse.

El inventario detallado, con conteos, pesos y relaciones, está en `catalogo_archive_inventario.md`.

**Juicio final:** no recomiendo tratar `_archive` como basura ni como un simple duplicado. Recomiendo priorizar una futura revisión visual de los originales AI/SVG/PDF, una lectura comparativa de las corridas ARICA y una preservación controlada de la arqueología/rollback. Eso identifica valor real sin reactivar ni borrar nada.

## Dictamen forense

El material más valioso no es el más pesado. La cadena de contraportadas de 2026-07-05 contiene brief, estado, reporte, fuentes editables AI/SVG, cambios y PDF. **Corrijo una afirmación anterior:** no está probado que sea una entrega aprobada; `brief.yaml`, `estado.md` y `reporte_job.md` dicen `pendiente_datos`, con cliente, proyecto, productos y texto aprobado pendientes. Su valor real es el de una cadena de producción recuperable en estado incompleto. Las seis propuestas PDF están bajo `entregado-a-cliente`, pero esa ruta no prueba por sí sola aceptación comercial.

El conjunto `ARICA-FONDART-2027` es evidencia de proyecto, no solo output. Sin embargo, presenta una anomalía crítica: los `runs/*/observation.json` son idénticos al `input/archive_observation.json`. El proceso posterior puede seguir siendo valioso, pero esa observación no debe contarse como medición independiente hasta revisar sus campos.

El rollback conserva memoria probatoria: decisiones curatoriales humanas, rechazos, estados no promovidos, fallos y contexto operativo. Los textos con `unknown` o investigaciones inconclusas prueban una búsqueda fallida, no el hecho buscado. Los manifests y razones de retiro deben leerse como testimonios históricos: hay contradicciones internas y al menos una justificación técnica refutada.

El `projection3/MANIFEST.json` confirma que el merge no es una fuente única: registra 5.426 rutas, 3.087 iguales, 813 divergentes y 2.366 variantes entre orígenes.

**Conclusión:** `_archive` contiene fuentes creativas, evidencia de proyecto y memoria de decisiones. Su riesgo principal no es la falta de valor, sino mezclar originales, derivados, duplicados y relatos defectuosos bajo una misma etiqueta. La prioridad forense es proteger AI/SVG/PDF, ARICA y rollback; no borrar ni fusionar basándose en extensión, nombre o igualdad de bytes.

## Triage solicitado

Hay basura real, pero no es sinónimo de “archivo grande”. Con baja pérdida informacional aparecen logs de smoke/debug, cachés de herramientas, salidas temporales y, con verificación previa, bibliotecas compiladas de entornos Python. Los instaladores ya consumidos (`.deb`, `.tar.gz`) y el instalador `.exe` incompatible son voluminosos y de bajo retorno práctico.

Lo que puede ahorrar más trabajo es: las fuentes AI/SVG y PDF de contraportadas; el job completo con brief, estado, cambios y script; el input y las corridas de ARICA; las decisiones curatoriales humanas; `projection3/MANIFEST.json`; y los hashes/manifests de evidencia. Esos archivos permiten retomar, comparar o demostrar algo sin rehacer el proceso.

No clasifiqué como basura las bases, packs Git, transcripciones ni snapshots: pueden parecer técnicos, pero contienen procedencia y decisiones. Tampoco clasifiqué como “entrega confirmada” el job de contraportadas: sus propios documentos dicen `pendiente_datos`.

**Orden de prioridad:** proteger fuentes gráficas y ARICA; conservar rollback y decisiones; usar manifests para navegar; revisar luego logs/cachés/binarios; y solo considerar eliminación después de verificar cobertura, regenerabilidad y ausencia de valor probatorio. Esta separación es conceptual: no se movió ni eliminó ningún archivo.

## Resultado de la investigación

El job de contraportadas está en `pendiente_datos`: faltan cliente, proyecto, medidas, productos y aprobación textual. Sus fuentes AI/SVG ahorran rehacer diseño, pero no prueban una entrega cerrada.

En ARICA, `observation.json`, `units.json` y `projection.json` son idénticos entre las tres corridas grandes; la observación además coincide con el input. Las diferencias aparecen en `practice`, `product-plan` y `portfolio-dossier`. Se reutilizó una base común y se modificaron capas interpretativas; no son tres observaciones independientes.

La primera ronda visual registra 40/40 decisiones humanas, 106 historias candidatas y 155 carruseles. El conjunto sin episodio confirmado reúne 18 medios y 11 rechazos: conserva criterio y abstención, no obras confirmadas.

En DREF, el `cue_map` difiere solo en bytes, no estructuralmente; `misionar` aparece en reconstrucciones, no como video original probado dentro del archivo; y Escarlata prueba la colaboración pública, pero no el binding físico con un video local.

### Candidatos transversales

`ARICA-FONDART-2027`, `2026-07-05_contraportadas` y `primera-ronda-visual-20260807` son los tres candidatos con mayor potencial de ahorro de trabajo fuera del caso DrefQuila.

### Investigación de los nuevos candidatos

`mak_knowledge.db` contiene 49 tablas, 42.355 artefactos, 8.273 elementos de clasificación, 8.331 entidades, 6.058 relaciones, 98.223 eventos temporales, 30.985 imports Python, 124 enlaces de catálogo y 44 registros de proyecto. No es un cache vacío. Conserva estados `observed`, `candidate` y `human_attested`, pero sus tablas de memoria de archivo están vacías y mezcla varias raíces: es conocimiento estructurado, no estado actual completo.

`claude-codex-mak-20260815.sqlite` contiene 1.028 commits, 9.054 relaciones archivo-commit, 213 acciones Codex, 508 seguimientos de ideas, 1.548 de propuestas, 3.702 enlaces pregunta-respuesta, 22.632 candidatos y 18.930 señales. Sus tablas de memorias y actividad Claude están vacías; vale por la reconstrucción del proceso, no como memoria consolidada.

`projection3/MANIFEST.json` registra 5.426 rutas entre tres orígenes: 3.087 iguales, 813 variantes preservadas y 2.366 archivos variante. Ahorra la comparación manual, pero no decide qué versión es correcta.

La revisión de candidatos transversales produjo una corrección: `FLYERS8.ai` no es un AI nativo verificable por su extensión; `file` lo identifica como PDF de 19 páginas con recursos embebidos. Su valor puede ser alto como composición/render, pero no debe asumirse que conserva edición Illustrator sin abrirlo en una herramienta compatible. `claude_code_web_codex.sqlite` contiene 58.879 turnos, 926 commits, 8.342 asociaciones archivo-commit, 4.405 enlaces pregunta-respuesta, 30.800 candidatos y 26.395 señales; es una fuente de arqueología de proceso. `CAPACIDADES.md` es un mapa operativo de 2026-08-09 que documenta consumidores y mediciones; ahorra reconstrucción, pero está explícitamente fechado y no es estado actual.

### Comprobación de exclusividad

La investigación de existencia cambia el dictamen: `mak_knowledge.db` **sí existe fuera de `_archive`** en `/home/mak/data/mak_knowledge.db` y su SHA-256 coincide exactamente con la copia archivada. En cambio, no encontré fuera de `_archive` otra copia de `claude-codex-mak-20260815.sqlite` ni de `projection3/MANIFEST.json`. Por tanto, solo los dos últimos son exclusivos de `_archive` por nombre/ruta conocida; la base MAK es un snapshot duplicado.

### Tres candidatos de seguimiento

1. **`cue_map_dref.json`**: única divergencia byte a byte dentro del kit DREF CHOCOLATE; comparar sus cues puede revelar un cambio operativo real.
2. **`DREFGIRA/misionar`**: única coincidencia directa entre una carpeta reconstruida y una canción verificable; conviene separar obra, show y assets auxiliares.
3. **`Escarlata (Remix)`**: colaboración respaldada por Apple Music y YouTube, pero sin vinculación física definitiva con los videos locales.
