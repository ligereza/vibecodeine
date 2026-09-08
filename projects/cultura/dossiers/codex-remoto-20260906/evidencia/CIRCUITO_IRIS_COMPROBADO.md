# Circuito IRIS: qué está implementado, qué se observó, qué falta

Fecha de medición: **2026-09-06**, entre 17:41 y 17:48 (hora de Santiago).
Método: lectura de código, lectura de datos y una prueba HTTP reproducible
(`evidencia/prueba_circuito.sh`, salida en `evidencia/SALIDA_PRUEBA_2026-09-06.txt`).
La prueba no escribe en el archivo de producción: sólo hace GET y un POST de
control cuyo resultado esperado es 404.

## 1. Qué es IRIS exactamente

El propio código lo declara. `~/cultura/mak_plataforma/hub.py`, líneas 1-11:

> "hub.py -- the human-facing MAK Hub (port 8900). (…) Its historically named
> ``/portafolio/`` route is the operator-facing IRIS ordering/curation interface
> (Atlas Campo del Orden), **not the artist's public portfolio**; ``iskvw.cl`` is a
> separate downstream site."

**Corrección a los briefs recibidos.** Los documentos de traspaso describen IRIS
como "el Portfolio Editor" y a veces como una plataforma pública de portafolio.
El código dice otra cosa: `/portafolio/` es la superficie **de operador** para
ordenar y curar (Atlas Campo del Orden). El sitio público es otro y aguas abajo.
Esta distinción cambia la formulación de una postulación de Difusión: hoy no
existe una superficie pública de obras, existe una mesa de trabajo del artista.

Rutas verificadas: el servicio escucha en `127.0.0.1:8900` (proceso `python`,
PID 971 en la medición), es decir **sólo local**, no expuesto a internet.

## 2. El circuito, paso por paso

| # | Paso del circuito | Estado | Evidencia citada |
|---|---|---|---|
| 1 | Tomar un conjunto acotado de registros | **Implementado y con datos reales** | `~/iskvw/datos/archivo.json`, generado `2026-08-29T10:38:17`: 2.034 piezas, 5.812 vínculos. `campo.json`: 219 piezas seleccionadas de un total del que se **filtraron 478** (`meta.filtradas`), con filtro declarado por carpetas `posts`/`reels`. |
| 2 | Distinguir obras y contexto | **Implementado** | `campo.json` tipifica cada pieza: `obra` 134, `foto_evento` 40, `tatuaje` 28, `logo` 4, `flyer_evento` 2, `pantalla` 1, `dibujo` 1, `meme` 1, `dibujo digital` 1, `ficha_sustancia` 1, `otro` 6. La distinción obra/contexto existe como dato, no como aspiración. |
| 3 | Ordenar según un criterio | **Implementado, parcialmente medido** | Cada pieza tiene coordenadas `x`,`y` normalizadas (proyección 2D), `colores`, `estilo` y `percibido` (descripción por visión de máquina; 219 de 219 con percepción). El archivo declara su propia calidad de proyección: `vecindad_conservada = 0.4855`. Es decir, el sistema **publica cuánto se pierde** al ordenar: algo menos de la mitad de la vecindad original se conserva. |
| 4 | Revisar relaciones | **Implementado a nivel de datos** | `archivo.json` contiene 5.812 vínculos con `de`, `a`, `peso` y `clase` (`semantico` 5.794, `etiqueta` 18). `micelio.json` (1,4 MB) conserva un grafo con umbral declarado. |
| 5 | Componer un portafolio (decisión humana) | **Contrato definido, uso real en cero** | `curaduria.json` es "la mano del artista" (así se autodocumenta): campos `titulo`, `mostrar`, `abstraccion`, `svg`, `regimen`, `peso`, `serie`, `nota`. Su diccionario `piezas` está **vacío**: `0` decisiones humanas registradas. El bucle de decisión está especificado y cableado, pero no ejercitado. |
| 6 | Exportar o preparar una salida | **Sólo descarga de JSON. No hay formato de portafolio.** | `editor.html` línea 1092: "sibling data files with fetch and its only output is a download". Líneas 2784-2786: la única salida es un `Blob` `application/json` entregado con `a.download`. Existen los botones `descargar mi curatoria` (línea 950) y `Descargar tablero.json` (línea 1061). No hay generación de PDF, web pública, catálogo ni ninguna otra forma de portafolio. |

