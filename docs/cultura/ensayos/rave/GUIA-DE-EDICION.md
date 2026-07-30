# 🛠 Guía de edición — Sistema de íconos «El Informe Rave»

Respuesta corta a tus tres preguntas:

1. **¿Puedo editar y que la animación siga intacta?** → Sí. Los colores y las
   velocidades están declarados como variables al inicio de cada archivo.
   Cambiarlos **no puede** romper la animación.
2. **¿Qué se puede editar?** → Prácticamente todo, en 4 niveles de riesgo (abajo).
3. **¿Con qué tener cuidado?** → Con 6 cosas concretas, todas detectables
   corriendo `python3 herramientas/validar.py` antes de publicar.

---

## 📁 Estructura

```
informe-rave/
├── iconos/                    ← AQUÍ EDITAS TÚ (16 archivos .svg)
│   ├── 01-paradise-garage.svg
│   ├── 02-warehouse-house-chicago.svg
│   └── ... (hasta 16)
├── datos/
│   └── iconos.json            ← títulos y descripciones de las tarjetas
├── herramientas/
│   ├── validar.py             ← revisa que no rompiste nada
│   ├── construir.py           ← regenera galeria.html desde /iconos
│   └── extraer.py             ← (ya se usó; no hace falta volver a correrlo)
├── exportados/                ← PNG que generes
├── galeria.html               ← GENERADO. No lo edites a mano.
└── GUIA-DE-EDICION.md
```

### El ciclo de trabajo

```bash
# 1. edita los .svg que quieras en /iconos (cualquier editor de texto)
# 2. revisa que todo esté sano
python3 herramientas/validar.py
# 3. regenera la galería
python3 herramientas/construir.py
# 4. abre galeria.html en el navegador
```

> **Truco:** cada `.svg` funciona solo. Puedes arrastrar
> `iconos/05-shoom-smiley-acid-house.svg` directo al navegador y verlo animado,
> sin pasar por la galería. Así iteras más rápido.

---

## 🎨 Nivel 1 — Riesgo CERO (cambia lo que quieras)

Al inicio de cada `.svg` hay un bloque así:

```css
/* ══ PALETA — edita libremente estos valores ══ */
svg{
  --fondo: #12120a;
  --aura:  #d7ff2e;
  --cara:  #e8ff33;
  /* ── velocidades (mayor = más lento) ── */
  --vel-cara:      3s;
  --vel-parpadeo:  4s;
  --vel-goteo:     2.6s;
}
```

**Puedes cambiar cualquier valor de la derecha sin ningún riesgo.**

| Qué cambias | Cómo | Ejemplo |
|---|---|---|
| Un color | cualquier color CSS válido | `--cara: #ff00aa;` o `--cara: tomato;` |
| Transparencia | usa hex de 8 dígitos | `--aura: #d7ff2e80;` (50% opaco) |
| Velocidad | sube o baja los segundos | `--vel-cara: 8s;` (más lento) |
| Congelar algo | ponle un valor enorme | `--vel-goteo: 9999s;` |

**Regla de oro:** cambia solo lo que está **después de los dos puntos**.
Nunca renombres la variable (`--cara` debe seguir llamándose `--cara`).

### Paletas por ícono

Cada archivo tiene sus propios nombres, en español y descriptivos
(`--papel`, `--tinta`, `--sol`, `--corazon`, `--hormigon`, `--piel-1`…`--piel-6`,
`--sello`, `--glitch-a`…). Ábrelo y los verás listados arriba.

---

## ✏️ Nivel 2 — Riesgo BAJO (fácil y seguro)

### Mover, escalar o rotar un elemento
Envuélvelo en un `<g>` con `transform`. El lienzo va de `0,0` a `120,120`:

```xml
<g transform="translate(0,-6)">      <!-- 6 unidades hacia arriba -->
<g transform="scale(1.15)">          <!-- 15% más grande -->
<g transform="rotate(12 60 60)">     <!-- 12° sobre el centro -->
```

### Cambiar grosores de línea
Busca `stroke-width="3"` y cámbialo. Valores 1–6 funcionan bien a este tamaño.

### Cambiar textos
Los `<text>` son editables directamente:
```xml
<text x="60" y="115" text-anchor="middle">20.000 — 80.000</text>
```
Con `text-anchor="middle"`, el texto se centra en la `x` que le des —
así que puedes alargarlo sin que se descuadre. Si se sale del cuadro,
baja el `font-size`.

⚠️ **Ojo con los símbolos**: dentro de un SVG, `&` debe escribirse `&amp;`,
`<` como `&lt;` y `>` como `&gt;`. Si escribes `Rock & Roll` tal cual,
el archivo deja de abrir.

### Cambiar la opacidad de una capa
Añade `opacity=".5"` a cualquier elemento o grupo.

---

## 🔧 Nivel 3 — Riesgo MEDIO (se puede, con cuidado)

