# Ficha de corpus y selección propuesta de portafolio

Generada el 2026-09-06 leyendo `~/iskvw/datos/campo.json` y `archivo.json`.
No modifica nada. Es una **propuesta de selección basada en evidencia**, no
una decisión: la decisión curatorial la toma el artista.

## 1. El corpus

- Atlas completo: **2034 piezas**, **5812 vínculos**.
- Campo visual de trabajo: **219 piezas**, de las que **134 están tipificadas como obra**.
- Contexto (registro de evento, flyer, logo, pantalla): **47 piezas**.
- Percepción de máquina disponible: **219 de 219**.

### Estilos presentes en las obras (normalizando mayúsculas)

| Estilo | Obras |
|---|---:|
| surrealismo, ilustración digital | 14 |
| abstracto | 11 |
| surrealismo, psicodelia | 8 |
| surrealismo, pop art | 5 |
| abstracto, surrealista | 5 |
| dibujo animado | 3 |
| ilustración digital | 3 |
| surrealismo | 3 |
| animación | 3 |
| arte abstracto | 3 |
| surrealismo, arte digital | 3 |
| surrealista | 2 |

Total de estilos distintos tras normalizar: **77**.

### Colores dominantes en las obras

| Color | Apariciones |
|---|---:|
| rojo | 67 |
| azul | 55 |
| amarillo | 34 |
| verde | 32 |
| morado | 32 |
| negro | 32 |
| blanco | 22 |
| naranja | 19 |
| rosa | 13 |
| gris | 11 |
| magenta | 10 |
| beige | 7 |

> **Higiene de datos, declarada y no ocultada.** Sin normalizar, `azul` y
> `Azul` cuentan como categorías distintas, y los estilos aparecen con y sin
> mayúscula inicial. Esta ficha normaliza para leer; el archivo todavía no.
> Corregirlo es una actividad presupuestada en el Expediente 1.

## 2. Selección propuesta para portafolio (12 obras)

**Criterio explícito y reproducible:** máxima cobertura de estilo y de
paleta con el menor número de piezas, priorizando las de paleta más rica.
Es un criterio de *diversidad*, no de *calidad* — un instrumento no puede
juzgar calidad y este no lo pretende. Sirve como punto de partida para que
el artista acepte, rechace o reemplace cada entrada.

| # | id | tipo | estilo | colores | qué se ve (lectura de máquina) |
|---:|---|---|---|---|---|
| 1 | `00dfbf29763b-179633901` | obra | Surrealismo, Psicodelia | naranja, verde, azul | Una ilustración digital de una mujer en una bañera con elementos surrealistas y psicodélicos. |
| 2 | `0142feb0bda0-178579068` | obra | Dibujo animado | morado, rosa, verde | Una imagen del personaje Bubbles de las series animadas 'The Powerpuff Girls', con una expresión seria y un ci… |
| 3 | `0309513c750b-179881129` | obra | Arte digital, poligonales | rojo, azul, verde | Una pieza artística con una representación abstracta de una mariposa tridimensional. |
| 4 | `04d565d4c17f-180200086` | obra | Surrealismo, Ilustración digital | morado, azul, verde | Una ilustración surrealista y onírica con elementos naturales estilizados y efectos de luz. |
| 5 | `070d74bb7ee3-178454423` | obra | Ilustración digital | rojo, morado, verde | Una mujer con cabello rizado y adornos en el cuerpo está en una selva exuberante, frente a un topo que esconde… |
| 6 | `08d8944c7581-178960004` | obra | Surrealismo, Pop Art | rojo, azul, morado | Una imagen surrealista que combina elementos faciales y naturaleza. |
| 7 | `0986fd0e1556-178906347` | obra | Ilustración digital surrealista | azul, turquesa, violeta | Conejo blanco en un paisaje acuático con hongos bioluminiscentes. |
| 8 | `0b6e572c5a89-178696660` | obra | Realista, línea negra | blanco, negro, beige | Tatuaje en la pierna de un conejo con kimono y paraguas. |
| 9 | `0bffc5fc7955-178435716` | obra | Cartoon, ilustración abstracta | orange, blue, green | Ilustración abstracta y estilizada de una criatura con rasgos caricaturescos y colores vibrantes. |
| 10 | `0fa807254c70-178501458` | obra | Abstracto, Surrealista | rojo, beige, negro | Una imagen con una figura humana estilizada, posiblemente un retrato, con elementos abstractos y geométricos e… |
| 11 | `19116286e171-179736437` | obra | Surrealismo, ilustración digital | morado, azul, amarillo | Una escena surrealista con una rata y un gato sentados a una mesa, rodeados de objetos extraños y colores vibr… |
| 12 | `196b3c04dc11-179951339` | obra | Surrealista, con uso de color iridiscente y distorsión visual para crear una sensación de extrañeza. | amarillo, naranja, rojo | Imagen con efecto de visión a través de un microscopio o lente circular, mostrando un campo agrícola y una cas… |

Cobertura de la selección: **11 estilos** y **15 colores** distintos.

## 3. Estado de derechos

- Todas las piezas son **obra propia del artista**. No hay obra de terceros
  en el corpus de trabajo, por lo que **no corresponde** el anexo de
  autorización de derechos de autor en ninguna de las tres postulaciones.
- Las piezas tipificadas como `foto_evento` (40) **pueden contener imágenes**
  **de personas**. Antes de publicar cualquiera de ellas hay que revisarlas una
  por una. Corrige la afirmación genérica "sin datos humanos" que aparecía en
  documentos previos: un archivo artístico sí puede contener personas.
  **Recomendación: excluir la categoría `foto_evento` completa de toda salida**
  **pública hasta que exista revisión pieza a pieza.** La selección de arriba
  ya está restringida a `tipo = obra` por esa razón.

## 4. Qué queda pendiente y sólo puede hacerlo el artista

1. Aceptar, rechazar o reemplazar cada una de las 12 entradas propuestas.
2. Poner título propio, con sus tildes, a cada obra seleccionada.
3. Fechar las piezas que no tengan fecha.
4. Revisar las 40 `foto_evento` si alguna vez van a publicarse.
