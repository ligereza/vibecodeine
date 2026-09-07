# Selección candidata de portfolio — Ama Amoedo

Generada por `verificador/generar_seleccion_portfolio.py` el 2026-09-06.
Sólo lectura: no modifica ningún dato de MAK.

> **Qué decide este documento y qué no.** Decide la selección y propone los
> epígrafes, con un criterio explícito y reproducible. **No decide autoría:**
> promover un registro a obra es un acto del artista, y por eso cada candidata
> lleva su nivel de procedencia a la vista. Lo único que queda pendiente es la
> aprobación y la entrega física de los archivos.

## 1. Por qué hay niveles de procedencia y no una lista plana

El archivo tiene tres cuerpos de material que no se cruzan, y sólo uno de ellos
reúne las tres condiciones que un portfolio necesita: que el artista lo haya
reconocido como obra, que exista una lectura de lo que se ve, y que el archivo
esté en disco.

| Nivel | Qué reúne | Piezas |
|---|---|---:|
| **N1** | decisión humana registrada **y** archivo en disco | **4** |
| **N2** | archivo en disco **y** lectura de máquina **y** tipificado `obra`, sin decisión | **134** |
| **N3** | título y texto propios del artista, **sin archivo** y sin decisión | **8** |

**La intersección N1 ∩ N2 es cero.** Se comprobó cruzando el identificador de
medio de las 68 piezas decididas contra las 219 del campo visual: ninguna
coincide. Son dos inventarios disjuntos.

Y las de N3 —las que sí llevan título y texto del artista— **no tienen archivo**:
sus rutas `assets/works/*.svg` no existen en disco. No pueden ir a un portfolio.

> Este hallazgo no es un obstáculo del expediente: **es su argumento**. Hoy no
> hay en el archivo ninguna pieza que sea simultáneamente decidida por el autor,
> legible y presente. Cerrar esa distancia es exactamente lo que la beca financia.

## 2. N1 — las que el titular ya decidió, con archivo verificado en disco

Estado final de las decisiones registradas entre el 2026-08-07 y el 2026-09-02.
Tomando para cada registro su última decisión, que es la que manda.

| # | id del registro | fecha de la obra | archivo | tamaño | decidida el | sesión |
|---:|---|---|---|---:|---|---|
| 1 | `18007549444004070.jpg` | 2018-11-29 | `/portfolio-media/posts/201811/18007549444004070.jpg` | 113.8 KB | 2026-08-09 | `estudio-mslo4jtt-qtvs36` |
| 2 | `17973246073163234.jpg` | 2018-11-29 | `/portfolio-media/posts/201811/17973246073163234.jpg` | 136.6 KB | 2026-08-09 | `estudio-mslo4jtt-qtvs36` |
| 3 | `17874296566294009.jpg` | 2018-11-29 | `/portfolio-media/posts/201811/17874296566294009.jpg` | 45.4 KB | 2026-08-09 | `estudio-mslo4jtt-qtvs36` |
| 4 | `18017817841126419.jpg` | 2019-02-24 | `/portfolio-media/other/18017817841126419.jpg` | 158.2 KB | 2026-08-09 | `estudio-mslo6kwb-genx8d` |

**Estas cuatro entran al portfolio sin discusión:** son las únicas que llevan
un acto de autoría registrado. No tienen título ni epígrafe propio —el campo de
descripción original está vacío en tres y contiene `xx` en la cuarta—, de modo
que **el epígrafe lo escribe el titular**. Es el único texto que no puedo redactar.

## 3. N2 — propuesta razonada para completar el conjunto

**Criterio, explícito y reproducible:** máxima cobertura de estilo y de paleta
con el menor número de piezas, priorizando las de paleta más rica; desempate
determinista por identificador. Es un criterio de **diversidad**, no de calidad:
un instrumento no puede juzgar calidad y éste no lo pretende.

Se seleccionan 12 de 134 candidatas, cubriendo 11 estilos y 15 colores distintos.

| # | id | estilo | colores | epígrafe propuesto | alerta de dato |
|---:|---|---|---|---|---|
| 5 | `00dfbf29763b-17963390141` | Surrealismo, Psicodelia | naranja, verde, azul | Ilustración digital de una mujer en una bañera con elementos surrealistas y psicodélicos | — |
| 6 | `0142feb0bda0-17857906844` | Dibujo animado | morado, rosa, verde | Imagen del personaje Bubbles de las series animadas 'The Powerpuff Girls', con una expresión seria y un cigarrillo en la boca | — |
| 7 | `0309513c750b-17988112985` | Arte digital, poligonales | rojo, azul, verde | Pieza artística con una representación abstracta de una mariposa tridimensional | — |
| 8 | `04d565d4c17f-18020008679` | Surrealismo, Ilustración digital | morado, azul, verde | Ilustración surrealista y onírica con elementos naturales estilizados y efectos de luz | — |
| 9 | `070d74bb7ee3-17845442352` | Ilustración digital | rojo, morado, verde | Mujer con cabello rizado y adornos en el cuerpo está en una selva exuberante, frente a un topo que esconde una pequeña casa. Hay flores y otro topo ce | — |
| 10 | `08d8944c7581-17896000479` | Surrealismo, Pop Art | rojo, azul, morado | Imagen surrealista que combina elementos faciales y naturaleza | — |
| 11 | `0986fd0e1556-17890634727` | Ilustración digital surrealista | azul, turquesa, violeta | Conejo blanco en un paisaje acuático con hongos bioluminiscentes | — |
| 12 | `0b6e572c5a89-17869666019` | Realista, línea negra | blanco, negro, beige | Tatuaje en la pierna de un conejo con kimono y paraguas | la lectura de máquina describe algo que puede no ser obra, pese a estar tipificada `obra` |
| 13 | `0bffc5fc7955-17843571640` | Cartoon, ilustración abstracta | orange, blue, green | Ilustración abstracta y estilizada de una criatura con rasgos caricaturescos y colores vibrantes | vocabulario de color sin normalizar: orange, blue, green |
| 14 | `0fa807254c70-17850145885` | Abstracto, Surrealista | rojo, beige, negro | Imagen con una figura humana estilizada, posiblemente un retrato, con elementos abstractos y geométricos en rojo sobre un fondo beige | — |
| 15 | `19116286e171-17973643747` | Surrealismo, ilustración digital | morado, azul, amarillo | Escena surrealista con una rata y un gato sentados a una mesa, rodeados de objetos extraños y colores vibrantes | — |
| 16 | `196b3c04dc11-17995133948` | Surrealista, con uso de color iridiscente y distorsión visual para crear una sensación de extrañeza. | amarillo, naranja, rojo | Imagen con efecto de visión a través de un microscopio o lente circular, mostrando un campo agrícola y una casa en el horizonte | — |

