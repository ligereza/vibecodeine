# Teoría de sistema de MAK

## Tesis

MAK no es un organizador de carpetas, un clasificador de archivos ni un
asistente que espera etiquetas humanas. Es un sistema operativo autónomo y
reutilizable para archivos creativos: observa un archivo físico, construye una
memoria de evidencia, reconstruye unidades y relaciones, conecta esa práctica
con oportunidades externas y produce variantes auditables de portfolio,
dossier, postulación y research.

El resultado humano no es “saber qué es cada archivo”. Es poder trabajar con
una selección cultural defendible, textos calibrados, medios reales,
procedencia, huecos y próximos pasos sin rehacer manualmente años de trabajo.
La incertidumbre no desaparece: se convierte en estado operativo, redacción
prudente, menor prioridad, variante alternativa o investigación planificada.

ARICA, MYRA, RAYU e ISKVW son casos que ejercitan contratos. No son la unidad
arquitectónica, no son el portfolio completo y no deben generar excepciones
hardcodeadas.

## Por qué el problema fue mal entendido

El archivo artístico no es simplemente un conjunto de documentos empresariales.
Una obra terminada puede tener una imagen o video entregado, pero también una
escena de Blender, un proyecto de After Effects, un script, un manifest, una
secuencia de frames, una textura, una exportación, una versión corregida y una
publicación. El producto final es sólo una manifestación del proceso; el
archivo completo es la memoria operacional que permite relacionar esa
manifestación con sus fuentes y transformaciones.

Por eso la primera formulación como “elegir un `tool_id`” o como clasificación
multiclase sobre un catálogo fijo falló. Muchas decisiones son composicionales:
localizar un proyecto, validar sus recursos, elegir un renderer, producir una
imagen, comparar versiones, armar una secuencia, adaptar el texto a una
convocatoria y mantener las afirmaciones dentro de la evidencia. Una label no
representa precondiciones, efectos, costos, incompatibilidades ni acciones no
vistas en entrenamiento.

La alternativa más fuerte es aprender o representar el mundo operativo del
proyecto. En ese mundo existen capacidades, artefactos, estados, relaciones,
transformaciones, objetivos, restricciones, validadores, costos y sondas. Un
planificador puede derivar acciones; el router, si sigue siendo útil, es sólo
un selector acotado de capacidades disponibles.

## Separaciones que son invariantes

### Evidencia, conocimiento y política

La evidencia responde “qué fue observado y cómo”. Incluye bytes, hashes,
metadata, referencias nativas, logs, exports, manifests, publicaciones y
witnesses de transformación. La evidencia puede ser fuerte o débil, pero
siempre conserva su fuente y alcance.

El conocimiento semántico es una hipótesis estructurada sobre esa evidencia:
“este frame puede ser componente de este video”, “este script participa en este
export”, “estos archivos podrían pertenecer a una unidad local”. Tiene score,
alternativas, evidencia a favor, contradicción, missing evidence y próxima
sonda. No es automáticamente verdad artística.

La política operativa decide qué hacer dadas metas, restricciones y estado:
investigar una fuente, comparar dos hipótesis, compilar un dossier, esperar,
producir una variante o abstenerse de publicar. La política puede aprender
ranking, atención, valor de información y selección de consultas. No debe
aprender autoría, intención o verdad por retroalimentación de sus propios
borradores.

Si `semantic_rule` es incompatible con el router, eso no demuestra por sí solo
que el modelo conceptual esté mal. Puede ser un contrato de integración mal
diseñado. La prueba técnica es construir el mismo caso composicional con dos
representaciones: un clasificador de label única y un modelo de capacidades con
precondiciones/efectos. Si la decisión exige una secuencia, una rama imposible
o una capacidad ausente que la label no puede expresar, la insuficiencia es de
formulación. Si ambos expresan el caso pero divergen por campos, IDs o estados,
el problema es de contrato.

### Identidad física, contenido y estado

