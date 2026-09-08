# Ficha técnica — IRIS / Dimensiones del Orden

Medición: **2026-09-06**. Toda cifra es reproducible con
`evidencia/prueba_circuito.sh`.

## Identificación

| | |
|---|---|
| Nombre operativo | IRIS — Atlas Campo del Orden |
| Superficie | `http://127.0.0.1:8900/portafolio/` (**sólo local**, no expuesto a internet) |
| Servidor | `~/cultura/mak_plataforma/hub.py` — ThreadingHTTPServer en Python 3 |
| Raíz de contenidos | `~/iskvw/` |
| Interfaz | `editor.html` (256.541 bytes) + `mesa_montaje.js` (122.282 bytes), sin dependencias de red |
| Estado | En funcionamiento y en uso por su autor |

## Corpus verificado

| Archivo | Contenido | Cifra |
|---|---|---|
| `datos/archivo.json` | Atlas completo, generado `2026-08-29T10:38:17` | 2.034 piezas, 5.812 vínculos |
| | por clase | obra 1.826 · código 208 |
| | por medio | texto 1.807 · imagen 227 |
| | vínculos por clase | semántico 5.794 · etiqueta 18 |
| `datos/campo.json` | Campo visual de trabajo | 219 piezas, 478 filtradas |
| | con percepción de máquina | **219 de 219** |
| | tipificación | obra 134 · foto_evento 40 · tatuaje 28 · otro 6 · logo 4 · flyer_evento 2 · pantalla 1 · dibujo 1 · meme 1 · dibujo digital 1 · ficha_sustancia 1 |
| | calidad de la proyección | `vecindad_conservada = 0.4855` |
| `datos/micelio.json` | Grafo con umbral declarado | 1.431.380 bytes |
| `datos/obras.json` | Selección editorial | 8 obras |
| `datos/curaduria.json` | Decisiones humanas | **0** |
| `datos/tablero.json` | Mejoras activables por el artista | 3 activas |

## Modelo de datos

**Pieza:** `id`, `titulo`, `clase`, `fecha`, `resumen`, `etiquetas`, `peso`,
`medio` (`tipo` + `src`), `estado`, `extra`.

**Pieza del campo:** `id`, `x`, `y`, `colores`, `estilo`, `tipo`, `percibido`
(descripción de máquina), `archivo`, `tilde` (`marcas`, `por_cien`, `cuales`).

**Vínculo:** `de`, `a`, `peso`, `clase`.

**Curaduría (la mano del artista):** `titulo`, `mostrar`, `abstraccion` (0–1),
`svg`, `regimen`, `peso`, `serie`, `nota`. Todos opcionales. El propio archivo lo
documenta: *"un campo que no escribís no cambia nada"*.

## Propiedades de diseño verificadas

1. **Sólo lectura del lado del servidor.** `hub.py` resuelve `/portafolio/` sólo
   para GET. Un POST devuelve **404** (comprobado). El editor mantiene toda
   edición en memoria del navegador.
2. **La única salida es una descarga.** `editor.html` l.1092: *"its only output is
   a download"*. Un `Blob` `application/json` entregado con `a.download`.
3. **No publica automáticamente.** El artista descarga y confirma fuera de la
   aplicación (l.1094).
4. **Advierte antes de perder trabajo.** El editor firma el estado descargado y
   pregunta si hay ediciones sin descargar antes de reemplazarlas (l.2589).
5. **Declara la distorsión de su propio orden.** `vecindad_conservada` está en el
   archivo de datos, no en un informe aparte.
6. **Declara el filtro.** `campo.json.meta.filtro` registra qué se incluyó, qué se
   excluyó y por qué carpetas.

## Lo que NO existe (y por eso se financia)

| Capacidad | Estado | Cómo se comprobó |
|---|---|---|
| Exportación a formato de portafolio | **no existe** | Sólo hay descarga de JSON en el código |
| Superficie pública accesible | **no existe** | El servicio escucha en 127.0.0.1 |
| Bucle de curaduría ejercido | **no ejercido** | `curaduria.json` tiene 0 decisiones |
| Vocabulario visual normalizado | **sucio** | `azul` (59) y `Azul` (10) como categorías distintas |
| Validación con artistas externos | **inexistente** | Sin registro de uso por terceros |
| Modo multiusuario | **no existe** | Servicio de un solo operador |

## Advertencia de uso

Esta ficha acredita **disponibilidad del servicio, estructura de datos y
propiedades de diseño**. No acredita eficacia, adopción, ni que el orden
propuesto mejore la comprensión de un archivo. Ninguna postulación de este
paquete afirma lo contrario.
