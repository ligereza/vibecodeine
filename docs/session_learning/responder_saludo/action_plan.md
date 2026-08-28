# Plan de acción de MAK

## Objetivo operativo

Cerrar un vertical reusable y autónomo:

```text
archivo artístico real
  -> evidencia reproducible
  -> práctica y relaciones provisionales
  -> oportunidad versionada
  -> investigación dirigida por valor de información
  -> plan común
  -> dossier/portfolio, postulación y research brief
  -> episodio y siguiente acción
```

El primer producto no es una base de datos ni una cola de preguntas. Es un
borrador cultural auditable que puede usar evidencia suficiente, declarar
huecos sin inventar y continuar con un plan de investigación cuando la
postulación todavía no es legítima.

## Arquitectura única

MAK debe conservar seis componentes, todos sobre los contratos y superficies
existentes:

1. **Observación y memoria física.** El observer es el único lector físico. La
   memoria conserva artifacts físicos, estados por snapshot, observations,
   hashes y replay. No decide obra.
2. **Reconstrucción estructural.** Stage 2A–2D transforma el replay en
   features, candidatos, unidades balanceadas y Project IR provisional. No
   resuelve autoría ni crea un portfolio.
3. **Estado epistemológico.** Practice evidence, opportunity constraints,
   fit, possibilities y evidence return mantienen separadas práctica interna y
   oportunidad externa. El binding explícito es la frontera.
4. **Operating world y research frontier.** Las capacidades existentes se
   describen por precondiciones, efectos, costo, validadores y evidencia. La
   búsqueda elige sondas y compone acciones; el router sólo sirve como
   proyección acotada, no como modelo central.
5. **Common product compiler.** Portfolio dossier, application package y
   research brief derivan del mismo product plan. El plan produce variantes
   draftable, blocked o research-first y no publica ni envía.
6. **Episode/learning controller.** Decision, observation y outcome se separan
   en episodios. El aprendizaje queda limitado a ranking, atención, VOI y
   query selection; la autonomía devuelve una acción plan-only y finita.

No se debe crear una base, Hub, lane, framework o `experiments/` paralelo.
Cuando un órgano legacy tenga drift, se documenta el borde y se usa el
contrato puro aceptado alrededor de él.

## Pisos y gates

### Piso A: memoria observable

**Dependencias:** observer, archive memory y replay.

**Gate:** batch estricto, archive aislado, idempotencia, duplicate bytes
separados, touch estable, symlink/error/null-content preservados, sin escritura
de artwork.

**Métrica:** cero pérdida, cero duplicados semánticos, replay byte-identical.

### Piso B: reconstrucción provisional

**Dependencias:** Stage 2A, 2B, 2C, 2D.

**Gate:** todos los endpoints físicos resuelven; candidatos tienen evidencia;
unidades mantienen assigned/ambiguous/unassigned balance; Project IR mapea cada
unidad una vez; truth promotions es cero.

**Métrica:** artifact conservation = 1.0; relation IDs únicos; deterministic
replay = 1.0; porcentaje de refs sin destino = 0.

### Piso C: práctica y oportunidad

**Dependencias:** accepted Project IR, practice state, opportunity packet y
source validity.

**Gate:** sólo `requirement_ids` explícitos enlazan ambos lados; fuentes
observadas o stale abstienen; hard gates faltantes no se transforman en
elegibilidad.

**Métrica:** cada requirement tiene estado `supported`, `missing`, `unknown` o
`contradicted`; cero claims web promovidos a practice evidence.

### Piso D: posibilidad, research y producto

**Dependencias:** fit, program candidates, possibility field, frontier jobs,
triangulation, evidence return y product plan.

**Gate:** posibilidades rivales se preservan; jobs quedan
`planned_not_dispatched`; research retorna evidencia aditiva; portfolio puede
ser interno aunque application esté bloqueada; ningún asset se publica por
default.

**Métrica:** cobertura de requisitos, cantidad de narrative atoms soportados,
gaps explícitos, research jobs con VOI y cero false-ready products.

### Piso E: episodios y aprendizaje

**Dependencias:** product episode, learning evaluation y autonomy plan.

**Gate:** outcome ausente no es negativo; source refs de outcomes tienen hash;
training/promotion/database write/publication/submission/dispatch permanecen
falsos salvo autorización explícita posterior.

**Métrica:** episodios replayables, holdout por archive/person/project,
calibración de ranking/VOI y mejora de decisión operativa sin cambios en verdad
autoral.

## Primer corte ejecutable

El siguiente corte no agrega arquitectura. Usa las salidas temporales del
piloto ARICA/Fondart ya reportadas por el CURRENT y las convierte en evidencia
reproducible:

1. conservar en un root explícito y acotado un manifest de hashes y schemas
   para el Project IR y practice state del piloto;
2. ejecutar el job oficial de validez Fondart con `source_policy=official-source-only`
   y devolver un receipt triangulable;
3. proyectar los testigos técnicos C04–C06 a evidence interna, manteniendo
   separados `c04`, `c05`, `c06` de evidencia web;
4. recomputar desde fit el mismo product plan;
5. comprobar que el dossier gana sólo claims respaldados, que application
   sigue bloqueada si corresponde y que autonomy produce una única siguiente
   acción acotada;
6. repetir exactamente el mismo recorrido sobre un segundo archivo sin
   introducir el nombre ARICA, MYRA, RAYU o ISKVW en el código.

El primer corte debe ser read-only sobre inputs y usar sólo un output root
derivado. La persistencia durable debe guardar manifests, hashes y contratos,
no copias masivas de media.

