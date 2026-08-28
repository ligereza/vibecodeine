# Teoria del archivo artistico como sistema dinamico

## Tesis

Un archivo artistico grande no es un catalogo de obras ya conocidas. Es un
sistema dinamico, multimodal y parcialmente observable: contiene estados
fisicos, huellas de trabajo, duplicados, fuentes nativas, derivados, sidecars,
secuencias, recursos, exportaciones, publicaciones y vacios. Cada observacion
es una actualizacion del estado de conocimiento, no una sentencia sobre lo que
el artista quiso hacer.

La unidad de verdad operacional es el vinculo entre una afirmacion y su
evidencia. La unidad de almacenamiento es el artifact fisico. La unidad de
reconstruccion es provisional. La unidad de producto es un borrador gobernado
por evidencia. La unidad de aprendizaje es un episodio con outcome externo
verificado. Confundir estas unidades es la fuente principal de falsos
positivos.

## 1. Estados y transiciones

El archivo puede modelarse como una sucesion de snapshots:

```text
filesystem root
  -> physical observation batch
  -> append-only memory snapshot
  -> candidate relations
  -> provisional units
  -> Project IR
  -> practice evidence / opportunity fit
  -> product drafts
  -> externally verified outcome
```

La flecha no es una promocion automatica. Cada transicion agrega una
representacion y conserva el estado anterior. Una observacion de `file` puede
producir un hash; un hash puede producir una igualdad de bytes; ninguna de las
dos cosas produce por si sola una obra, un proyecto, una serie, un autor o una
publicacion.

La memoria es temporal en dos sentidos:

1. El mismo `artifact_id` puede tener estados diferentes en snapshots sucesivos
   porque el mismo path cambio bytes, tamano, mtime o disponibilidad.
2. Un artifact puede faltar en un snapshot sin que desaparezca de la memoria;
   `missing` es una diferencia incremental, no una orden de borrado.

La temporalidad fisica y la temporalidad semantica deben permanecer separadas.
`mtime_ns` describe el estado observado del filesystem y puede cambiar al
copiar un archivo. No participa en `snapshot_id` semantico. El orden temporal
de una exportacion solo se sostiene cuando existe un witness explicito que
conecta fuente, accion, marcador, output y hashes.

## 2. Identidad fisica versus identidad de contenido

La distincion central es:

```text
archive_id + relative_path -> artifact_id / physical_id / artifact_ref
bytes -> sha256 -> content_id (nullable)
```

Dos paths con los mismos bytes son dos artifacts fisicos y un solo contenido
observado. Por ejemplo, `renders/a.png` y `backup/a.png` conservan dos
`artifact_ref` aunque compartan `content:sha256:<h>`. Si el primer path cambia
bytes, sigue siendo el mismo artifact fisico con un nuevo estado de snapshot.
Si se mueve, aparece otro artifact fisico; el posible `version_of` es una
hipotesis que necesita evidencia adicional.

Los directorios, symlinks, especiales, entradas inaccesibles y errores de
lectura no son "archivos vacios". Pueden carecer de `sha256` y `content_id`,
pero deben conservar `kind`, `availability`, target estable, `error_code` o
`error_operation` cuando corresponda. La ausencia de hash es una propiedad de
observabilidad, no evidencia de igualdad.

Esta separacion permite que el sistema aprenda tres cosas distintas:

- existencia y estado de una localizacion fisica;
- igualdad o diferencia de bytes observados;
- una relacion cultural o productiva apoyada por evidencia independiente.

La tercera nunca debe ser rellenada automaticamente por las dos primeras.

## 3. Rutas, nombres y estructura

La ruta relativa es coordenada fisica, no significado. Nombres como `final`,
`v2`, `export`, `obra`, `proyecto`, `serie` o `selected` son tokens de evidencia
de baja autoridad. Pueden alimentar una observacion candidata, pero nunca
deben generar un `documented_fact`.

La estructura de carpetas sigue siendo util como contexto: ayuda a agrupar
sidecars, secuencias, manifests, frames y recursos cercanos. La estructura
tambien puede indicar una hipotesis de unidad. Pero el resultado debe conservar
alternatives, evidence_against, missing_evidence y next_probe.

Una secuencia numerada no es necesariamente una serie artistica: puede ser
una captura, un cache, un render o una transferencia. Un sidecar no es
necesariamente una declaracion autoral: puede ser metadata de software. Un
manifest ayuda a explicar una transformacion o un conjunto, pero su presencia
no prueba que todos los miembros sean una obra comun.

## 4. Relaciones y unidades

El grafo debe aceptar nodos heterogeneos: fuente nativa, componente, version,
render, frame, export, documento, manifest, recurso, publicacion y error. Una
unidad provisional es una organizacion revisable de esos nodos, no un objeto
ontologico definitivo.

