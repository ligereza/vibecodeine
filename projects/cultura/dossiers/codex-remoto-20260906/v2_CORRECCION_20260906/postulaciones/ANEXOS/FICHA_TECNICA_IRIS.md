# Ficha técnica del instrumento — corte 2026-09-06

Reproducible con `bash evidencia/prueba_estado.sh`; salida fechada en
`evidencia/SALIDA_PRUEBA_ESTADO.txt`. Sólo lectura.

> **Esta ficha reemplaza la versión de la v1.** Aquella describía un solo cuerpo
> de datos y afirmaba que no había decisiones humanas registradas. Son dos
> cuerpos distintos, y sí hay decisiones. La corrección está en
> `RESPUESTA_AUDITORIA.md` A2.

## Identificación

| | |
|---|---|
| Nombre operativo | IRIS — Atlas Campo del Orden |
| Superficie servida | `http://127.0.0.1:8900/portafolio/` — **sólo local**, no expuesta a internet |
| Servidor | `~/cultura/mak_plataforma/hub.py`, ThreadingHTTPServer en Python 3 |
| Interfaz | `editor.html` 256.541 bytes + `mesa_montaje.js` 122.282 bytes, sin dependencias de red |
| Estado | En funcionamiento y en uso por su autor |

## Universo A — lectura de máquina (`~/iskvw/datos/`)

| Archivo | Contenido | Cifra |
|---|---|---|
| `archivo.json` | Atlas, `fuente: todo`, generado `2026-08-29T10:38:17` | 2.034 piezas · 5.812 vínculos |
| | por clase | obra 1.826 · código 208 |
| `campo.json` | Campo activo, mtime `2026-09-02T12:52:53` | 219 piezas · 478 filtradas |
| | con percepción de máquina | **219 de 219** |
| | calidad de la proyección | `vecindad_conservada = 0.4855` |
| `micelio.json` | Grafo con umbral declarado | 1.431.380 bytes |
| `curaduria.json` | Decisiones **en este archivo** | **0**, mtime `2026-08-01` |

Tipificación completa del campo activo, que suma 219: `obra` 134 · `foto_evento`
40 · `tatuaje` 28 · `otro` 6 · `logo` 4 · `flyer_evento` 2 · `pantalla` 1 ·
`dibujo` 1 · `meme` 1 · `dibujo digital` 1 · `ficha_sustancia` 1.

**`tipo: "obra"` es tipificación del pipeline, no validación autoral.** Que 134
piezas estén marcadas `obra` no significa que el artista las haya reconocido como
obra suya.

## Universo B — decisión humana persistida (`~/plataforma/director_runs/portfolio-editor-20260808/`)

Función que la produce: `_portfolio_select_unlocked`, `hub.py` líneas 2059-2160.
Escribe en JSONL y asienta en el ledger común con control de unicidad.

| Archivo | Contenido |
|---|---|
| `PORTFOLIO_INBOX.json` | `faro-portfolio-inbox-v1`, **`status: not_public`**, **7.044 ítems**, 7.023 con asset |
| `selections.jsonl` | **87 decisiones**, 68 ítems, **14 sesiones**, `2026-08-07T21:28` → `2026-09-02T02:53` |
| | `descartar` 65 · `seleccionar` 13 · **`deseleccionar` 9** |
| | **65 de 65 descartes con `reason_code: "no_es_obra"`** · 75 filas con `provider: human` |
| `classifications.jsonl` | **103** · `human_draft` 100, `human_confirmed` 3 · **`promotion: none` en las 103** |
| `common_ledger.jsonl` | 477 filas · **123 en dominio `iskvw`**: 100 `decision`, 21 `evidence`, 2 `reject` |

**Los dos universos no comparten identificadores.** Sus cifras no se suman.

## Propiedades verificadas

1. **Sólo lectura del lado del servidor.** POST sobre la superficie servida
   devuelve **404**, comprobado. Toda edición vive en memoria del navegador.
2. **Persistencia real en el otro universo.** 87 decisiones con fecha, motivo,
   sesión y propietario.
3. **Reversibilidad ejercida, no sólo declarada.** 9 `deseleccionar` son nueve
   reversiones reales de una decisión previa.
4. **Validación autoral de obra/no-obra ejercida 65 veces**, con motivo registrado.
5. **La compuerta de publicación existe y está sin cruzar.** Inventario
   `not_public`, 103 clasificaciones en `promotion: none`, 3 confirmadas de 103.
6. **El orden declara su propia distorsión.** `vecindad_conservada` está en el
   archivo de datos, no en un informe aparte.
7. **El filtro está declarado**, en `campo.json.meta.filtro`.

## La brecha, con el nombre de cada pieza

| Pieza | Qué hace | Por qué no cubre la brecha |
|---|---|---|
| `editor.html` | Exporta **datos**: un `Blob` `application/json` con `a.download` (l. 1092, 2784-2786) | No produce un portafolio |
| `~/tools/compile_portfolio_dossier.py` + `~/flujo/src/flujo/knowledge/portfolio_dossier.py` | Compila `mak-portfolio-dossier-v1`. Carga, y **rechaza entradas vacías con 22 errores de validación** | Su contrato consume un plan y un estado de evidencia; declara que *no lee un archivo, no abre una base de datos y no publica un asset* |

> **No existe la pieza que tome el inventario más las decisiones humanas ya
> registradas y produzca un artefacto de portafolio publicable.** Eso, y no
> construir IRIS, es lo que se pide financiar.

## Lo que no está probado

**NO PROBADO** — que el instrumento sirva a alguien distinto de su autor; que
mejore la comprensión de un archivo; que sea accesible según norma; que soporte
más de un usuario; que se instale de forma autónoma en equipos de terceros.

**INEXISTENTE DEMOSTRADO** — superficie pública: el servicio escucha en
`127.0.0.1:8900`.

**NO AUDITABLE** — las mejoras de importación, reimportación y exportación de
IRIS y el ciclo de PUPILA encargados a otros agentes. Sin prueba integrada,
fechada y reproducible sobre MAK. No se citan ni se presupuestan como hechas.

## Advertencia de uso

Esta ficha acredita disponibilidad del servicio, estructura de datos, decisión
humana persistida y propiedades de diseño. **No acredita eficacia, adopción ni
que el orden propuesto mejore la comprensión de un archivo.** Ninguna postulación
del paquete afirma lo contrario.