Un artifact físico pertenece a un archive y a una identidad de path estable.
Dos paths con bytes iguales siguen siendo dos entidades físicas. El contenido
es una identidad de bytes opcional y compartida; no asigna pertenencia a una
obra. Los atributos que cambian, incluidos bytes y metadata física, viven en
ArtifactState por snapshot.

Esto evita tres errores: colapsar duplicados, usar `mtime` como significado y
confundir una nueva versión física con una nueva obra. El replay debe ignorar
tiempo volátil cuando la semántica es la misma y debe conservar el primer
estado determinista o separar el dato volátil de la identidad.

### Observación, transformación y relación

`Observation` dice que un observador encontró una condición o referencia.
`TransformationEvent` sólo existe cuando inputs, outputs y witness apoyan el
evento. `Relation` puede ser una candidate relation sin afirmarla. Esta
separación permite representar correctamente casos como:

- `RAYU.blend -> rayu_export.py -> rayu_resources.glb`: evento de export
  apoyado por C05/C06;
- `ARICA.aep -> tottem_ojo.mp4`: referencia nativa y media observada, pero
  output role/export causality desconocidos;
- `MYRA_final.mp4` y frames: output observado, source binding desconocido.

La información técnica sirve, pero su alcance debe quedar limitado. Un
`ffprobe`, un basename o la coexistencia en una carpeta no prueban intención,
calidad, autoría o publicación.

## El archivo como mundo operativo

La memoria mínima es object-centric:

```text
Archive
  -> Artifact físico
      -> ArtifactState por snapshot
          -> Observation
          -> TransformationEvent
          -> Relation candidate
              -> provisional unit / Project IR
                  -> practice evidence state
```

Desde ahí la circulación de MAK es:

```text
archivo físico
  -> evidencia y replay
  -> relaciones y unidades provisionales
  -> Project IR / practice evidence
  <-> opportunity constraints
  -> posibilidades de programa
  -> research frontier y evidence return
  -> common product plan
  -> dossier / application / research
  -> episode / outcome
  -> aprendizaje operativo y próxima sonda
```

Cada paso es una proyección, no una migración total de autoridad. Project IR
es intercambio; practice state es evidencia interna; opportunity constraints
son evidencia externa; product plan es una vista derivada; el ledger es
memoria de episodios. Ninguno reemplaza al archivo físico.

## Qué significa que MAK piense

Pensar no es generar texto libre ni devolver un `unknown`. Es mantener un
conjunto acotado de hipótesis, buscar evidencia, componer capacidades, simular
resultados, comparar explicaciones rivales, falsar las débiles y producir el
mejor producto permitido por la evidencia.

Una ejecución pensante puede:

1. detectar que una carpeta contiene un anchor nativo, medios, sidecars y
   secuencias sin asumir todavía una obra;
2. generar varias relaciones locales con endpoints físicos;
3. comparar una hipótesis de componente contra una hipótesis de versión;
4. descubrir que falta un export witness y convertir esa ausencia en una sonda
   de bajo costo;
5. formar una unidad provisional o dejar refs ambiguas/unassigned;
6. cruzar esa práctica con requisitos explícitos de una oportunidad;
7. planificar investigación oficial si la fuente está observada pero no
   confirmada;
8. compilar un dossier interno con nueve huecos, en vez de inventar narrativa;
9. aprender de si una investigación, ranking o producto produjo un resultado,
   sin convertir el borrador en verdad.

El planificador necesita capacidades con precondiciones, efectos, costo,
incertidumbre y validadores. Ejemplos: `observe_explicit_root`,
`replay_snapshot`, `extract_native_metadata`, `compare_local_artifacts`,
`validate_official_source`, `compile_dossier`, `queue_research_job` y
`record_episode_projection`. El planificador debe detectar imposibilidad y
capacidad faltante; no inventar una ejecución exitosa.

## Supervisión natural y aprendizaje

Los años de trabajo terminado sí contienen supervisión, aunque no estén
etiquetados como dataset. Un export con un script y un marker aporta una señal
causal más fuerte que un basename. Un manifest conecta outputs y versiones. Una
publicación demuestra que cierta manifestación salió del archivo, aunque no
explica todos sus fuentes. Un documento nativo conserva composición, capas,
escenas o referencias. La reutilización, el co-consumo, las secuencias, las
entregas y el tiempo aportan señales probabilísticas.

