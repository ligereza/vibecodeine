# Guía de continuidad: análisis de sesiones Claude y Codex

> **Propósito:** continuar el análisis histórico e interpretativo sin tratar un
> handoff, una conversación o un informe generado como la verdad completa.
>
> **Estado:** guía metodológica; los resultados deben conservar fuentes,
> hashes, método y nivel de confianza.

## Objetivo

Reconstruir cómo MAK llegó a su estado actual: qué decisiones lo formaron, qué
alternativas fueron abandonadas, qué preguntas no fueron respondidas, qué
propuestas se ejecutaron sin validación y dónde se repitió trabajo evitable.

El análisis relaciona cuatro capas:

1. **Conversación:** preguntas, propuestas, correcciones, interrupciones,
   pausas, hotspots de frustración y lenguaje de cierre.
2. **Estado operativo:** archivos, procesos, servicios, tests, puertos, hashes y
   productos generados.
3. **Esfuerzo temporal:** intervalos entre interacciones, actividad, descanso y
   costo de máquina cuando sea medible.
4. **Genealogía material:** sesiones Claude, memorias Codex, archivos
   recuperados, duplicados, eliminaciones y productos derivados.

El resultado debe ser un grafo de procedencia y un conjunto de hipótesis, no un
diagnóstico psicológico ni una nueva regla universal.

## Fuentes identificadas

### Claude

- Origen Windows: `C:\Users\issvk\claude_sesiones_recuperadas`
- Archivo MAK: `/home/mak/WIN/claude_sesiones`
- Corpus estructurado: `docs/recovered/claude_sessions_2026-08-12/`
- Importador: `tools/recovered/import_claude_sessions.py`
- Material recuperado: Fondart, entidades RD, testeos, Chemsex, relaciones,
  catálogos, fuentes, propuestas e integración.

### Codex

- Memoria Windows: `C:\Users\issvk\.codex`
- Archivo MAK: `/home/mak/WIN/codex`
- Implementación del organismo: `cultura/mak_codex/`
- Superficies relevantes: `agente_libre.py`, `codex_lib.py`,
  `interfaz_codex.py`, `motor_semantico/`, `debug.py`, `generar.py` e
  `iconos.py`.

### Arqueología y esfuerzo

- `C:\Users\issvk\Downloads\arqueologia.py`
- `C:\Users\issvk\Downloads\esfuerzo.py`
- `C:\Users\issvk\Downloads\ultimochat.txt`
- `cultura/mak_plataforma/capataz.py`
- `cultura/mak_plataforma/metricas_capataz.py`
- `tools/inferential_archaeology.py`, si existe en el checkout activo
- `_logs/cauce_director/` y registros de reconciliación

Los archivos de Downloads son fuentes históricas, no autoridad de producción.
No deben sobrescribirse ni interpretarse sin registrar su origen.

## Herramientas y función

### Importación de sesiones

`import_claude_sessions.py` normaliza material recuperado, permite deduplicar y
conservar la procedencia. No demuestra que una interpretación de Claude fuera
verdadera.

### Arqueología inferencial

`arqueologia.py` y `inferential_archaeology.py` extraen eventos y relaciones
entre sesiones, archivos, propuestas, reglas y estados. Sus marcadores son
heurísticos: `PERO!!!`, `ya lo hiciste` o `queda pendiente` son candidatos, no
diagnósticos.

### Esfuerzo y Capataz

`esfuerzo.py` mide proxies de ritmo, tiempo y costo. `capataz.py` y
`metricas_capataz.py` permiten contrastar actividad declarada con actividad
observada. El tiempo no equivale a valor y una respuesta del agente no equivale
a trabajo completado.

### Evidencia determinista

Usar existencia de archivos, hashes, JSON válido, tests, imports, procesos,
puertos y respuestas reales. Un JSON actualizado, un Mermaid o una respuesta
segura no son evidencia suficiente por sí solos.

## Método de análisis

### 1. Inventario y deduplicación

Registrar `source_path`, tipo, tamaño, fecha, hash, estado (`raw`, `derived`,
`duplicate`, `report`) y relación con su original. Deduplicar por hash, no solo
por nombre. No contar dos veces una sesión que existe como JSON bruto y como
corpus importado.

### 2. Normalización de eventos

Usar campos en inglés/ASCII para datos de máquina:

```text
event_id, source_id, session_id, timestamp, actor, event_type,
question_or_claim, action_taken, evidence_path, status, confidence
```

La interpretación humana puede mantenerse en español con diacríticos.

### 3. Contrastar lenguaje y hecho

Comparar cada declaración con la superficie material:

- `done` contra archivos modificados y tests;
- `integrated` contra presencia y hash;
- `no_pending` contra preguntas y tareas abiertas;
- `phase_complete` contra un producto o gate real;
- `no_processes` contra inspección de procesos.

Registrar contradicciones, no escoger automáticamente la frase más segura.

### 4. Clasificar preguntas e ideas

Separar `seed`, `hypothesis`, `project`, `product`, `rejected`, `duplicate` y
`unanswered`. “Dame una propuesta” no es un proyecto: para serlo necesita
evidencia, alcance, responsable y acción acotada.

### 5. Medir interacción sin diagnosticar

Medir intervalos, interrupciones, loops autónomos, correcciones repetidas,
frases de cierre, trabajo posterior a una afirmación de finalización y cambios
de intensidad como hotspots contextuales. Informar “candidate hotspot” o
“false-closure pattern”, nunca una intención no demostrada.

### 6. Triangular

Un hallazgo importante debe tener al menos dos capas independientes. Una
afirmación de finalización más un archivo modificado no basta hasta que exista
test, hash o comprobación runtime. Un hotspot gana fuerza si coincide con un
artefacto roto y retrabajo posterior.

### 7. Conservar caminos alternativos

Para cada decisión registrar:

```text
decision_id, chosen_path, discarded_paths, reason, cost_of_reversal,
downstream_effects
```

Así se estudia el “multiverso” de posibilidades sin inventar historias ni
clonar repositorios.

## Entregables para completar el análisis

1. `session_inventory`: sesiones y fuentes deduplicadas.
2. `question_ledger`: preguntas respondidas, evitadas, repetidas y abiertas.
3. `idea_catalog`: ideas por estado y dominio (`artistic`, `system`, `research`,
   `rd`, `portfolio`, `cross-domain`).
4. `decision_graph`: decisiones, alternativas, archivos producidos y reversas.
5. `effort_report`: ritmo, pausas, loops autónomos y energía, sin confundirlos
   con valor artístico.
6. `closure_audit`: afirmaciones del agente comparadas con evidencia.
7. `triangulation_report`: hallazgos fuertes, débiles y no verificables.

Cada salida debe indicar fuentes, fecha, método, confianza y omisiones. Los
resúmenes no reemplazan las sesiones brutas.

## Límites

- No tratar un handoff o plan histórico como regla universal.
- No contar cachés de plugins como sesiones.
- No inferir emoción, manipulación o engaño desde una frase aislada.
- No llamar evidencia a un informe generado sin comprobación.
- No crear otra base o framework antes de revisar importadores, catálogos,
  SQLite y schemas existentes.
- No borrar contradicciones ni trabajos fallidos: marcarlos con procedencia y
  estado.

## Inicio recomendado

Comenzar con inventario y deduplicación. Luego producir `question_ledger` y
`closure_audit` antes de proponer nuevas herramientas. La meta es recuperar la
inteligencia ya presente en el trabajo de Claude y Codex, no crear una capa que
la oculte.
