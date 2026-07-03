# HANDOFF 2026-06-30 - SVG Studio fixes

## Que se hizo

Fixed 3 issues in SVG Studio:

### 1. Hub.py - SVG limit per group (8 -> 50)
- File: src/flujo/web/hub.py
- Line: groups[gname] = items[:50]
- Previously limited to 8 SVGs per group, now supports 50

### 2. svgIndex.ts - Mock data from demo to real
- File: web/src/data/svgIndex.ts
- Replaced MOCK_SVG_INDEX demo data (330x130 fake labels)
- Now uses 16 real SVGs from repo (2000x2800 flyers)

### 3. SvgVisualizer.tsx - Dimension fallback
- File: web/src/components/SvgVisualizer.tsx
- Changed fallback from {width:1600, height:1000} to {width:2000, height:2800}

## Archivos modificados

- src/flujo/web/hub.py
- web/src/components/SvgVisualizer.tsx
- web/src/data/svgIndex.ts
- context/flujo_hub.html (rebuilt)
- context/plano_demo.html (rebuilt)
- context/svg_visualizer.html (rebuilt)

## Verificacion

After apply:
1. cd web && npm run typecheck && npm run build:context && cd ..
2. py -m compileall src/flujo
3. py -m pytest tests/ -q
4. py scripts/hub_smoke.py
