# Teoría de sistema de control distribuido para MAK

## Tesis

MAK no es una cadena que convierte archivos en productos. Es un sistema distribuido de control epistemico que conserva varias autoridades, permite proponer bajo incertidumbre y solo avanza cuando una transición tiene evidencia y un consumidor. Su variable controlada no es la cantidad de outputs, sino la distancia entre lo que el sistema afirma y lo que sus fuentes permiten afirmar.

El ciclo fundamental es:

```text
observar -> proponer -> refutar -> compilar -> evaluar resultado -> replanificar
```

Cada verbo pertenece a un rol distinto. Separarlos evita que el mismo componente invente una hipótesis, la valide con su propio output y la convierta en publicación. El inventario normativo está en [inventory.json](inventory.json) y el grafo de IDs, invariantes y fallos en [hashmap.json](hashmap.json).

## Tres topologías, una coordinación

MAK expone al menos tres proyecciones legítimas que no deben fusionarse por decreto:

1. El registro de departamentos define ownership y superficies: `rd`, `cultura` e `iskvw`.
2. La interfaz de Research representa el flujo material mediante seis órganos: `entrada`, `curatoria`, `research`, `codex`, `plataforma` y `emerge`.
3. El estado durable amplía el mapa de owners y consumidores con RD, Portfolio, Research, Curatoria, Cultura/MAK, Lenguaje/Vigía y Venue/SCD.

También existe un mapa de coherencia repo/runtime para cinco pares físicos. Ese mapa responde otra pregunta: si lo que corre coincide con lo que se lee en el baseline. No es un cuarto organigrama.

La reconciliación correcta es un crosswalk tipado:

- un departamento responde **quién conserva autoridad**;
- un órgano responde **qué transformación ocurre en el flujo**;
- un owner/consumer responde **quién produce y quién usa un contrato**;
- una pareja repo/runtime responde **qué código está efectivamente en ejecución**.

Declarar una sola lista “canónica” borraría información. Por eso `gap.topology_reconciliation` queda abierto y observable.

## Distribución de funciones de control

### Quién observa

`entrada` recibe obras, ideas y referencias. Curatoria y el observador de archivo convierten materia física en observaciones deterministas, memoria temporal, relaciones candidatas, unidades provisionales y Project IR. RD observa sus fuentes operativas sin perder autoridad propia. El estado de servicios se consulta en modo de solo lectura; una credencial o un archivo de configuración no prueba que un proveedor funcione.

El observador no interpreta intención artística. Un byte duplicado no fusiona identidades, un ancestro compartido no crea un proyecto y una dependencia no se vuelve miembro. La partición asignado/ambiguo/no asignado es parte del estado, no ruido que deba ocultarse.

### Quién propone

Copilot propone afinidades, ordenamientos, hipótesis curatoriales y candidatos de lectura. Sus contratos preservan evidencia, incertidumbre y `promotion=none`. Su función es ampliar el espacio de búsqueda y dirigir atención, no dictar verdad.

`cultura/mak_curatoria/triangular.py` cumple una función más acotada y anterior: transforma fichas RD con fecha e identificadores del evento en preguntas verificables sobre productoras. Su propia doctrina dice que no investiga y no despacha. Es un compilador de preguntas, no la triangulación que confirma respuestas.

El piso de posibilidades propone programas artísticos provisionales desde práctica y oportunidad. Un evaluador independiente puede aceptar, abstener o rechazar; una abstención posterior jamás revive un rechazo.

### Quién refuta

La refutación está distribuida en evaluadores independientes, validadores de contrato, triangulación de Research y checks foreground. La triangulación aceptada exige referencias explícitas y grupos de fuentes independientes. Sus resultados pueden ser apoyados, contradichos o no resueltos, pero mantienen promoción de verdad en cero.

Research observa el ambiente: vigencia de una convocatoria, requisitos o fuentes externas. Esa evidencia puede corregir el estado de oportunidad. No puede convertirse en evidencia de práctica, autoría o identidad artística salvo que un futuro contrato explícitamente practice-scoped nombre artefactos físicos existentes.

### Quién compila

Los compiladores no deciden verdad; proyectan contratos aceptados sin perder procedencia:

- reconstrucción compila observaciones en Project IR provisional;
- Piso 1 compila oportunidad, práctica y fit mediante bindings explícitos;
- Piso 2 compila el campo de posibilidades evaluadas;
- Piso 3 compila gaps en trabajos de investigación no despachados, triangulación y propuestas aditivas de retorno de evidencia;
- Piso 4 compila un único plan común y de él deriva dossier, aplicación y brief de research;
- Piso 5 compila episodios, evaluación de aprendizaje shadow y un plan finito de autonomía.

