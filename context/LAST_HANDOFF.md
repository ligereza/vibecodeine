Date: 2026-07-06
Version: 0.48.5 (matches pyproject.toml / src/flujo/version.py)
Assistant: Cauce (formerly Vibo)
Repo: origin/main = 237114b (todo mergeado; sin ramas abiertas)

== ESTADO ACTUAL ==
Todo el trabajo de la sesion esta en main. Foco reciente: contraportadas de suplementos con
la plantilla nueva (capa CAMBIOS del .ai) via generador de repo, y el puente agente<->Illustrator
por COM (win32com DoJavaScript) sin compartir pantalla.

== LISTO ==
- Contraportadas dark de los 8 suplementos: gen_contraportadas.py rellena la plantilla
  svg/suplementos_rd/_plantilla/contraportada_cambios.svg (exportada de la capa CAMBIOS) con el
  contenido del JSON maestro; salida svg/suplementos_rd/09_contraportadas_dark/*.svg. Reproducible
  via repo (no toca el .ai del usuario).
- Puente agente<->Illustrator (tools/illustrator/ai_illustrator_bridge.jsx): export doc->state.json,
  apply ops.json (setText/setSize/setFill/setFont/move/addText; target por nombre o 'find' por
  contenido). PROBADO end-to-end en Illustrator real via COM (no destructivo).
- AI Operating Layer v1: docs/AI_OPERATING_LAYER, AI_PROVIDER_ROUTING, AIDER_API_SETUP, TASK_PROMPTS;
  .aider.conf.example.yml, .env.example; contexto_repo.py task; skill taller-svg-rd.
- Toolbox: tools/context_pack, token_budget, handoff, verify_all; tools/svg/{svg_lint,svg_to_pdf,
  recolor_svg,pack_delivery}; .githooks/pre-commit; bridges PS/AE (sin probar en app).
- Piezas SVG editables en Illustrator: fuente Arial (no DejaVu), logo RD vectorial inline, titulo
  centrado, parrafos como bloque (tspan). Flyers dark + brief packs eventos (svg/eventos_rd).

== PENDIENTE ==
- [HECHO 2026-07-06] Alineacion/tipografia de las 8 contraportadas. Bug de raiz: gen_contraportadas.py
  STRIP borraba "Capa_28" (que envuelve cajas_editables8 = las 3 cajas del diseno) y "Layer_18"
  (el logo/marca (R)), creyendo que eran texto viejo. La plantilla CAMBIOS no tiene texto viejo
  (solo el (R) del logo). Ahora STRIP=[] (conserva cajas+logo). Layout nuevo (a pedido del usuario):
  sin kicker "PRODUCTO"/"LINEA"; titulo alineado a la IZQUIERDA dentro del ovalo de cabecera
  (x 168..700, y~356), auto-ajustado a 1-2 lineas al mayor tamano legible que quepa; bloques
  Descripcion y Nutrientes ("Productos" en 01_linea) alineados a la izquierda, ocupando su caja
  (Descripcion 618..1418, Nutrientes 1478..2178), centrados verticalmente y con el cuerpo de la
  Descripcion JUSTIFICADO a lo ancho (via textLength/lengthAdjust). El cuerpo elige la mayor fuente
  legible (46..22px) que quepa en la caja, bajando solo si el contenido es denso (ej. 01_linea con
  7 productos). Logo intacto (el usuario lo dio por bueno). Verificado renderizando las 8 a PNG (Chromium).
- Logo color vectorial (assets/logo/RD_logo_vector_color.svg, lo prepara el usuario) -> cambiar la
  variante dark de 'blanco' a 'color' en los generadores.
- Probar Aider real con los perfiles (.aider.conf: Claude+Qwen / NIM / OpenRouter).  [pospuesto]
- Bridges Photoshop/After Effects sin probar en las apps reales.  [pospuesto]

== BLOQUEADORES ==
- Cuota Claude casi agotada: reservar Claude para arquitectura/review; lo barato a Qwen/NIM/OpenRouter.
- build_chataigne_noisette_experimental: falta el .noisette real para validar el schema.
- Push directo a main a veces bloqueado por guardrail: usar PR o reintentar tras fetch. Si GitHub
  falla, entregar airdrop.zip.

== PROXIMO PASO RECOMENDADO ==
Cuando haya logo color vectorial: apuntar la variante dark a 'color' y regenerar. Para editar la
plantilla CAMBIOS: bridge por COM (find contenido -> content nuevo) o re-exportar y correr
gen_contraportadas.py.