Estas señales deben separarse:

- evidencia fuerte: witness validado, hash, manifest, documento nativo,
  publicación o decisión histórica con provenance;
- señal probabilística: embedding, similitud visual/textual, basename,
  proximidad temporal, directory topology o co-consumo;
- hipótesis curatorial: unidad, obra, serie, programa o selección posible;
- objetivo: cobertura, diversidad, coherencia, ajuste, costo y riesgo;
- validación automática: schema, replay, hash, split, refs resueltas, balance y
  gates.

El orden de modelado debe ser conservador: reglas y validadores primero,
representaciones congeladas después, modelos pequeños sobre embeddings antes
de cualquier fine-tuning. Transfer learning, feature extraction, metric
learning, clustering, self-supervision, adapters, LoRA y distillation son
instrumentos posibles, no la misión. Se justifican sólo si un experimento con
holdout por archive/person/project muestra una señal estable que un baseline no
explica.

La separación de train/validation/test debe ocurrir antes de extraer features.
No se debe usar el mismo artista, proyecto, manifest o futuro outcome en ambos
lados. Un episodio abierto no es un fracaso. Un resultado externo puede
calibrar ranking, atención, VOI o query selection; nunca debe promover un
claim de obra.

## Por qué aparecieron loops

El loop principal fue tratar MAK como una tarea local: leer carpetas, ordenar,
crear un reporte, preguntar al usuario, guardar un handoff y comenzar otra
carpeta. Ese loop no tenía una función de producto ni una memoria de mundo.

El segundo loop fue convertir `unknown` en salida final. Como una imagen plana
o un MP4 no revelan por sí mismos su origen, el sistema concluía que nada podía
relacionarse y devolvía la duda al artista. La corrección es aceptar que algunas
cosas son lógicamente no observables desde un producto final, pero aun así
producir: evidencia técnica, hipótesis rival, redacción calibrada, selección
interna, research plan o dossier con huecos.

El tercer loop fue arquitectónico: cada fracaso fundaba otra lane, Hub,
framework o handoff. La corrección es una arquitectura corta y reusable, con
consumidores reales y gates observables. No se arregla un runtime legacy para
probar una teoría nueva; se lo registra y se lo bordea con un contrato puro.

El cuarto loop fue la falsa confianza de los fixtures. Los contratos Stage 1–5
pueden pasar y aun así faltar datos reales para un dossier útil. El piloto
ARICA/Fondart es valioso precisamente porque produce un dossier interno,
application bloqueada y una acción de research, no una postulación falsa.

## Límites honestos

MAK puede decidir autónomamente qué evidencia existe, qué hipótesis son
compatibles, qué relaciones tienen mejor soporte, qué producto es draftable,
qué requisito está bloqueado y qué investigación tiene mayor valor esperado.

Puede mantener hipótesis de obra, serie, versión, componente y publicación
sin bloquear el resto del producto. Puede producir una variante privada que
declara sus límites. Puede decir que un recurso no está asignado sin convertir
eso en que no pertenece a la obra.

No puede conocer lógicamente desde una imagen plana la intención del autor, ni
probar causalidad de exportación por coexistencia, ni reconstruir una escena
destruida, ni declarar que una obra es representativa del artista si el archivo
observado es parcial. Tampoco puede convertir una fuente web en evidencia de
práctica sin una referencia interna explícita.

Estos límites no son preguntas obligatorias para el usuario. Son variables de
control: afectan la confianza, el texto, el ranking, la privacidad, la
selección y la siguiente sonda.

## Criterio de verdad del sistema

MAK avanza cuando reduce incertidumbre relevante y entrega un producto mejor
trazado, no cuando fuerza más afirmaciones. El éxito es una circulación
reproducible desde dos archivos distintos hasta un dossier/portfolio interno,
con research y postulación correctamente bloqueados cuando corresponde, sin
editar inputs, sin duplicar entidades físicas y sin convertir hipótesis en
verdad.