Las relaciones tienen direccion e inversa. `component_of` se opone a
`has_component`; `version_of` a `has_version`; `manifestation_of` a
`has_manifestation`; `depends_on` a `depended_on_by`. Reanclar un edge sin
invertir el predicado crea una afirmacion semantica contraria. Las relaciones
simetricas, como `same_series_candidate`, siguen siendo candidates y no deben
colapsar endpoints.

Los recursos compartidos y dependencias no se vuelven proyectos por cercania.
Un ancestro comun puede explicar una relacion entre dos unidades y, al mismo
tiempo, permanecer fuera de la pertenencia de ambas. La particion
`assigned`, `ambiguous` y `unassigned` es una medicion de lo que el sistema
puede sostener, no un juicio de valor sobre el archivo.

## 5. Procedencia y evidencia

Toda capa debe llevar el origen de lo que copia. Hay varias autoridades:

- el observer prueba que una entrada y ciertos bytes/atributos fueron
  observados en un root explicito;
- archive memory prueba que ese batch fue materializado y puede reproducirse;
- un native witness puede apoyar un evento tecnico acotado;
- Research prueba captura, hashes, licencia y claims extraidos bajo sus reglas;
- una convocatoria local aporta requisitos externos, pero no prueba el lado
  interno del artista;
- un outcome externo validado puede alimentar shadow learning.

La procedencia no es decoracion. Es el mecanismo que impide que un documento
de oportunidad, una URL o un nombre de archivo se conviertan en evidencia de
autoria. La evidencia tambien tiene direccion: `evidence_for` y
`evidence_against` deben convivir. Un candidato sin counterevidence visible es
una hipotesis pobre, aunque su score sea alto.

## 6. Incertidumbre productiva

`candidate`, `pending_relation`, `unresolved_candidate`, `unknown`,
`review_required`, `ambiguous`, `unassigned`, `abstain` y `blocked` no son
errores del sistema. Son salidas necesarias cuando una observacion no alcanza
el umbral de la afirmacion solicitada.

La abstencion mantiene circulación: puede crear una pregunta Research,
conservar un gap en el dossier, seleccionar una accion bounded de autonomia o
pedir un witness. La abstencion no autoriza a inventar un proyecto vacio, un
claim soportado, un public asset o un negativo de aprendizaje.

Por eso un dossier puede ser `draft_only` con secuencia curatorial provisional
y cero assets publicos. Una aplicacion puede estar bloqueada mientras el
dossier interno es util. Un resultado de Research sin claims extraidos debe
ser exactamente `unresolved`, nunca `supported`.

## 7. El sistema aprende sin borrar el archivo

El aprendizaje no empieza con embeddings ni con una etiqueta global de obra.
Empieza con invariantes medibles:

- replay determinista bajo otra raiz absoluta;
- cero mutacion de bytes y mtimes de la fuente;
- cobertura de entradas y errores representados;
- preservacion de duplicados fisicos;
- balance exacto de assigned/ambiguous/unassigned;
- retencion de provenance y evidence gaps;
- abstencion cuando falta source validity o binding;
- split de episodios por `identity_group`, con holdout independiente.

Solo outcomes externos verificados pueden alimentar ranking, attention,
`voi_calibration` o `query_selection`. No se aprenden truth, authorship,
identity, claim_status ni artistic_worth. `training_permitted=false` es una
propiedad de la etapa, no una sugerencia.

## 8. Casos locales y arquitectura portable

ARICA, MYRA, RAYU e ISKVW son pruebas de portabilidad y superficies de
evidencia, no nombres del modelo general.

- **ARICA** demuestra el cruce completo con un archivo real y una oportunidad
  local: muchos artifacts, observaciones y gaps, pero resultado research-first
  y source validity no confirmada.
- **RAYU** es un subcaso ARICA donde C05 permite apoyar un export concreto
  `RAYU.blend -> rayu_resources.glb`. El witness no eleva entrega final,
  autoria ni intencion.
- **MYRA** estresa el limite de volumen y muestra que cientos de candidates y
  un conjunto de unassigned pueden ser una salida sana, no una falla de
  pertenencia.
- **ISKVW** muestra que un archive JSON y una media tree son superficies
  distintas. Un numeric ID o un contact sheet ayudan a reconciliar, pero las
  colisiones se reportan y los no-ID quedan pendientes.

La arquitectura portable vive en contratos y funciones puras: observation,
memory, reconstruction, Project IR, practice evidence, opportunity,
research, products y shadow learning. Los consumidores locales pueden
adaptarse o abstenerse. Ningun caso debe introducir otra registry, router,
database o significado de autor.

## 9. Prediccion operacional

Si una futura integracion mejora, no deberia producir mas certezas por defecto.
Deberia producir:

1. mas evidencia explicitamente enlazada;
2. menos gaps justificados;
3. mejores probes para candidates ambiguos;
4. replay y hashes estables;
5. igual o menor tasa de false-green;
6. mas productos internos utiles sin elevar publication, submission o truth.

El criterio de exito es aumento de trazabilidad y capacidad de abstencion,
no la cantidad de proyectos, series o obras que el sistema declara.