### Borrar un elemento
Se puede, **pero borra la etiqueta completa**, de `<` a `/>`:

```xml
✅ <circle cx="60" cy="58" r="42" fill="var(--cara)"/>     ← borra la línea entera
❌ <circle cx="60" cy="58" r="42"                          ← quedó abierta = roto
```
Si el elemento tiene `class="i5f"` y lo borras, la regla CSS `.i5f` queda
huérfana: inofensivo, el validador te lo dirá como aviso (⚠), no como error.

### Ajustar una animación
Los `@keyframes` son editables. Puedes cambiar los porcentajes y los valores:

```css
@keyframes i5wob{
  0%,100%{transform:rotate(-7deg) scale(1)}
  50%    {transform:rotate(7deg) scale(1.05)}   /* sube a 15deg para más drama */
}
```
**No cambies el nombre** del keyframe (`i5wob`) a menos que también lo cambies
en la línea `animation:` que lo invoca. El validador detecta este error.

### Reordenar capas
En SVG **no existe z-index**: lo que va después se dibuja encima.
Para mandar algo al fondo, muévelo más arriba en el archivo.

### Cambiar el punto de giro
```css
.i5f{transform-origin:60px 58px}   /* si rota raro, es esto */
```
Debe apuntar al centro visual del elemento que rota.

---

## ⚠️ Nivel 4 — Aquí sí puedes romper cosas

Estas son las **6 cosas que hay que cuidar**:

| # | Peligro | Qué pasa | Cómo evitarlo |
|---|---|---|---|
| 1 | **Renombrar una variable** (`--cara` → `--kara`) | El elemento se vuelve negro o invisible | Cambia el valor, no el nombre |
| 2 | **Etiqueta sin cerrar** | El SVG no abre (pantalla en blanco) | Toda etiqueta termina en `/>` o tiene su `</tag>` |
| 3 | **`&` `<` `>` sin escapar en textos** | El archivo no parsea | Usa `&amp;` `&lt;` `&gt;` |
| 4 | **Cambiar el `viewBox`** | Se descuadran todas las coordenadas | Déjalo en `0 0 120 120` |
| 5 | **Duplicar un `id`** al copiar/pegar entre archivos | Gradientes y filtros se mezclan mal | Renombra el id **y** su `url(#id)` |
| 6 | **Renombrar una clase solo en un lado** | La animación deja de correr | Cámbiala en el CSS **y** en el `class=` |

### El seguro contra todo esto

```bash
python3 herramientas/validar.py
```

Te dice exactamente qué está mal y en qué archivo:

```
05-shoom-smiley-acid-house.svg
  ✗ var(--cara) usada pero NO declarada en la paleta
  ⚠ regla .i5ring sin elementos que la usen (animación muerta)
```

- **✗ = error real.** El ícono se ve mal. Arréglalo.
- **⚠ = aviso.** Es solo desorden, no rompe nada.

Detecta: XML mal formado, viewBox alterado, variables no declaradas,
keyframes inexistentes, clases descolgadas, ids duplicados y `url(#…)` rotos.

---

## 🧩 Copiar un ícono para hacer variantes

```bash
cp iconos/05-shoom-smiley-acid-house.svg iconos/17-mi-version.svg
```

Luego agrégalo a `datos/iconos.json` para que aparezca en la galería:

```json
{
  "n": "17",
  "archivo": "17-mi-version.svg",
  "slug": "17-mi-version",
  "titulo": "Mi versión",
  "descripcion": "Texto que aparece bajo el ícono.",
  "estilo": "Estilo propio"
}
```

Y corre `construir.py`. Si el ícono copiado tenía `<defs>` con gradientes
(el 04, 09, 14 y 16 los tienen), **renombra sus ids** para que no choquen:
`id="g4s"` → `id="g17s"`, y también `fill="url(#g4s)"` → `fill="url(#g17s)"`.

---

## 🖼 Exportar a PNG

```bash
pip install cairosvg pillow
python3 herramientas/exportar_png.py           # 512 px por defecto
python3 herramientas/exportar_png.py 1024      # tamaño a gusto
```

Los PNG salen en `/exportados`. Nota: el PNG es una **foto fija** del primer
fotograma; la animación solo vive en el SVG y en el HTML.

---

## 💡 Ideas rápidas para darle tu estilo

**Unificar la paleta de los 16** (que dejen de ser 16 estilos y sean un sistema):
elige 3 colores y reemplaza `--fondo`, el color dominante y el acento en cada archivo.

**Volverlos todos monocromos** para impresión: pon todos los colores en negro
y el fondo en blanco.

**Bajar el ritmo general**: multiplica por 2 todas las variables `--vel-*`.
Quedan más elegantes y menos "demo".

**Modo silencioso**: pon todas las `--vel-*` en un valor altísimo y tendrás
la versión estática, útil para PDF o papel.