## Métricas de aceptación

MAK v1 se considera logrado cuando, en dos archivos de artistas distintos y sin
etiquetado nuevo del usuario:

- el observer y replay conservan el 100% de los artifacts observados;
- duplicate bytes no colapsan paths físicos y los estados por snapshot son
  reproducibles;
- al menos el 95% de candidatos emitidos tienen endpoints y evidence refs
  resolubles; el resto queda explícitamente skipped/unresolved;
- cada artifact termina assigned, ambiguous o unassigned exactamente una vez;
- cada unidad provisional produce como máximo un Project IR record;
- el practice state contiene claims sólo con evidence refs internas y cero
  promociones de verdad;
- el sistema genera un dossier interno con assets y provenance reales, aunque
  la aplicación esté bloqueada;
- cada gap relevante genera una sonda o razón de abstención, no una pregunta
  obligatoria al usuario;
- el producto conserva enlaces desde texto/asset/requirement hasta evidencia y
  decisión;
- un segundo replay del mismo input es byte-identical;
- un split por archive/person/project supera un baseline vacío en recuperación
  de relaciones fuertes o, si no lo supera, mata la técnica en vez de
  promoverla;
- la autonomía produce una acción plan-only finita y no ejecuta publicación,
  envío, dispatch ni entrenamiento.

Los umbrales son gates de decisión, no promesas de que todo archivo producirá
un portfolio completo. Un archivo con poca evidencia puede producir un dossier
research-first válido.

## Experimentos falsables antes de ML complejo

### Experimento 1: clasificador contra operating world

Construir sobre los mismos casos una baseline de label única y un planificador
de capacidades. El caso debe exigir al menos dos acciones, una precondición y
una rama imposible. Medir exactitud de la primera acción, validez de la
secuencia, detección de imposibilidad y trazabilidad. Si la tarea sólo exige
una acción fija y ambos empatan, el planificador no queda justificado todavía.

### Experimento 2: representación contra nombre de archivo

Ocultar relaciones fuertes en un split por proyecto y comparar basename/path,
metadata, embeddings congelados, kNN y un modelo pequeño de ranking. Medir
recall top-k, precision, calibration y fuga entre snapshots. Si embeddings no
superan el baseline o sólo funcionan dentro del mismo proyecto, no se añade
fine-tuning.

### Experimento 3: producto contra reporte

En dos archivos reales, comparar un reporte de inventario con el common product
plan. Medir cobertura de assets, claims soportados, gaps, requisitos trazables,
variantes producidas y tiempo de preparación. El producto gana sólo si entrega
una selección/brief utilizable sin subir false claims.

### Experimento 4: research como feedback

Tomar una oportunidad con fuente `observed_local`, generar jobs técnicos,
triangular un receipt oficial y recomputar. El resultado esperado no es
“application ready” automático: es una reducción medible de gaps, o una razón
mejor para seguir bloqueado. Si el receipt contamina practice evidence, el
experimento falla.

## Condiciones de abstención

MAK continúa produciendo cuando puede, pero se abstiene de afirmar o ejecutar
cuando:

- el input no cumple el contrato canónico y no existe un adaptador aceptado;
- la evidencia requerida no tiene endpoint o hash verificable;
- dos unidades compiten por el mismo artifact sin topology suficiente;
- el source gate de la oportunidad es observado, stale, unknown o contradicho;
- falta un hard gate o documento obligatorio;
- una relación depende sólo de basename, coexistencia o similitud sin soporte;
- un output no tiene binding nativo, manifest o publicación;
- el producto requeriría inventar biografía, intención, serie, autoría o
  representatividad;
- no hay holdout independiente para promover una técnica de aprendizaje;
- el siguiente paso implicaría escritura externa, dispatch, publicación,
  submission, entrenamiento o modificación de inputs.

La abstención correcta sigue incluyendo el mejor producto privado posible, la
razón estructurada, la evidencia ya disponible y una sonda interna de bajo
costo. No se transforma en una conversación obligatoria con el artista.

## Gestión del trabajo y de los legados

- **C02–C08:** conservar como regresiones, testigos y límites; no convertirlos
  en una arquitectura paralela.
- **Copilot/router:** conservar como catálogo o selector de capacidad mientras
  no se demuestre que debe ser reemplazado; no usarlo como target de aprendizaje
  universal.
- **active_policy:** mantener congelada hasta contar con episodios independientes
  y evaluación por archive/person; no promover por métricas de fixtures.
- **19 lanes:** conservar como mapa de investigación read-only; no abrir nuevas
  lanes hasta que una conexión existente consuma un contrato real.
- **Handoffs:** un solo `context/LAST_HANDOFF.md`; estos documentos preservan
  aprendizaje de la sesión, no crean una segunda autoridad operativa.
- **ARICA scripts:** mantener como evidencia de caso; no usarlos como productor
  general ni como excepción del pipeline.

## Próxima acción concreta

Cerrar primero el gap de evidencia del source gate Fondart y el gap de
proyección C04–C06. Después ejecutar el mismo recompute desde fit con los
hashes del Project IR/practice state y medir si aumentan los claims respaldados,
si disminuyen los gaps justificados y si la aplicación sigue correctamente
bloqueada o pasa sus hard gates. Sólo después buscar un segundo archivo.

El criterio de avance no es que MAK diga más. Es que pueda decir más cosas
correctas, producir un producto más útil y conservar exactamente por qué las
dijo.
