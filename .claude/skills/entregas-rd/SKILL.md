---
name: entregas-rd
description: Playbook probado para producir entregables comerciales/visuales de Reduciendo Dano (cotizaciones de eventos, flyers de suplementos con QR, planos operativos) respetando la linea editorial v4.1 y el validador del repo. Invocar cuando el usuario pida cotizacion, flyer, reverso, plano, rider o variantes dark/neon del sistema RD.
---

# Entregas RD — playbook operativo

Skill destilada de la sesion 2026-07-02 (identidad "Vibo", primero en un
contenedor cloud sin push, despues terminada en la maquina local del usuario
con Windows + Git Bash). Codifica lo que funciono para que sesiones futuras
no reinventen el flujo.

## Cuando invocar

- "Cotizacion" / "propuesta" / "brief comercial" de eventos.
- "Flyer" / "reverso" / "contraportada" / "QR" de suplementos.
- "Plano" / "rider" / "layout" de intervencion en terreno.
- "Version dark" / "neon" / "rave" de cualquier pieza institucional.

## Reglas duras (romperlas invalida la entrega)

1. **Moneda CLP** con formato `$1.234.000`. No inventar precios: si no los
   conoces, pregunta o deja "A definir". Los del jefe (2026-07-02) son:
   informativo $250.000 · informativo+testeo $300.000 (6 vol) · servicio
   completo evento masivo $500.000 (15 vol).
2. **Contenido de suplementos** viene VERBATIM de
   `projects/piezas_vectoriales/suplementos_rd/01_contenido/contenido_suplementos_rd.json`.
   Cargarlo con `json.load` y tomar los campos tal cual (title, description,
   items) — no reescribir el texto de memoria. NO usar los datos DEMO de
   `src/flujo/comercial/suplementos_config.py` (tienen telefonos falsos +1 809).
3. **Texto institucional** viene de `datadrops/Propuesta_Reduciendo_Dano.txt`.
4. **Logo RD** NUNCA se regenera con IA (regla dura §0 de v4.1). Usar el
   asset real: `assets/logo/RD_logo_A_transparente.png` (216x171, extraido
   por chroma key desde `datadrops/2026-06-22_154643_0_raveeditrdrealv5/rave_edit_rd_real_v5.png`).
   Si no existe, recrearlo con el mismo metodo (ver receta E).
5. **Dos paletas del repo, decidir cual segun el uso real de la pieza**:
   - Sistema CREMA (v4.1 §6.H) — regla dura para IMPRESION de suplementos:
     fondo `#F6EFE3`, verde `#173F2F`, amarillo `#F5C54D`, tinta `#161513`.
   - Sistema RAVE/dark (v4.1 §0) — para DIGITAL/nocturno (WhatsApp, IG,
     cotizaciones): negro `#0A0A0A`, magenta `#C800C8`, amarillo neon
     `#FFD21F`, blanco ceramico `#F2F2F2`.
   Si el usuario pide "todo dark" para una pieza que va a IMPRENTA, avisale
   una vez que el flyer viejo que fallo (`datadrops/flyers/BACK.SUPLEMENTOS.pdf`)
   era justamente negro/neon vacio — es el anti-patron documentado en v4.1.
   Si insiste, procede en dark y dejalo explicito en el commit/handoff como
   decision del usuario, sin insistir mas ("no seas porfiado, estilo dark").
6. **Canvas obligatorio flyer suplementos**: 2000x2800 px (10x14 cm @300dpi).
   Cambiarlo rompe el validador.
7. **QR** siempre con tarjeta blanca de zona quieta >= 4 modulos (48px de
   padding sobre el modulo). Apunta a `https://reduciendodano.cl`.
8. **Handoff obligatorio al cierre**: actualizar `context/LAST_HANDOFF.md`
   (ASCII-only) y `context/SESSION_STATE.json` con fecha/version reales.
9. **QA visual real = Illustrator local del usuario**, no un renderizador
   headless. Para el paquete final de piezas graficas usar
   `py -m flujo suplementos illustrator <nombres...>` y que el usuario lo
   revise en su Illustrator antes de imprimir. Los renders PNG que generes
   tu mismo (ver receta F) son solo para tu propia verificacion rapida
   durante la sesion, no reemplazan el QA en Illustrator.
10. **Push**: si trabajas en un contenedor cloud sin acceso de escritura al
    repo (403 en git push), entrega por airdrop (`_airdrop/` en la raiz del
    ZIP) + reporte de verificacion. Si trabajas en la maquina local del
    usuario con Git Bash, commitea y pushea de verdad — no hay razon para
    airdrop ahi.

