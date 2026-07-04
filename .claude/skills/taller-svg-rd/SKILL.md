---
name: taller-svg-rd
description: >-
  Playbook tecnico para PRODUCIR piezas SVG de Reduciendo Dano (brief de packs de
  eventos, flyers de suplementos, planos/riders) y derivarlas a PDF, manteniendolas
  editables en Illustrator y en el SVG Studio del hub. Cubre: logo RD vectorial inline
  (crisp, sin raster roto), paletas por fondo (dark neon / grises / blanco monocromo),
  SVG con capas nombradas, PDF via Edge headless (sin cairosvg/inkscape), merge con
  pypdf, vectorizar texto a curvas, y los arreglos de portabilidad Windows (cp1252,
  fuente DejaVu). Invocar al generar/editar piezas SVG->PDF de RD, arreglar un logo que
  se rompe al zoom, montar la version blanca/impresion de un brief, refinar flyers
  (centrar titulo, quitar duplicados, revectorizar), o habilitar edicion web de una pieza.
  Destilada de la sesion 2026-07-04 (asistente Cauce).
---

# Taller SVG RD - pipeline de produccion de piezas

Complementa a `entregas-rd` (playbook comercial). Aqui vive el COMO tecnico:
generar SVG, derivar PDF, dejar editable, sin reinventar ni pisar bugs ya resueltos.

## Cuando invocar

- Generar/regenerar brief de packs de eventos, flyers de suplementos, plano/rider.
- "El logo se ve roto al hacer zoom" -> es raster embebido; pasar a vectorial inline.
- Montar la version blanca/impresion (monocromo) de una pieza.
- Refinar flyers: centrar titulo, quitar duplicados, revectorizar, cambiar logo.
- Dejar una pieza editable "por la web" (SVG Studio del hub).
- Convertir SVG a PDF en Windows sin cairosvg/inkscape.

## Reglas duras (romperlas rompe la entrega)

1. **Logo SIEMPRE vectorial inline**, nunca PNG base64. El raster rompe el gotero/gotas
   al hacer zoom. Terna en `assets/logo/`:
   - `RD_logo_vector_negro.svg`  -> fondo CLARO/blanco (gota negra + RD blanco)
   - `RD_logo_vector_blanco.svg` -> fondo OSCURO (gota blanca + RD negro)
   - `RD_logo_vector_color.svg`  -> dark neon (si existe; lo prepara el usuario)
   El ® del logo queda como `<text>` (esta en toda fuente): es seguro dejarlo.
   Los tres son variantes del logo real (§4 v4.1): NO regenerar con IA.
2. **Encoding utf-8 SIEMPRE** en `open()` de JSON/SVG/txt. Windows usa cp1252 por
   defecto y CRASHEA con acentos (`UnicodeDecodeError: byte 0x8d ...`).
   `open(path, encoding="utf-8")` / `Path(p).read_text(encoding="utf-8")`.
3. **Moneda CLP** formato `$250.000`. Tarifas del jefe (2026-07-02): informativo 250.000,
   con testeo 300.000 (6 vol), servicio completo evento masivo 500.000 (15 vol). No inventar.
4. **ONG sin fines de lucro**: nada de "MAS ELEGIDO"/"mas vendido" ni lenguaje promocional.
5. **Canvas fijos**: flyer suplementos 2000x2800 (10x14cm). Brief/plano A4 (2100x2970
   vertical / 2970x2100 horizontal, 10u = 1mm). Cambiarlos rompe el validador.
6. **Borrado destructivo**: listar EXACTO que se borra y confirmar antes. Todo es
   recuperable con git (recordarselo al usuario).

## Recetas

### A - Logo vectorial inline (el fix del "logo roto")

Helper reutilizable (mismo en todos los generadores):

```python
def inline_logo(variant, x, y, w):
    raw = open(f"assets/logo/RD_logo_vector_{variant}.svg", encoding="utf-8").read()
    inner = raw[raw.index("<svg"):]                    # descartar <?xml?>
    h = round(w * 817.61 / 1060, 1)                    # aspect real del logo
    return inner.replace("<svg ", f'<svg x="{x}" y="{y}" width="{w}" height="{h}" ', 1)
```

Se incrusta como `<svg>` anidado (conserva su viewBox y estilos). Reemplaza al
`<image ... base64 ...>`. Generar variantes negro/blanco desde el vector maestro
(`C:/rd/recursos/LOGO RD.svg`, gota negra + RD blanco) intercambiando fills:
blanco = `Gota fill #fff` + letras `#fff->#000` en el `<style>`.

### B - Paletas por fondo

- **blanco** (RECOMENDADA para ONG/impresion): fondo `#FFFFFF`, tinta `#141414`,
  bordes/acentos negros, grises de jerarquia, logo `negro`. Sale la mas limpia.
- **dark** (rave v4.1): fondo `#0A0A0A`, magenta `#C800C8`, amarillo `#FFD21F`,
  logo `blanco` (o `color` cuando exista).
- **gris** (dark en grises): fondo oscuro, rampa de grises con jerarquia (no
  luminancia pura), logo `blanco`.
Parametrizar la paleta como dict `P` y construir la pieza una sola vez con `P[...]`.
Borde neon SIN filtros SVG: dos `<rect>` stroke (ancho op .16 + fino op .55).

### C - SVG con capas nombradas (editable)