La regla del plan común es estructural. Portfolio y aplicación no pueden escribir narrativas, assets o requirements en silos porque entonces cada producto construiría una realidad distinta.

### Quién actúa

El plan de autonomía solo elige acciones `observe`, `research`, `recompute`, `compile`, `wait` o `abstain`. Todas llevan `dispatch=false`, `conductor_projection=plan-only`, `max_attempts=1` y condiciones de parada. Por evidencia consultada, no existe autorización para cablearlo directamente al Conductor.

El Conductor es un actuador separado: reclama un job, persiste resultado, exige `validated=true` y registra la transición. Para publicación, promoción, delivery o mutación de repositorio añade un gate explícito. La revisión del usuario puede ser opcional para la elaboración interna, pero la consecuencia externa no se deduce de esa autonomía interna.

## Abstención como señal de realimentación

En un pipeline convencional, abstener parece no hacer nada. En MAK, `abstain` mide una frontera de evidencia y genera una acción limitada: observar un artefacto faltante, verificar vigencia, investigar una contradicción, recomputar después de una ingesta aditiva o esperar un outcome abierto.

El piloto ARICA/Fondart demuestra esa dinámica. El sistema produjo un dossier interno útil, mantuvo bloqueada la aplicación, enumeró 16 constraints requeridos sin apoyo, nueve gaps del dossier y una acción de research no despachada. Ese resultado es mejor control que una falsa postulación lista.

La función objetivo para el siguiente ciclo no es forzar `pass`. Es aumentar evidencia explícita y reducir gaps justificadamente; un `abstain` mejor explicado también es progreso si conserva las autoridades correctas.

## Bucles de feedback

### Cierre de evidencia

Una carencia priorizada se compila en job no despachado. Una captura acotada produce fuentes y claims candidatos. La triangulación independiente devuelve `supported_candidate`, contradicción o `unresolved`. El retorno de evidencia queda `pending_ingestion`; solo después de ingesta aditiva se recomputa fit, posibilidad y productos. El loop se detiene si no cambia el hash, se agota presupuesto, se cierra el requirement o se consume el intento único.

### Reconstrucción de práctica

El archivo se observa sin mutarlo, se conserva la partición total de artefactos y se evalúan relaciones y unidades. Project IR solo admite `candidate` o `unknown`. El feedback es un evaluator independiente, no la cantidad de agrupaciones producidas.

### Aprendizaje shadow

Los productos pueden generar episodios y recibir outcomes externos verificados. Con una identidad estable, esos outcomes permiten señales de atención y ranking. Un episodio abierto no es negativo; un solo grupo de identidad no alcanza para una policy candidate; training permanece deshabilitado. El sistema nunca aprende verdad, autoría o identidad artística desde sus propios borradores.

## Lo que nunca puede autopromoverse

- Un nombre OCR, filename, timestamp, similitud visual o score no puede autopromoverse a identidad, autoría o relación canónica.
- Una hipótesis de Copilot, relación candidata, unidad provisional, programa o claim extraído no puede autopromoverse a hecho.
- Una fuente `observed_local`, `unknown` o `stale` no puede autopromoverse a `current_verified`.
- Evidencia de convocatoria no puede autopromoverse a evidencia de práctica.
- Un retorno de evidencia `pending_ingestion` no puede autopromoverse a estado aceptado.
- `draftable` no puede autopromoverse a publicado o enviado.
- Una acción rankeada no puede autopromoverse a dispatch.
- Un outcome abierto, una abstención o un fallo no puede autopromoverse a etiqueta negativa de entrenamiento.
- Un patrón aprendido no puede autopromoverse al router sin evidencia independiente suficiente.
- El sistema no puede validar su propia verdad, autoría o identidad usando outputs que él mismo escribió.

## Criterio de estabilidad

MAK es estable cuando cada transición tiene fuente, autoridad, contrato, evaluador, consumidor, estado y condición de parada; cuando una contradicción aumenta control en vez de ser borrada; y cuando ninguna salida interna cruza una frontera externa sin un gate y un receipt observables.

Esa estabilidad no exige certeza total. Exige que la incertidumbre permanezca tipada y que el sistema pueda continuar trabajando de manera acotada sin inventar evidencia.