## Recetas

### Receta A — cotizacion general de eventos (sin lugar/fecha)

Uso: cuando la piden agencias o para prospectar productoras. Estructura del
documento entregado en `datadrops/cotizacion_general_eventos/`:
`cotizacion_general_eventos.md` + `.html` (imprimible a PDF) + `_RD_dark.pdf`
+ plano SVG + rider TXT. La plantilla vive en
`plantillas/cotizacion_general.template.md`.

Pasos:
1. Crear job `jobs/YYYY-MM-DD_slug/` (carpeta local, gitignored salvo
   `_template`) con `pedido_original.txt`, `brief.yaml`,
   `evento_masivo_generico.json` (o el JSON del evento real), `estado.md`,
   `resultado.md`.
2. Redactar el markdown desde la plantilla, sustituyendo tarifas.
3. Generar el HTML membretado con la paleta que corresponda (ver regla 5).
   Ver `generadores/gen_cotizacion_dark_html.py` como referencia de
   estructura (header con logo real embebido en base64, tablas, plano
   inline, footer).
4. Adjuntar plano (receta C) y rider con checklist de 17 items.
5. Copiar los archivos finales a `datadrops/cotizacion_general_eventos/`
   (jobs/ es local por convencion; datadrops/ persiste y se commitea).
6. Generar el PDF final (ver receta F para el metodo en Windows).

### Receta B — reversos de suplementos con QR

Usa `generadores/gen_dark_backs.py` como base (adaptar paleta si se pide
crema). El script:
- carga el contenido VERBATIM desde el JSON maestro (regla dura 2),
- respeta la estructura `<g id>` canonica (fondo/marco/header/titulo/cajas/
  contenido/bloque_qr/footer),
- valida que el texto no desborde las cajas (assert antes de escribir),
- genera QR vectorial via `qrcode` (ERROR_CORRECT_M, zona quieta 4 modulos),
- pasa `py -m flujo suplementos validate` sin hallazgos.

Ajustables: `box1/box2` (posicion y altura de las cajas), `desc_wrap` /
`item_wrap` (ancho de linea), `desc_lead`/`item_lead` (interlineado). Si el
assert de desborde falla, subir el `_wrap` o bajar el `_lead`/`_gap`.

Numeracion de archivos: seguir el correlativo de
`svg/suplementos_rd/02_editables_svg/` (01-08 = frentes crema canonicos).
Los reversos van despues del ultimo numero usado, sin reservar rangos para
crema vs dark si solo se produce una paleta en la sesion.

Comando de verificacion post-generacion (obligatorio):

```bash
py -m flujo suplementos validate svg/suplementos_rd/02_editables_svg/*.svg
```

(usar `py`, no `python`, en Windows — ver AGENTS.md)

### Receta C — plano operativo (simbologia PlanoTool)

Usa `generadores/gen_plano_dark.py` como base (adaptar paleta si se pide
crema). Replica el SVG imprimible del componente
`web/src/components/PlanoTool.tsx` (canvas 2970x2100, simbologia tecnica
idempotente al tool, leyenda tecnica 2 columnas, sello RD con el logo real
embebido en base64).

Modificar la lista `SYMBOLS` para agregar/quitar simbolos: cada tupla es
`(key, label, x, y, w, h)`. Los `key` validos estan en la constante
`ZONE_COLORS` del propio generador.

No usar `py -m flujo plano <json> -o` — genera un plano viejo con motor
distinto sin la simbologia. La receta correcta es siempre el generador.

### Receta D — variantes dark

Toda pieza dark:
- fondo `#0A0A0A`, panel `#161318`,
- borde neon magenta `#C800C8` (dos capas: ancho + fino, opacidades .16 y .55
  simulan glow SIN filtros SVG — Illustrator los rechaza),
- headings en amarillo `#FFD21F` (con `text-shadow` en HTML, con doble
  texto desplazado 4px en SVG para simular glow sin filtros),
- sello RD (logo real, embebido base64, `assets/logo/RD_logo_A_transparente.png`),
- QR mantiene fondo blanco (jamas neon: rompe el escaneo).

### Receta E — recuperar el logo real (si `assets/logo/` no existe)

