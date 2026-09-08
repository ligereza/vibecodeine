> **SUPERADO.** Este borrador quedó reemplazado por
> `postulaciones/ANEXOS/SELECCION_PORTFOLIO_AMA.md`, que clasifica las
> candidatas por nivel de procedencia, propone epígrafes y marca las alertas
> de dato. Se conserva porque documenta el primer cruce de decisiones.

# BORRADOR · Índice de selección candidata para el portfolio

> **ESTO NO ES UN PORTFOLIO.** Es un índice de candidatas construido a
> partir de decisiones que el titular ya tomó y que el sistema registró.
> No promueve ningún registro a obra, no publica material restringido y no
> decide autoría. El PDF de portfolio se arma con la decisión del titular.

Generado el 2026-09-06 leyendo `selections.jsonl` y `PORTFOLIO_INBOX.json`.
Solo lectura: no modifica nada.

## 1. De dónde sale esta selección

No la propuse yo. Sale del **estado final de las decisiones que el titular
registró entre el 7 de agosto y el 2 de septiembre de 2026**, tomando para
cada registro su última decisión, que es la que manda.

- Registros con alguna decisión: **68**
- Estado final `seleccionar`: **4**
- Estado final `descartar`: **62** (todos con motivo `no_es_obra`)
- Estado final `deseleccionar`: **2**

El inventario del que provienen está marcado `status: not_public` y tiene
7.044 registros. Es decir: **lo decidido cubre el 1% del inventario.** Ese
es justamente el trabajo que el Expediente 1 pide financiar.

## 2. Candidatas: los registros que el titular seleccionó

| # | id del registro | tipo | fecha | última decisión | sesión |
|---:|---|---|---|---|---|
| 1 | `18007549444004070.jpg` | published_media | 2018-11-29 | seleccionar | `estudio-mslo4jtt-qtvs36` |
| 2 | `17973246073163234.jpg` | published_media | 2018-11-29 | seleccionar | `estudio-mslo4jtt-qtvs36` |
| 3 | `17874296566294009.jpg` | published_media | 2018-11-29 | seleccionar | `estudio-mslo4jtt-qtvs36` |
| 4 | `18017817841126419.jpg` | published_media | 2019-02-24 | seleccionar | `estudio-mslo6kwb-genx8d` |

**Son cuatro, y conviene decir lo que eso significa.** Las bases de Ama Amoedo
admiten hasta 20 imágenes con epígrafes. Cuatro no alcanza para un portfolio.

Esto no es un defecto del índice: es el estado real del archivo, y es el
argumento más fuerte del Expediente 1. De 7.044 registros se revisaron 68 y
sobrevivieron cuatro. El titular descartó 62 con el motivo "no es obra" y se
desdijo de dos selecciones anteriores. Es un criterio exigente aplicado a una
muestra mínima.

**Consecuencia práctica para el envío del 9 de septiembre:** el portfolio de
Ama Amoedo no puede armarse sólo con lo ya decidido. El titular tendrá que
seleccionar directamente, con su criterio y sin el instrumento, las piezas que
falten. Es trabajo suyo de unas horas, no una decisión que este paquete pueda
tomar por él. Está anotado como dependencia D-3.

## 3. Lo que este índice deliberadamente NO hace

- **No promueve registros a obras.** Los `tipo_contenido` del inventario son
  `story` y `published_media`: categorías de origen, no juicios de autoría.
- **No incorpora las 134 piezas tipificadas `obra`** del otro universo
  (`campo.json`). Esa tipificación es del pipeline, no del artista, y sus
  identificadores no se cruzan con los de aquí.
- **No publica nada.** Las 103 clasificaciones registradas están en
  `promotion: "none"` y sólo 3 en `human_confirmed`. La compuerta de
  promoción existe y está sin cruzar.
- **No decide títulos.** Los epígrafes los escribe el titular.

## 4. Decisión mínima que se necesita del titular

1. Revisar las candidatas listadas y aceptar, rechazar o ampliar.
2. Escribir el epígrafe de cada una.
3. Confirmar que ninguna incluye imágenes de terceros sin autorización.
4. Con eso, el PDF se arma. Sin eso, no debe armarse.

## 5. Advertencia sobre material con personas

El inventario contiene registros de eventos que pueden mostrar personas
identificables. Ninguna salida pública de este paquete los incluye, y la
revisión pieza por pieza antes de publicar es una decisión del titular, no
automatizable. Esto corrige la afirmación genérica "sin datos humanos" que
aparecía en documentos anteriores al 6 de septiembre.