Archivos: `~/iskvw/piel/animadas/<id>.svg`, los 12 verificados en disco.

**2 de las 12 candidatas llevan una alerta de dato.** No se ocultan y no
descalifican la pieza: describen exactamente el trabajo que el Expediente 1 pide
financiar. Dos defectos aparecen en la muestra y los dos son reales:

- **Tipificación que no es validación autoral.** Al menos una candidata está
  marcada `obra` por el pipeline mientras su lectura de máquina describe un
  tatuaje. Ningún instrumento puede resolver eso: lo resuelve el artista.
- **Vocabulario de color sin normalizar.** Alguna candidata trae los colores en
  inglés y el archivo mezcla `azul` con `Azul`. Decidir con qué palabras se
  describe el propio trabajo es una decisión de autor, no de mantenimiento.

> **Los epígrafes de N2 son propuestas derivadas de la lectura de máquina,
> no texto del artista.** Se entregan redactados para que el titular los acepte,
> corrija o reemplace. Ninguno afirma autoría, técnica ni año: esos datos no
> están en la fuente y no se inventan.

## 4. N3 — por qué quedan fuera, aunque sean las que tienen mejor texto

| id | título del artista | archivo declarado | ¿existe en disco? |
|---|---|---|---|
| `vola` | VOLÁ · lo visible y lo invisible | `assets/works/vola-vaso.svg` | **no** |
| `campo-motor-diagnostico` | Campo · Motor de Diagnóstico | `assets/works/campo-motor-diagnostico.svg` | **no** |
| `cenefa-dossier` | Cenefa · Dossier | `assets/works/cenefa-dossier.svg` | **no** |
| `wip-malla-reactiva` | Malla Reactiva | `assets/works/malla-reactiva-cover.svg` | **no** |
| `sala-flujo-3d` | sala flujo — portafolio 3D | `assets/works/sala-3d-cover.png` | **no** |
| `tapiz-system-projection` | TAPIZ :: system projection | `assets/works/tapiz-cover.png` | **no** |
| `cauce-sala3d` | Cauce · Sala 3D | `assets/works/cauce-sala3d.svg` | **no** |
| `medallon-entrada` | Medallón · Entrada | `assets/works/medallon-entrada.svg` | **no** |

Las ocho tienen título, año, técnica y descripción larga escritos por el
artista, y son con diferencia el mejor material textual del archivo. **Pero
ninguna tiene archivo en disco y ninguna pasó por instancia de decisión alguna:**
0 en el inventario de curaduría, 0 selecciones, 0 clasificaciones, 0 en el
registro de decisiones y 0 en `curaduria.json`. Su `estado: publicada` es un
valor por defecto que llevan las 1.826 piezas de esa clase, no una decisión.

Además `obras.json` es del 2026-07-27, anterior al inventario de curaduría
(2026-08-07) y al campo visual (2026-09-02): describe un estado del proyecto
que las dos instancias posteriores no recogieron.

**Acción recomendada, no bloqueante para el 9 de septiembre:** si el titular
localiza esos ocho archivos, pasan a ser el mejor material del portfolio, porque
aportan lo único que a N1 y N2 les falta: título y texto de autor. Mientras no
aparezcan, no se incluyen. Registrado como pendiente personal, no como pregunta.

## 5. Conjunto propuesto

- **4 piezas de N1** — decisión de autoría registrada, archivo verificado.
- **12 piezas de N2** — propuesta razonada, epígrafes a validar.
- **Total: 16 piezas**, dentro del máximo de 20 que admiten las bases.

## 6. Lo único pendiente del titular

1. Aprobar o corregir el conjunto de 16.
2. Escribir los cuatro epígrafes de N1 y validar los doce de N2.
3. Entregar los archivos físicos, o autorizar el uso de los que están en disco.
4. Confirmar que ninguna pieza incluye imágenes de terceros sin autorización.

No se le pregunta qué obras elegir: la selección está hecha y fundamentada.
Se le pide aprobarla, que es un acto de autoría y no una decisión de diseño.
