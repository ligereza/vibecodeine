# HANDOFF 2026-07-03 - Adobe Toolkit (Illustrator / Photoshop / After Effects + panel CEP)

Version: 0.48.5 (sin bump: entrega de herramientas .jsx/panel, no toca src/flujo)
Fecha: 2026-07-03
Asistente: Vibo

## Que se hizo

Nuevo toolkit de automatizacion Adobe bajo `tools/`, siguiendo el patron .jsx que ya
usaba `tools/illustrator/` (IIFE, `#target`, prompts/alerts en espanol sin acentos,
export desde documentos temporales para no tocar el documento del usuario).

Scripts:
- `tools/illustrator/scripts/titles_to_photos.jsx` : bloque de texto -> cada linea como PNG/JPG individual (conserva fuente/tamano/color).
- `tools/illustrator/scripts/logo_revector_extrude.jsx` : JPEG de baja calidad -> trazado de imagen (BW/color) + extrusion 3D vectorial (copias apiladas/oscurecidas) -> exporta vector (SVG/EPS/PDF) + PNG.
- `tools/illustrator/scripts/logo_revector_batch.jsx` : lo mismo por lotes sobre una carpeta entera de imagenes.
- `tools/photoshop/scripts/layers_to_photos.jsx` : cada capa (o solo texto) -> PNG recortado con transparencia, desde duplicado temporal.
- `tools/after_effects/scripts/titles_to_comps.jsx` : bloque de texto -> una comp por titulo, centrada, con fundido.
- `tools/after_effects/scripts/auto_titles_mixer_ae.jsx` : una comp por titulo con ecualizador (efecto Audio Spectrum) + titulo que LATE con el volumen (Convert Audio to Keyframes + expresion). Usa match names / indices para funcionar con AE en espanol o ingles.

Panel (addon) CEP para las tres apps:
- `tools/adobe_panel/` : CSXS/manifest.xml, index.html, css/style.css, js/CSInterface.js (minimo), js/main.js (dispatcher), .debug, README.md, build_zxp.ps1. Los botones cambian segun la app activa y ejecutan los .jsx del repo (fuente unica; ruta configurable en `REPO_TOOLS` de main.js).

Docs:
- `tools/ADOBE_TOOLKIT.md` : indice y guia de uso.
- `tools/adobe_panel/README.md` : instalacion CEP (PlayerDebugMode) + empaquetado .zxp.

## Como se usa

- Illustrator/Photoshop: `Archivo > Secuencias de comandos > Explorar...` > `<script>.jsx`
- After Effects: `Archivo > Secuencias de comandos > Ejecutar archivo...` > `<script>.jsx`
- Panel CEP: ver `tools/adobe_panel/README.md` (activar PlayerDebugMode + copiar a la carpeta de extensiones; opcional firmar .zxp con `build_zxp.ps1` + ZXPSignCmd.exe).

## Decisiones / notas

- CEP (no UXP) para el panel: unica tecnologia que cubre AI+PS+AE en un solo bundle hoy.
- Extrusion 3D vectorial en vez de efecto 3D vivo (fragil/dependiente de version): exporta limpio a SVG/EPS/PDF + PNG. Para 3D foto-realista, aplicar `Efecto > 3D y materiales` manual sobre el vector.
- El mixer usa efectos nativos apuntando a la capa de audio; el "pulso" necesita Convert Audio to Keyframes (comando de menu, con variantes ES/EN). Si no se encuentra, el ecualizador igual reacciona y el script avisa como hacerlo a mano (renombrar la capa creada a `AUDIO_AMP`).

## Riesgos / pendientes (verificar en la app del usuario - regla de oro)

- La API de trazado de imagen (threshold, cornerAngle, ...) varia entre versiones; va en try/catch, pero probar el batch con 2-3 JPEG reales.
- Convert Audio to Keyframes: nombre de menu localizado; confirmar en el AE del usuario.
- CSInterface.js es minimo (cubre lo usado); si algo falla, reemplazar por el oficial de Adobe (Adobe-CEP/CEP-Resources).
- .zxp no se genera aqui: `build_zxp.ps1` lo automatiza con ZXPSignCmd.exe (a descargar) + certificado autofirmado.

## Estado git

- El auto-checkpoint ya commiteo los archivos a `main` (commit 257157a "checkpoint: feat: sesion vibo completa"). Arbol limpio.
- Pendiente: `git push` a origin (https://github.com/ligereza/vibecodeine). Esta sesion es local (usuario LIGEREZA, dueno del repo), asi que el push funciona.

## Verificacion

Reporte Formal de Verificacion y Tolerancia Cero a Errores
- py -m compileall src/flujo: no aplica (no se toco Python)
- py -m pytest tests/ -q: no aplica (no se toco Python/tests)
- cd web && npm run build:context: no aplica (no se toco web)
- py -m flujo verify: no aplica
- py scripts/validate_airdrop.py: OK (VALIDACION OK)
- Observaciones: entrega solo de herramientas .jsx/panel bajo tools/. Verificacion final real corresponde al usuario en Illustrator/Photoshop/After Effects (regla de oro).