## 3. Prueba HTTP (2026-09-06)

```
RUTA                                   HTTP  BYTES      TIPO
/portafolio/                           200   256541     text/html; charset=utf-8
/portafolio/editor.html                200   256541     text/html; charset=utf-8
/portafolio/mesa_montaje.js            200   122282     text/javascript
/portafolio/datos/archivo.json         200   1833824    application/json
/portafolio/datos/campo.json           200   93657      application/json
/portafolio/datos/obras.json           200   10048      application/json
/portafolio/datos/curaduria.json       200   625        application/json
/portafolio/datos/tablero.json         200   3966       application/json
/portafolio/CONTRATO.md                200   5068       text/markdown

POST /portafolio/datos/curaduria.json -> 404
```

**Lectura honesta de esto.** Los 200 acreditan **disponibilidad del servicio y
entrega efectiva de contenido con tamaño y tipo esperados** — es más que un
"ping", porque cada ruta devuelve el archivo real. No acreditan que un artista
complete un flujo de curaduría de principio a fin: eso no se probó con usuarios.

El POST que devuelve 404 es la prueba positiva de una propiedad de diseño, no un
fallo: `hub.py` líneas 5584-5599 sólo resuelven GET sobre `PORTFOLIO_ROOT`. La
superficie es de **sólo lectura** y el editor mantiene todas las ediciones en
memoria del navegador; el artista descarga y confirma fuera de la aplicación
(`editor.html` línea 1094: "the artist commits curaduria.json through the same gate").

## 4. Lo que se puede afirmar y lo que no

**Se puede afirmar, con archivo y línea:**
- Existe un corpus propio real: 2.034 piezas, 5.812 vínculos, 227 imágenes.
- Existe percepción computacional sobre 219 obras: color, estilo y descripción.
- Existe una tipificación obra/contexto operativa.
- Existe una métrica publicada de pérdida al ordenar (`vecindad_conservada`).
- Existe un contrato explícito de decisión humana, reversible y opcional campo a campo.
- El sistema no publica automáticamente: la salida requiere un acto del artista.

**No se puede afirmar hoy:**
- Que exista exportación a un formato de portafolio. **No existe.** Sólo descarga de JSON.
- Que exista una superficie pública de obras. No existe: el servicio es local (127.0.0.1).
- Que el bucle de decisión humana esté validado: `curaduria.json` tiene 0 decisiones.
- Que la herramienta haya sido usada por artistas distintos del autor.
- Que el orden propuesto mejore la comprensión: no hay medición con personas.

**Higiene de datos observada (declararla es mejor que ocultarla):** `campo.json`
mezcla `azul` (59) y `Azul` (10) como colores distintos, y `estilo` es texto
libre con variantes ("Surrealismo, Ilustración digital" / "Surrealismo,
ilustración digital"). La normalización del vocabulario es trabajo real
pendiente y es una actividad legítima de un presupuesto.

## 5. Consecuencia para las postulaciones

Cada una de estas tres cosas **es una actividad a financiar, no una capacidad a declarar**:

1. **Exportación a formato de portafolio** (web publicable, PDF, o ambas).
2. **Publicación** de una superficie accesible fuera de `127.0.0.1`.
3. **Ejercicio real del bucle de curaduría** con archivos y personas, empezando
   por el archivo propio, y normalización del vocabulario visual.

Un expediente que presente 1, 2 o 3 como ya resueltos sería falso frente a esta
evidencia. Un expediente que los presente como el trabajo que pide financiar es
exacto y, además, es un proyecto con alcance verificable.