```python
from PIL import Image
import colorsys

img = Image.open("datadrops/2026-06-22_154643_0_raveeditrdrealv5/rave_edit_rd_real_v5.png").convert("RGB")
W, H = img.size
crop = img.crop((int(W*0.385), int(H*0.065), int(W*0.635), int(H*0.245)))
# mascara alpha por HSV: transparenta el fondo claro/desaturado del mockup,
# deja opaco el logo (magenta/amarillo saturado)
out = Image.new("RGBA", crop.size)
px, po = crop.load(), out.load()
for y in range(crop.size[1]):
    for x in range(crop.size[0]):
        r, g, b = px[x, y]
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        if s < 0.18 and v > 0.55:
            a = 0
        elif s < 0.30 and v > 0.55:
            a = int(255 * (s - 0.18) / 0.12)
        else:
            a = 255
        po[x, y] = (r, g, b, a)
out.crop(out.getbbox()).save("assets/logo/RD_logo_A_transparente.png")
```

NUNCA regenerar el logo con un modelo de IA — solo recorte + chroma-key
determinista sobre el asset real ya existente en el repo.

### Receta F — verificacion visual en Windows (sin cairosvg)

`cairosvg` falla en Windows por defecto (`OSError: no library called
"cairo-2"` — falta la libreria nativa de Cairo, `pip install cairosvg` no
la trae). En vez de instalar el runtime de GTK3, usa el Edge que ya viene
con Windows en modo headless:

```bash
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  --headless=new --disable-gpu --no-sandbox \
  --screenshot="$(pwd)/ruta/salida.png" \
  --window-size=2000,2800 --hide-scrollbars \
  "file:///$(pwd)/ruta/archivo.svg"
```

Importante: `--window-size` debe ser >= al tamano real del canvas del SVG/
HTML (o el screenshot recorta al viewport en vez de mostrar todo). Para
PDF de un HTML, mismo binario con `--print-to-pdf=salida.pdf
--no-pdf-header-footer` en vez de `--screenshot`.

Esto es SOLO para tu propia verificacion rapida durante la sesion — el QA
real de las piezas graficas pasa por Illustrator (regla dura 9).

## Diagnostico rapido si algo falla

| Sintoma | Causa probable | Fix |
|---|---|---|
| `validate` falla por dimensiones | canvas != 2000x2800 | no tocar viewBox |
| `validate` falla por placeholders | quedaron `NOMBRE DEL SUPLEMENTO` etc. | reemplazar todos |
| Texto desborda caja | `_wrap` muy corto o `_lead` alto | ajustar en `CONTENT` |
| QR no escanea | zona blanca < 4 modulos, o modulos sobre neon | usar `qr_svg()` tal cual |
| `cairosvg` falla en Windows | falta libreria nativa Cairo | usar Edge headless (receta F) |
| Screenshot recortado | `--window-size` menor al canvas | igualar tamano de ventana al viewBox |
| Push da 403 en sesion cloud | acceso de solo lectura | entregar por airdrop |
| Push funciona pero en repo local no | confundiste sesion cloud con local | verificar `pwd` / ruta antes de asumir |
| Commit "Unverified" | falta autor `noreply@anthropic.com` | ya esta configurado en runtimes cloud; en local usa el git config del usuario |

## Entregables minimos por sesion

1. Archivos finales en sus rutas del repo.
2. Renders PNG de verificacion propia (Edge headless en Windows, ver receta F).
3. PDF de la cotizacion si aplica (Edge headless `--print-to-pdf`).
4. Handoff `HANDOFF_YYYY-MM-DD_<tema>.md` en raiz.
5. `context/LAST_HANDOFF.md` + `context/SESSION_STATE.json` actualizados.
6. Si estas en sesion cloud sin push: airdrop ZIP validado
   (`py scripts/validate_airdrop.py`). Si estas en maquina local: commit +
   push real, sin airdrop.
7. Reporte formal de verificacion (formato en AGENTS.md).

## Referencias fijas del repo

- `linea_editorial/v4.1.md` — LA fuente de verdad visual (§0 rave, §6.H crema).
- `AGENTS.md` — contrato operativo (verificacion, airdrop, continuidad).
- `docs/CONTRAPORTADAS_SUPLEMENTOS_RD.md` + `_OPERATIVO.md` — pre-prensa.
- `docs/BRIEF_SUPLEMENTOS_RD.md` — intake por tipo de pieza.
- `web/src/components/PlanoTool.tsx` — simbologia tecnica canonica.
- `src/flujo/eventos/presets.py` — presets UNDER/BASE/MAINSTREAM.
- `datadrops/Propuesta_Reduciendo_Dano.txt` — texto institucional.
- `assets/logo/README.md` — procedencia del logo real extraido.