Grupos `<g id="...">`: `fondo_editable`, `header`/`header_marca`, `titulo`, `cajas_editables`,
`proporciones`, `footer`. En Illustrator = grupos nombrados. El FONDO en su propia capa
`fondo_editable` -> el usuario lo oculta/reemplaza con sus disenos ("fondo extraible").
Titulo centrado: `text-anchor="middle"` en CX = ancho/2 (1000 en canvas 2000).

### D - SVG -> PDF con Edge headless (Windows, sin cairosvg/inkscape)

`cairosvg` no carga libcairo en Windows; no hay inkscape/rsvg. Usar Edge:

```bash
EDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
"$EDGE" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf-no-header \
  --user-data-dir="$SCRATCH/edge_profile" --print-to-pdf="OUT.pdf" "file:///WRAPPER.html"
```

WRAPPER.html inlinea el SVG con `@page{size:A4;margin:0}` (o `size:100mm 140mm` para
flyer) y `svg{width:...;height:...}`. Preserva vector. El `ERROR ...task_manager...` de
Edge es inofensivo. Screenshot de verificacion: `--screenshot=OUT.png --window-size=W,H`
(hz aspecto correcto) + Read del PNG.

### E - Merge / bundle con pypdf (y pagina en blanco)

Edge suele meter una 3a pagina en blanco. Tomar solo las paginas reales:

```python
from pypdf import PdfReader, PdfWriter
def take(src,n): r=PdfReader(src); return [r.pages[i] for i in range(min(n,len(r.pages)))]
# bundle = packs(1 pag) + plano/rider(2 pag)  -> 3 paginas, 0 blancos
```

Usar rutas con `/` (forward slash) en Python: `\b` en f-strings se vuelve backspace.

### F - Vectorizar (texto -> curvas)

`gen_vectorizar.py IN.svg OUT.svg`. En Windows la fuente DejaVu se resuelve via
matplotlib (`mpl-data/fonts/ttf/DejaVuSans[-Bold].ttf`), no la ruta Linux hardcodeada.
El logo deja su ® como `<text>` (2 por pieza): tolerar (no assert duro). El titulo
centrado queda como paths (por eso ya no hay `text-anchor` en el vectorizado: es correcto).

### G - Editar la pieza "por la web" (SVG Studio)

Poner el SVG en `svg/<grupo>/nombre_editable.svg` (con "editable" en el nombre).
El hub lo lista via `/api/list-svg-works`; el editor `parseSvgToConfigElements`
descompone los `<text>` en elementos editables (si >=3). Controles disponibles
(anadidos esta sesion en `web/src/components/SvgVisualizer.tsx`): Fuente (Helvetica/
Arial/Courier), peso Black, Tamano, Alinear al margen (1+ elementos), Margen editable.
El editor no reescribe el archivo: edita y **descarga** el SVG.
Rebuild del hub tras tocar `web/src`: `cd web && npm run build:context` (regenera
`context/flujo_hub.html`); refrescar navegador (Ctrl+F5).

### H - Monitoreo del hub por log

`FLUJO_WEB_DEBUG=1 py -m flujo app` (segundo plano). SIN esa env var el servidor
silencia el log (`hub.py` override de `log_message`). Con ella, cada GET/POST queda
registrado -> se puede narrar la actividad del usuario. Auto-bump de puerto: leer el
puerto real del banner, no asumir 8765.

## Diagnostico rapido

| Sintoma | Causa | Fix |
|---|---|---|
| Logo roto al zoom | PNG base64 raster | Receta A (vector inline) |
| `UnicodeDecodeError 0x8d` al generar | `open()` sin utf-8 (cp1252) | anadir `encoding="utf-8"` |
| `FileNotFoundError DejaVuSans...ttf` | ruta fuente Linux | resolver via matplotlib |
| `quedaron <text> sin convertir` | ® del logo | assert -> warning (Receta F) |
| PDF con pagina en blanco extra | Edge print-break | `take(pdf, n_real)` con pypdf |
| ruta con `\x08rief...` | `\b` en f-string Python | usar `/` en rutas |
| SVG no aparece en SVG Studio | fuera de `svg/<grupo>/` | mover y nombrar `*_editable.svg` |
| controles de la tool no aparecen | bundle viejo | `npm run build:context` + Ctrl+F5 |

## Estructura de entrega

- Job en `jobs/AAAA-MM-DD_slug/` (SVG + PDF + JSON + `flows/gen_*.py` reproducible).
- ZIP con carpetas: `editables_svg/`, `vectorizado_svg/`, `vectorizado_pdf/`.
- JSON de datos (valores + proporciones) junto a los renders.
- Actualizar `brief.yaml` + `estado.md` del job al cerrar (sin datos personales).

## Referencias del repo

- `.claude/skills/entregas-rd/` - playbook comercial + generadores (gen_dark_fronts.py,
  gen_dark_backs.py, gen_vectorizar.py, gen_cotizacion_dark_html.py, gen_plano_dark.py).
- `assets/logo/RD_logo_vector_{negro,blanco,color}.svg` - logo vectorial (terna).
- `web/src/components/SvgVisualizer.tsx` / `PlanoTool.tsx` - editor del hub.
- `linea_editorial/v4.1.md` - fuente de verdad visual (§0 rave, §6.H crema).
- `src/flujo/web/hub.py` - servidor del hub (SSE, list-svg-works, log_message).
