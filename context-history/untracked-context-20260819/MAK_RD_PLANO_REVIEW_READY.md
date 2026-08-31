# Expediente review_ready: RD Plano/Rider y geometria de venue

Estado: `review_ready` como slice tecnico local. No significa que una venue
este modelada, que una medida este confirmada ni que exista una propuesta
comercial enviada.

## Fuente y origen

- Proyecto activo: `/home/mak/flujo/projects/plano/`
- Motor headless: `/home/mak/flujo/projects/plano/plano_stands.py`
- Motor comun: `/home/mak/flujo/src/flujo/plano/`
- Referencia teatral: `/home/mak/flujo/projects/plano/referencia_plano_teatro.py`
- Idea y reglas: `/home/mak/flujo/projects/plano/README.md`
- Feedback y pendientes: `/home/mak/flujo/projects/plano/feedback.md`
- Entrada validada: `/home/mak/flujo/projects/plano/ejemplos/evento_ejemplo.json`
- Interfaz HTML: `/home/mak/flujo/projects/plano/plano_editor.html`

El README y el feedback describen `referencia_plano_teatro.py` como el
generador radial original de teatro/sala asociado a SCD Plaza Egaña, con
escenario curvo, sagita, bloques de butacas alineados radialmente y balcón.
Se conserva como origen matematico/referencia, no como servicio activo.

## Separacion de capas

### Activo y portable

`plano_stands.py` delega en `flujo.plano` y funciona headless. Recibe JSON de
evento y produce:

- SVG del layout;
- rider tecnico de texto;
- modulos, pasillos, mesas, sillas, testeo y contencion segun reglas;
- costos derivados cuando el motor de costos es consumidor.

### Referencia historica y especializada

`referencia_plano_teatro.py` contiene la geometria radial de butacas y
balcon. Requiere GUI (`customtkinter` + `matplotlib`) para ejecutarse, por lo
que solo fue compilado en esta fase. No se instala esa GUI ni se fuerza dentro
del runtime headless.

## Consumidores comprobados

- `GET http://127.0.0.1:8900/departments/rd`: HTTP 200.
- `GET http://127.0.0.1:8900/api/rd/summary`: HTTP 200; consume el catalogo RD
  sin mezclar la base de campo.
- `GET http://127.0.0.1:8900/context/plano_demo.html`: HTTP 200.
- `GET http://127.0.0.1:8765/plano_demo.html`: HTTP 200.
- `GET http://127.0.0.1:8765/flujo_hub.html`: HTTP 200.
- `data/rd.db`: catalogo canonico integro y con datos.
- `data/rd_datos.db`: frontera de campo vacia; no se fusiona con `rd.db`.

## Validacion foreground

```text
py_compile de plano_stands.py, referencia_plano_teatro.py y flujo.plano
-> codigo 0

plano_stands.py evento_ejemplo.json
-> codigo 0; SVG valido; 8719 bytes; contiene PLANO, stands y contencion

plano_stands.py evento_ejemplo.json --rider
-> codigo 0; rider valido; 692 bytes; contiene alimentacion, 2 mesas y contencion

external_calls=0
operational_mutations=0
```

## Relacion con venue, VJ y RD

El mismo modelo puede crecer desde un rider RD de stands hacia una escena de
venue: escenario, accesos, baños, zona medica, pantallas, FOH, pasillos,
butacas y balcon. La salida sigue siendo geometria y reglas, no una promesa
de medidas reales. La relacion con VJ aparece en layout de pantallas, zonas de
operacion y lectura espacial; no introduce dependencia de hardware ni OSC.

## Pendientes que bloquean una version de venue

- Confirmar medidas reales de toldos, mesas, sillas y pasillos RD.
- Convertir reglas del brief a configuracion declarativa completa.
- Extender el solver desde fila/grid a escenario, accesos y zonas reales.
- Integrar la geometria radial de butacas como adaptador separado, no copiar
  la GUI al motor headless.
- Definir entradas tecnicas VJ/pantallas y sus restricciones verificables.
- Validar una venue concreta con planos o medidas autorizadas.
- Completar editor visual/exportacion y costos sin inventar datos.

## Decision de integracion

El motor activo queda dentro de `flujo` como herramienta offline portable. La
referencia SCD queda clasificada como genealogia matematica reutilizable. No se
fusionan ambos scripts por nombre, no se instala `customtkinter`, no se altera
ninguna base RD y no se publica una venue sin evidencia de medidas.
