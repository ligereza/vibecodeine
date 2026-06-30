# HANDOFF v0.48.6 - SVG Rendering Fix (Correcto)

## Problema Real
El SVG del repo se cargaba como data URI pero se renderizaba como `<image>` dentro de `<svg>`, lo cual no funciona.
Los demos funcionan porque renderizan elementos SVG nativos (`<rect>`, `<text>`) directamente.

## Solucion
1. svg_image se renderiza FUERA del SVG del canvas, como `<img>` HTML absolutamente posicionado
2. El contenedor del canvas tiene `position: relative`
3. renderCfgEl ahora retorna null para svg_image (no se renderiza dentro del SVG)

## Cambios
- web/src/components/SvgVisualizer.tsx:
  - Contenedor del canvas: `position: relative`
  - svg_image: renderizado fuera del SVG con img posicionado
  - renderCfgEl: svg_image retorna null

## Verificacion
- npm run typecheck: OK
- npm run build:context: OK

## Apply
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "v0.48.6"
