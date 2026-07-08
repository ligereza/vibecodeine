---
name: entregas-rd
description: Playbook probado para producir entregables comerciales/visuales de Reduciendo Dano (cotizaciones de eventos, flyers de suplementos con QR, planos operativos) respetando la linea editorial v4.1 y el validador del repo. Invocar cuando el usuario pida cotizacion, flyer, reverso, plano, rider o variantes dark/neon del sistema RD.
---

# Entregas RD — playbook operativo

Skill destilada de la sesion 2026-07-02 (chat "Vibo"). Codifica lo que funciono
para que sesiones futuras no reinventen el flujo.

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
   NO usar los datos DEMO de `src/flujo/comercial/suplementos_config.py`
   (tienen telefonos falsos +1 809).
3. **Texto institucional** viene de `datadrops/Propuesta_Reduciendo_Dano.txt`.
4. **Logo RD** NUNCA se regenera con IA (regla dura §0 de v4.1). Usar el
   asset real: `assets/logo/RD_logo_A_transparente.png` (216x171, extraido
   por chroma key desde `datadrops/2026-06-22_154643_0_raveeditrdrealv5/rave_edit_rd_real_v5.png`).
5. **Paletas coexisten pero NO se mezclan**:
   - Sistema CREMA (v4.1 §6.H) — para IMPRESION de suplementos: fondo `#F6EFE3`,
     verde `#173F2F`, amarillo `#F5C54D`, tinta `#161513`.
   - Sistema RAVE (v4.1 §0) — para DIGITAL/nocturno: negro `#0A0A0A`, magenta
     `#C800C8`, amarillo neon `#FFD21F`, blanco ceramico `#F2F2F2`.
6. **Canvas obligatorio flyer suplementos**: 2000x2800 px (10x14 cm @300dpi).
   Cambiarlo rompe el validador.
7. **QR** siempre con tarjeta blanca de zona quieta >= 4 modulos.
   Apunta a `https://reduciendodano.cl`.
8. **Handoff obligatorio al cierre**: actualizar `context/LAST_HANDOFF.md`
   (ASCII-only) y `context/SESSION_STATE.json` con fecha/version reales.
9. **Push bloqueado en web** — entregar por airdrop (`_airdrop/` en la raiz
   del ZIP) + reporte de verificacion.

## Recetas

### Receta A — cotizacion general de eventos (sin lugar/fecha)

Uso: cuando la piden agencias o para prospectar productoras. Estructura del
documento entregado en `datadrops/cotizacion_general_eventos/`:
`cotizacion_general_eventos.md` + `.html` (imprimible a PDF) + plano SVG +
rider TXT. La plantilla vive en `plantillas/cotizacion_general.template.md`.

Pasos:
1. Crear job `jobs/YYYY-MM-DD_slug/` con `pedido_original.txt` y `brief.yaml`.
2. Redactar el markdown desde la plantilla, sustituyendo tarifas.
3. Generar el HTML membretado con la paleta crema (default) o rave (dark).
4. Adjuntar plano (receta C) y rider con checklist de 17 items.
5. Copiar los archivos finales a `datadrops/cotizacion_general_eventos/`
   (jobs/ es local por convencion; datadrops/ persiste).

### Receta B — reversos de suplementos con QR

Usa `generadores/gen_backs.py` (crema) y `generadores/gen_dark_backs.py`
(dark). Ambos:
- respetan la estructura `<g id>` canonica (fondo/marco/header/titulo/cajas/
  contenido/bloque_qr/footer),
- validan que el texto no desborde las cajas (assert antes de escribir),
- generan QR vectorial via `qrcode` (ERROR_CORRECT_M, zona quieta 4 modulos),
- pasan `py -m flujo suplementos validate` sin hallazgos.

Ajustables: `title`, `desc_paras`, `items`, `accent`, `box1/box2` (posicion y
altura de las cajas), `desc_wrap` / `item_wrap` (ancho de linea). Si el
assert de desborde falla, subir el `_wrap` o bajar el `_lead`.

Reglas visuales que YA aplican los generadores:
- Zona blanca del QR: 48 px de padding (~4 modulos).
- Cuerpo minimo 24 px; headings 48 px; titulo 76-85 px.
- Margen seguro 120 px lateral, 74 px inferior sobre el footer.

Comando de verificacion post-generacion (obligatorio):

```bash
PYTHONPATH=src python3 -m flujo suplementos validate svg/suplementos_rd/02_editables_svg/*.svg
```

### Receta C — plano operativo (simbologia PlanoTool)

Usa `generadores/gen_plano.py` (crema) o `generadores/gen_plano_dark.py`
(rave, con sello RD abajo a la derecha). Ambos replican el SVG imprimible
del componente `web/src/components/PlanoTool.tsx` (canvas 2970x2100,
simbologia tecnica idempotente al tool, leyenda tecnica 2 columnas).

