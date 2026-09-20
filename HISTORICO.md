# HISTORICO.md — historia condensada de vibecodeine

**Este archivo no contiene instrucciones vigentes ni una cola de trabajo.** Su única función es explicar de dónde viene el sistema sin obligar a un agente a recorrer cientos de Markdown históricos. El presente está en `REAL_INFO.md`; el detalle forense permanece recuperable en Git.

## Por qué se creó este consolidado

Al 2026-09-20 el árbol contenía **1.025 archivos `.md` (~8,8 MB)**. La familia más grande era `context-history/` con **455 Markdown**, además de handoffs archivados, sesiones recuperadas, PHASE reports, cierres de sesión y varios documentos raíz que se describían a sí mismos como “current”, “canonical”, “master” o “next”.

El fallo práctico era peor que el volumen: distintas generaciones de documentos enviaban al agente a rutas incompatibles o inexistentes, entre ellas `AGENTS.md`, `agents.md`, `CLAUDE.md`, `STATUS.md`, `context/LAST_HANDOFF.md` y `context/HANDOFF_HISTORICO.md`. Tras merges grandes, el árbol llegó a conservar punteros a un `AGENTS.md` que ya no estaba en `main`.

Resultado: cada agente reconstruía una versión distinta del proyecto y heredaba “siguientes acciones” de épocas diferentes.

La corrección de 2026-09-20 es estructural:

```text
AGENTS.md
  -> REAL_INFO.md
       -> código / datos / medición actual

HISTORICO.md
  -> sólo si hace falta explicar el pasado
```

## Línea de tiempo condensada

### 2026-07 — nacimiento del organismo y reglas culturales

MAK se formuló como un organismo Linux de trabajo: investigación, generación/código, lenguaje, plataforma y puentes hacia dispositivos. La idea central era que la infraestructura debía convertir trabajo de agentes no confiables en resultados verificables.

Quedó fijada una regla duradera de idioma: operador y productos humanos en español correcto; código e identificadores nuevos orientados a inglés. La “tilde” quedó como señal cultural y como recordatorio de que los outputs humanos no deben degradar el idioma.

A fines de julio se formuló una visión del archivo artístico como sistema vivo: separar sustrato/datos de sus “pieles”, tratar la curaduría automática como propuesta verificable y no como verdad, y valorar más los gates y la trazabilidad que la brillantez de un modelo.

### 2026-08 — crecimiento, arqueología y consolidación

El sistema creció en varias direcciones: MAK, FLUJO, RD, iskvw, Research, Curatoria, Codex, datos, herramientas visuales y XIO. Se multiplicaron scripts, bases, worktrees y reportes de fase.

Entre el 24 y el 29 de agosto el foco pasó a reconstruir archivos por evidencia: observación física, memoria temporal, relaciones candidatas, unidades de proyecto provisionales y proyecciones Project IR. Se hizo explícita una distinción que sigue siendo importante: **observar un archivo no equivale a inferir una obra o intención**.

En paralelo se midió y consolidó la máquina MAK. Apareció una lección repetida: los documentos con estados narrativos (“VIVO”, “activo”, números de tests, rutas sin raíz) se pudren más rápido que los instrumentos que pueden volver a medir.

Esta época generó la mayor parte de los PHASE reports y del material bajo `context-history/`. Son evidencia de cómo se llegó a decisiones, no tareas actuales.

### 2026-09-02 — frontera IRIS / portafolio

Se aclaró un error que varios agentes repetían: IRIS es el sistema interno de orden y relación del archivo; el portafolio/iskvw es una salida distinta. Una ruta interna llamada `/portafolio/` o un editor compartido no cambia esa frontera conceptual.

También se auditó que basenames repetidos (`editor.html`, hubs, copias de worktrees) no prueban autoridad. La autoridad debe derivarse del consumidor real y la ruta servida.

### 2026-09-03 — intento de contrato único

El operador decidió eliminar la proliferación de contratos para agentes y quedarse con un único `AGENTS.md`. `LAST_HANDOFF.md` debía quedar sólo como historia y las decisiones actuales no debían depender de narrativas de estado.

La idea era correcta, pero el repositorio siguió conservando muchos documentos antiguos con vocabulario de autoridad. Eso dejó una contradicción: “un solo contrato” coexistía con decenas de archivos que todavía decían `current`, `canonical`, `master` o `next action`.

### 2026-09-06 a 2026-09-10 — topología y unión de ramas

