# Dimensiones del Orden

Este repo funciona como una zapatilla/alargador organizador para proyectos
creativos, automatizaciones e IAs. No reemplaza el trabajo manual del
disenador: ordena entradas, salidas, contexto y pasos.

```txt
proyectos + herramientas + IAs + checkpoints
        conectados a un mismo punto de orden
```

Hasta el 2026-09-02 este archivo tenia once lineas y el marco conceptual del
proyecto vivia unicamente dentro de un log de sesion
(`.codex/sessions/2026/08/24/rollout-2026-08-24T10-02-10-*.jsonl`), sin que
ningun test, documento ni herramienta lo referenciara. El repo tiene una regla
para eso: lo que se responde en una sesion se escribe en esa sesion o se
pierde. El texto que sigue se recupero de ese log y se conserva aqui, en
espanol, porque alimenta directamente material que leen personas (postulaciones
y lectura curatorial).

---

## Marco: el orden como composicion

### El título como operación

El título tampoco es una clave primaria. Es un acto que interviene sobre la percepción. Si $x$ representa la experiencia sensible y $t$ el título, el significado no es simplemente $M(x)$, sino:


$$
M = f(x,t,c,a,r)
$$


donde $c$ es el contexto, $a$ el artista y $r$ el recorrido previo del receptor.

El orden importa:


$$
f(x \rightarrow t) \
eq f(t \rightarrow x)
$$


Escuchar primero una canción y conocer después su título produce una reinterpretación retrospectiva. Leer el título antes condiciona la escucha futura. El título puede incluso operar sobre otra obra: anticiparla, completar una secuencia o modificar retrospectivamente una pieza anterior. Por tanto, título y obra no mantienen necesariamente una correspondencia uno-a-uno.

El nombre del artista ocupa un nivel superior. Funciona como el marco que vuelve comparables objetos que, aislados, podrían parecer inconexos. En ese sentido, el artista es el título global del corpus: no describe cada objeto ni demuestra autoría sobre todo lo almacenado, pero establece el horizonte desde el cual sus relaciones resultan pertinentes. Los títulos particulares ordenan localmente; la identidad artística condiciona globalmente.

### Por qué el orden perfecto es imposible

Reconstruir una ontología artística desde archivos es un problema inverso. Observamos efectos materiales $E$ —archivos, exports, fechas, similitudes, publicaciones— e intentamos recuperar una estructura cultural latente $W$:


$$
E = g(W)
$$


Pero $g$ no es invertible. Varias historias distintas pueden producir exactamente la misma evidencia:


$$
g(W_1)=g(W_2)=E
$$


Un archivo llamado `finalfinal.mp4` no contiene la decisión que lo convirtió en obra, versión o descarte. Si esa decisión nunca quedó registrada, ningún modelo puede recuperarla con certeza: no es falta de inteligencia, sino falta de identificabilidad. Exigir una reconstrucción perfecta obliga al sistema a inventar información o a detenerse indefinidamente.

La salida rigurosa consiste en cambiar la pregunta. No buscar:


$$
\text{“¿Cuál era el único orden verdadero?”}
$$


sino:


$$
\text{“¿Qué órdenes defendibles pueden construirse con la evidencia disponible?”}
$$


### Ordenar como composición

Los archivos sí contienen cualidades observables: color, duración, ritmo, escala, textura, movimiento, repetición, temporalidad, formato, proximidad y transformaciones. Estas cualidades no prueban identidad artística, pero permiten construir relaciones compositivas reales.

Sea $\phi(x)$ la representación observable de un elemento y $G$ el propósito de una presentación. El orden se convierte en una función:


$$
O_G = F(\{\phi(x)\},E,G)
$$


El mismo corpus puede producir órdenes distintos porque cambia $G$: evolución temporal, constelación conceptual, red de colaboraciones, recorrido sensorial, proceso de transformación o propuesta comercial. Ninguna de estas vistas necesita modificar los archivos ni declarar que una agrupación es la identidad definitiva de una obra.

La selección puede formularse como optimización multiobjetivo:


$$
O_G^*=\arg\max_O
\left(
\alpha C+
\beta D+
\gamma R_G+
\delta V+
\eta T-
\lambda N-
\mu U
\right)
$$


donde $C$ es coherencia, $D$ diversidad, $R_G$ adecuación al propósito, $V$ potencia perceptiva, $T$ trazabilidad, $N$ redundancia y $U$ afirmaciones sin respaldo.