Modificar la lista `SYMBOLS` para agregar/quitar simbolos: cada tupla es
`(key, label, x, y, w, h)`. Los `key` validos estan en la constante
`ZONE_COLORS` del propio generador.

No usar `py -m flujo plano <json> -o` — genera un plano viejo con motor
distinto sin la simbologia. La receta correcta es siempre el generador.

### Receta E — frentes dark de la linea completa (8 productos)

Usa `generadores/gen_dark_fronts.py`. Lee el JSON maestro completo y genera
los 8 frentes en `svg/suplementos_rd/05_dark_neon/NN_<slug>_dark.svg`
(2000x2800, sistema rave, logo real embebido). Mejoras sobre los reversos:

- Cajas de altura DINAMICA con tope de crecimiento 1.5x: el contenido se mide
  primero y las cajas se reparten el alto disponible; el sobrante se centra
  como aire simetrico (productos cortos no quedan inflados).
- Texto centrado verticalmente dentro de cada caja.
- Ajuste de linea por presupuesto de pixeles (`wrap_px`), no por conteo fijo.
- Kicker canonico "PRODUCTO"/"LINEA" (OJO: no usar la palabra S-U-P-L-E-M-E-N-T-O
  sola en mayusculas en ningun texto — es placeholder del validador y falla).
- Soporta los 3 modelos de contenido del JSON: desc+items, desc+versions+usage
  (Proteina) y general (linea completa).
- `PER_ID_ACCENT` permite forzar acento por producto (Pre Fiesta usa magenta
  RD para no chocar con el violeta de Hongos).

### Receta F — vectorizar (texto a curvas) sin Illustrator

Usa `generadores/gen_vectorizar.py IN.svg OUT.svg [...]`. Convierte cada
<text> a <path> con las curvas reales de DejaVu Sans/Bold via fontTools
(mismo resultado que los archivos de 03_final_vectorizado_svg). Respeta
x/y, tamano, peso, fill y text-anchor. Convenciones de salida:
- frentes crema -> 03_final_vectorizado_svg/NN_slug_vectorizado.svg
- piezas dark   -> 06_dark_vectorizado_svg/NN_slug_dark_vectorizado.svg
Las galerias 04_preview/preview_flyers.html (crema) y
preview_flyers_dark.html (dark) enlazan editable + vectorizado por pieza.

### Receta D — variantes dark

Toda pieza dark:
- fondo `#0A0A0A`, panel `#161318`,
- borde neon magenta `#C800C8` (dos capas: ancho + fino, opacidades .16 y .55
  simulan glow SIN filtros SVG — Illustrator los rechaza),
- headings en amarillo `#FFD21F` con `text-shadow` en HTML,
- sello RD (logo real, embebido base64),
- QR mantiene fondo blanco (jamas neon: rompe el escaneo).

Los generadores dark reciben la misma tabla `CONTENT` que los crema. Cambiar
solo la paleta, la estructura sobrevive.

## Diagnostico rapido si algo falla

| Sintoma | Causa probable | Fix |
|---|---|---|
| `validate` falla por dimensiones | canvas != 2000x2800 | no tocar viewBox |
| `validate` falla por placeholders | quedaron `NOMBRE DEL SUPLEMENTO` etc. | reemplazar todos |
| Texto desborda caja | `_wrap` muy corto o `_lead` alto | ajustar en `CONTENT` |
| QR no escanea | zona blanca < 4 modulos, o modulos sobre neon | usar `qr_svg()` tal cual |
| Push da 403 | sesion web solo lectura | entregar por airdrop |
| Commit "Unverified" | falta autor `noreply@anthropic.com` | ya esta configurado en el runtime |

## Entregables minimos por sesion

1. Archivos finales en sus rutas del repo.
2. Renders PNG de verificacion (usar cairosvg + Chromium headless).
3. PDF de la cotizacion (Chromium `--print-to-pdf`).
4. Handoff `HANDOFF_YYYY-MM-DD_<tema>.md` en raiz.
5. `context/LAST_HANDOFF.md` + `context/SESSION_STATE.json` actualizados.
6. Airdrop ZIP validado (`py scripts/validate_airdrop.py`).
7. Reporte formal de verificacion (formato en CLAUDE.md).

## Referencias fijas del repo

- `linea_editorial/v4.1.md` — LA fuente de verdad visual (§0 rave, §6.H crema).
- `CLAUDE.md` — contrato operativo (verificacion, airdrop, continuidad).
- `docs/CONTRAPORTADAS_SUPLEMENTOS_RD.md` + `_OPERATIVO.md` — pre-prensa.
- `docs/BRIEF_SUPLEMENTOS_RD.md` — intake por tipo de pieza.
- `web/src/components/PlanoTool.tsx` — simbologia tecnica canonica.
- `src/flujo/eventos/presets.py` — presets UNDER/BASE/MAINSTREAM.
- `datadrops/Propuesta_Reduciendo_Dano.txt` — texto institucional.
