# Teoría de capacidades de MAK

## Tesis

MAK no es la suma de sus scripts ni el inventario de `CAPACIDADES.md`. Es un
metabolismo: observa materia, conserva identidad y procedencia, convierte
observaciones en conocimiento provisional, somete ese conocimiento a gates,
produce proyecciones útiles y aprende sólo de episodios verificables.

La unidad de salud del sistema no es “existe un archivo” sino:

```text
productor -> contrato -> consumidor -> evidencia -> gate -> salida verificable
```

Un organismo puede tener una herramienta cableada y aun no tener capacidad
integrada. Una capacidad integrada puede producir conocimiento operativo sin
producir un producto público. Un producto verificable necesita además una
proyección válida, privacidad/visibilidad, revisión y una autoridad de salida.

## Cuatro estados que no deben mezclarse

### Herramienta disponible

El código y su CLI existen y pueden importarse o ejecutarse. Esto prueba
disponibilidad física, no que el consumidor correcto la llame ni que el runtime
esté vivo. Ejemplos: `research_source_capture.py`, `deep_learning_gate.py` y
`gen_vinculos_iskvw.py`.

### Capacidad integrada

Existe una entrada aceptada, una implementación, un consumidor real y una
salida validada. Los Pisos 1–5 alcanzan este nivel en sus contratos puros:
fit, possibility, frontier, evidence return, product plan y autonomy. La
integración sigue siendo epistemicamente limitada: abstain, unknown y
candidate son salidas válidas.

### Conocimiento operativo

Es una afirmación o relación que el sistema puede transportar con identidad,
fuente, hash, estado, visibilidad, alternativas y próxima acción. El C05
conoce un evento `EXPORTS_TO` apoyado para RAYU/GLB; no conoce entrega,
publicación, autoría o intención. El estado correcto es más pequeño que la
narrativa tentadora.

### Producto verificable

Es una proyección para un consumidor concreto: dossier interno, paquete de
research, dashboard RD, archivo ISKVW o una application draft. Debe declarar
qué claims, assets, requisitos y fuentes entraron, qué quedó fuera y qué
controles impiden publicar o enviar. `draftable` nunca significa
`submission_ready`.

## Metabolismo de archivo a acción

El circuito vivo actual es:

```text
archivo físico
  -> observer/memory/reconstruction
  -> Project IR y practice evidence
  -> opportunity constraints + explicit bindings
  -> fit
  -> candidate/evaluator/possibility
  -> research frontier
  -> triangulation/evidence return
  -> common product plan
  -> dossier/application/research
  -> bounded episode/autonomy
```

El circuito se rompe deliberadamente cuando falta una fuente, una relación, un
holdout o un consumidor. Esa ruptura no es un bug que deba ocultarse. Es el
metabolismo evitando convertir materia no verificada en hecho.

## Órganos y autoridad

Hub, Research, Curatoria, Portfolio/ISKVW, RD y la superficie Copilot/Codex
son órganos con responsabilidades diferentes. Comparten Project IR,
procedencia y contratos, pero no comparten automáticamente autoridad.

`triangular_fichas.py` es un patrón fuerte para RD: compara fuentes, conserva
dudosos y exige evidencia. No debe transformarse en autoridad para claims
artísticos. `gen_vinculos_iskvw.py` demuestra otra disciplina útil: declara
que un vínculo nace de conceptos compartidos; no lo vende como similitud.
Research aporta evidencia ambiental y de oportunidad; sólo un job con scope
practice y referencias de artefactos existentes puede proponer evidencia de
práctica.

Copilot sirve para coordinar contexto, prompts, rutas y handoffs. No es un
órgano de verdad. Su integración correcta consiste en entregar el contrato,
el dueño, el consumidor y el gate; no en permitir que un modelo rellene los
campos ausentes.

## Cómo evitar el loop de bugs

El sistema debe preferir un corte vertical pequeño sobre otra capa:

1. capturar una fuente oficial y una evidencia de archivo ya existente;
2. proyectarlas por los contratos aceptados;
3. medir qué requisito dejó de ser unknown;
4. recomputar desde fit, no reescribir el pasado;
5. mantener publicación, submission, dispatch, promotion y training cerrados.

Las herramientas REVISAR no se recuperan por nostalgia. Se recuperan sólo si
se identifica un productor, un consumidor, un contrato, una prueba y una
salida que no duplique una capacidad viva. Si no, permanecen como evidencia
histórica.

## Criterio de aprendizaje

El aprendizaje útil es ranking, routing, prioridad y selección de la próxima
pregunta. No debe aprender hechos desde sus propios drafts, ni autoría desde
embeddings, ni una etiqueta negativa desde abstention. `deep_learning_gate`
debe seguir siendo un guardián de labels, holdout, agrupación anti-leakage y
validación. Mientras no haya holdout independiente por proyecto/identidad,
la salida correcta es shadow o abstain.