Se retiró un guardián de topología que ya no representaba el sistema. Después se integraron MAK y FLUJO en `main` como una base Git conjunta, conservando sus carriles y hubs separados.

Un merge posterior reintrodujo piezas retiradas (topología/handoff) sin una decisión nueva; se corrigió. Lección: **un merge puede revivir documentación muerta**, por lo que la mera presencia de un archivo después de un merge no demuestra que haya recuperado autoridad.

### 2026-09-17 — XIO y la autoridad por consumidor

Una sesión retiró copias duplicadas de XIO y apuntó consumidores hacia el repositorio/ruta considerada vigente en ese momento. El gran merge del 2026-09-20 volvió a dejar `xio/` presente en el árbol integrado.

Por eso la conclusión durable no es “XIO vive aquí” ni “XIO vive afuera”: es **comprobar el consumidor y la rama actual antes de actuar**. Los runbooks fechados no deciden la autoridad de hoy.

### 2026-09-18 — ciclo Azure/DeepSeek

Se integraron herramientas y pruebas relacionadas con Azure y una calibración de delegaciones a DeepSeek. El aprendizaje durable fue metodológico:

- buscar antes de construir;
- ejecutar los tests generados, no confiar en su apariencia;
- una abstención correcta puede ser mejor que inventar;
- un registro manual de herramientas acumula fantasmas;
- separar existencia de un recurso de su uso real.

Los números y recursos concretos de esa sesión son históricos y no deben usarse como estado actual sin volver a medir.

### 2026-09-20 — gran integración y quiebre documental

`main` recibió una serie de merges de MAK, FLUJO, XIO, ramas de reparación y worktrees. El resultado técnico integró mucho trabajo, pero la superficie documental quedó incoherente: desaparecieron entradas raíz como `AGENTS.md`/README mientras otros documentos seguían ordenando leerlas.

Este es el origen inmediato del problema “cada Codex se pierde y tengo que repetir lo mismo”.

La corrección actual crea nuevamente una sola puerta de entrada y separa de forma explícita **verdad vigente** de **historia**.

## Decisiones históricas que explican el presente

Estas decisiones no deben reabrirse por accidente:

- MAK, FLUJO y la base integrada no son sinónimos.
- IRIS no es el portafolio público.
- La autoridad se prueba por consumidores/contratos/medición, no por nombres de archivo.
- Los facts cambiantes se miden; no se congelan en prosa.
- Los resultados de agentes se verifican.
- Una inferencia no se promueve a hecho por conveniencia.
- El historial existe para recuperar contexto, no para asignar trabajo al próximo agente.
- Los merges no autorizan por sí solos el regreso de una regla retirada.

## Familias históricas absorbidas conceptualmente por este archivo

Para orientación humana, este resumen reemplaza como lectura inicial a las antiguas familias:

- `context-history/**`;
- `context/HANDOFF_HISTORICO.md` y antiguos `LAST_HANDOFF.md`;
- `context/PHASE*.md`, índices y consolidaciones de fases;
- `docs/handoffs/archive/**`;
- `docs/recovered/**`;
- cierres de sesión y transferencias de agentes;
- `GENESIS.md`, `PROYECCION.md`, `NEXT.md` y memorias narrativas;
- planes fechados que ya tienen código, commits o decisiones posteriores.

El detalle no se pierde aunque esos documentos se retiren de la superficie activa: Git conserva sus versiones y permite recuperar una ruta o fecha concreta.

## Cómo hacer arqueología sin contaminar el presente

1. Empieza por este resumen.
2. Identifica la fecha, subsistema o decisión.
3. Usa `git log --all -- <ruta>` o busca el commit por fecha/mensaje.
4. Lee sólo la versión histórica necesaria.
5. Contrasta cualquier afirmación con el árbol y runtime actuales antes de reutilizarla.

Nunca copies un “next action” histórico a la tarea actual sólo porque fue lo último escrito en una sesión antigua.

## Lección documental final

El problema no era que faltara memoria; había demasiada memoria sin jerarquía.

La arquitectura documental deseada es deliberadamente pequeña:

- **`README.md`**: puerta humana mínima.
- **`AGENTS.md`**: contrato de arranque del agente.
- **`REAL_INFO.md`**: modelo mental vigente.
- **`HISTORICO.md`**: pasado condensado.

El resto de Markdown sólo existe por dominio o como evidencia específica, y no compite por autoridad global.