No existe necesariamente un único máximo. Existe una frontera de soluciones válidas. Esa multiplicidad no es un defecto: es la condición que permite que un mismo archivo produzca diferentes experiencias sin falsificar su historia.

### Consecuencia

Un portafolio no debe entenderse como el inventario definitivo de obras perfectamente identificadas. Es una proposición: toma materiales existentes y sostiene una lectura mediante selección, secuencia, contraste, repetición y contexto. Su verdad no consiste en haber recuperado una clasificación perdida, sino en conservar la evidencia, no inventar hechos y producir una experiencia coherente.

El aprendizaje tampoco debe comenzar intentando predecir la categoría correcta de cada archivo. Debe observar transformaciones completas:


$$
(\text{corpus},\text{propósito})
\rightarrow
(\text{selección},\text{relaciones},\text{orden},\text{presentación})
\rightarrow
\text{resultado}
$$


Así aprende qué decisiones de composición funcionan bajo determinadas condiciones. No aprende que `x.mp4` “es” una obra; aprende cuándo conviene mostrarlo, junto a qué otros elementos, bajo qué marco y con qué grado de afirmación.

La tesis central es, entonces, que el problema no consiste en descubrir unidades perfectas dentro del caos. Consiste en preservar lo que existe y construir, sobre ello, órdenes reversibles que hagan aparecer sentidos que ningún archivo posee por separado. El error no estaba en la incapacidad del sistema para adivinar: estaba en exigirle resolver como clasificación un problema que, por naturaleza, es de composición.

---

## Donde vive cada termino, en codigo

La formulacion anterior no es una metafora: cada termino tiene un archivo.

| Termino | Que es | Donde esta hoy |
|---|---|---|
| $E$ | La evidencia material observada | `experiments/pilots/ARICA-FONDART-2027/` (12.332 artefactos, 128 observaciones, 512 candidatos de relacion, 174 unidades) |
| $\phi(x)$ | La representacion observable de un elemento | `cultura/mak_plataforma/copilot.py`, esquemas `faro-portfolio-atlas-v1` y `faro-ordering-field-v2`. Hoy artesanal, sin embeddings |
| $G$ | El proposito de una presentacion | `data/portfolio_formats/*.json`, esquema `mak-portfolio-format-v1`. Cada formato declara claims permitidos, slots, estado minimo de evidencia y evidencia admisible |
| $F$ | La funcion que compone el orden | `flujo/src/flujo/knowledge/portfolio_dossier.py`, `contracurator.py`, `opportunity_fit.py` |
| $O_G$ | Un orden defendible, relativo a un proposito | Todavia no existe como salida: el sistema emite un veredicto unico en vez de N ordenes |

`G` ya esta implementado y nadie lo nombro asi. Un formato es un proposito:
`F4-fondart-nacional-investigacion-2027.json` declara `declared_claims`
(`ocurrio`, `puedo`, `hice_esta_parte`), `forbidden_claims` (`es_mio`,
`significa`) y cinco `forbidden_inferences`. Eso es exactamente la restriccion
que la teoria pide: no afirmar identidad ni significado desde evidencia de
archivo.

## El defecto que esto explica

El piloto termina en `fit: abstain`, `dossier: draft_only`, `application:
blocked`. No es un bug: es un sistema que se niega cuando la evidencia no
alcanza, y esa negativa es correcta para la pregunta que se le hace.

El problema es la pregunta. `opportunity_fit` calcula si el archivo se ajusta a
una linea de concurso, y el propio `F4` dice, transcrito de las bases: *el
ajuste de una practica audiovisual a esta linea es una decision del postulante,
no un resultado de este documento*. El sistema esta emitiendo veredicto sobre
algo que su formato pone fuera de alcance, y por eso se bloquea sin importar
cuanta evidencia se le agregue.

La correccion no es agregar evidencia ni relajar el gate. Es que `G` entre como
parametro del campo de orden y la salida sea un conjunto de ordenes
defendibles, cada uno con su formato, sus claims permitidos y su estado de
evidencia. Un mismo corpus produce entonces evolucion temporal, constelacion
conceptual, red de colaboraciones, recorrido sensorial, proceso de
transformacion o propuesta comercial, sin que ninguno declare cual es la
identidad definitiva de una obra.

## Retiro

Este documento se retira cuando `faro-ordering-field-v3` acepte `G` como
entrada y el piloto emita ordenes en lugar de un veredicto.
