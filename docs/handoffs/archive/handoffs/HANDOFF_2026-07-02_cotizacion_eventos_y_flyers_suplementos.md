# HANDOFF 2026-07-02 - cotizacion general eventos + reversos QR suplementos (dark/neon)

## Problema resuelto

1. EVENTOS: cotizacion GENERAL (sin lugar ni fecha) para la agencia de
   marketing que contacto al jefe en el evento de Amelie Lens. Documento que
   cuenta que hace RD, por cuanto y que necesita, con tarifas fijadas por el
   jefe (CLP por dia): informativo $250.000; informativo + testeo $300.000
   (6 voluntarios); servicio completo evento masivo $500.000 (15 voluntarios)
   con desglose que suma exacto. Texto institucional tomado verbatim de
   datadrops/Propuesta_Reduciendo_Dano.txt.
2. SUPLEMENTOS: rehechos los flyers que fallaron en el chat de diseno
   (BACK.SUPLEMENTOS.pdf quedo negro/neon y casi vacio, contra la linea
   editorial). Se crearon 2 reversos con QR, esta vez con contenido real
   verbatim del JSON maestro aprobado.

## Decision de estilo (importante para continuidad)

El usuario pidio explicitamente **dark/neon para TODO** en esta sesion
(cotizacion, plano y flyers de suplementos), no solo la cotizacion. Se le
advirtio una vez que la linea editorial v4.1 SS6.H exige paleta CREMA para
IMPRESION de flyers de suplementos, y que el flyer viejo fallido era
justamente negro/neon vacio (anti-patron documentado). El usuario confirmo
que queria dark de todas formas ("no seas porfiado, estilo dark"). Se
proceso en dark/neon puro, sin version crema, dejando esta nota para que
quien imprima estas piezas sepa que falta el paso de version crema si se
necesita para produccion fisica.

## Archivos entregados

EVENTOS (datadrops/cotizacion_general_eventos/):
- cotizacion_general_eventos.md (fuente editable)
- cotizacion_general_eventos.html (dark/neon, logo real embebido, imprimir a PDF con Ctrl+P)
- cotizacion_general_eventos_RD_dark.pdf (generado con Edge headless)
- plano_servicio_completo_generico_dark.svg (formato 2970x2100 del Plano/Rider
  Pro web, simbologia tecnica y LEYENDA TECNICA del tool - 13 simbolos, mas
  sello RD real)
- rider_servicio_completo_generico.txt (checklist 17 requerimientos del tool)
- pedido_original.txt (pedido del jefe)

SUPLEMENTOS (svg/suplementos_rd/02_editables_svg/):
- 09_post_fiesta_back_qr_dark_editable.svg (reverso Post Fiesta: ficha + QR, dark/neon)
- 10_linea_suplementos_back_qr_dark_editable.svg (reverso linea general + QR, dark/neon)
Contenido verbatim/subconjunto del JSON maestro aprobado
(projects/piezas_vectoriales/suplementos_rd/01_contenido/contenido_suplementos_rd.json).
QR vectorial a https://reduciendodano.cl con tarjeta blanca (zona quieta 4
modulos, nunca sobre neon). Validador flujo: OK en ambos, sin hallazgos.

LOGO REAL (assets/logo/):
- RD_logo_A_transparente.png: logo oficial RD Version A extraido por recorte
  + chroma-key HSV desde datadrops/2026-06-22_154643_0_raveeditrdrealv5/
  rave_edit_rd_real_v5.png (NO regenerado con IA, regla dura de la linea
  editorial). Cubre el asset que v4.1 marcaba PENDIENTE en su inventario.

SKILL (.claude/skills/entregas-rd/):
- SKILL.md con reglas duras, 4 recetas, diagnostico rapido.
- generadores/gen_plano_dark.py, gen_dark_backs.py, gen_cotizacion_dark_html.py
  (los scripts reales usados para producir todo lo de arriba, reutilizables).
- plantillas/cotizacion_general.template.md.

## Comandos de uso

```bash
py -m flujo suplementos validate svg/suplementos_rd/02_editables_svg/09_post_fiesta_back_qr_dark_editable.svg
py -m flujo suplementos validate svg/suplementos_rd/02_editables_svg/10_linea_suplementos_back_qr_dark_editable.svg
py .claude/skills/entregas-rd/generadores/gen_plano_dark.py
py .claude/skills/entregas-rd/generadores/gen_dark_backs.py
py .claude/skills/entregas-rd/generadores/gen_cotizacion_dark_html.py
```

## Riesgos o pendientes reales

- Datos de contacto directo (correo/telefono) del documento de cotizacion:
  "por definir con coordinacion RD". Confirmar con el jefe antes de enviar.
- WhatsApp real de RD sigue sin definir (pendiente historico del brief);
  los reversos usan solo web + redes (contenido aprobado).
- Version CREMA de estos flyers y del plano NO se genero en esta sesion (el
  usuario pidio dark explicitamente). Si estas piezas van a IMPRENTA fisica,
  falta correr la version crema (regla dura v4.1 SS6.H) antes de imprimir.
- No existen versiones vectorizadas (texto a curvas) de los flyers 09/10 en
  03_final_vectorizado_svg/; generarlas en Illustrator si la imprenta lo pide.
- Faltan reversos QR de los 6 productos individuales (02-07) si se quiere el
  sistema frente/reverso completo.
- QA visual final pendiente en Illustrator local del usuario (regla dura de
  la skill entregas-rd) -- lo verificado aqui es solo mecanico (validador) +
  visual rapido con Edge headless.
- context/LAST_HANDOFF.md y SESSION_STATE.json estaban desactualizados desde
  2026-07-01 (mencionaban Mapping LED como "sin commit", pero ya estaba
  commiteado en 9970575 desde antes). Se corrigieron en este cierre.

## Cierre 2026-07-03

- El usuario confirmo que el se encarga de los datos de contacto de la
  cotizacion (ya no es pendiente del agente).
- El usuario decidio explicitamente NO generar version crema de los flyers
  09/10 ni del plano: dark/neon queda como version final y unica de estas
  piezas. No volver a proponer la version crema para estos archivos.

## Reporte Formal de Verificacion y Tolerancia Cero a Errores

- py -m compileall src/flujo: no aplica (no se toco codigo Python del paquete)
- py -m pytest tests/ -q: no aplica (docs/SVG/datadrops/skill solamente)
- cd web && npm run build:context: no aplica (web/ no se toco)
- py -m flujo suplementos validate (09, 10 dark): OK, sin hallazgos mecanicos
- Render visual verificado con Edge headless (msedge --headless=new
  --screenshot, window-size igual al canvas real) en cotizacion, plano y
  ambos flyers -- sin desbordes, QR nitido, logo con glow correcto
- QA en Illustrator: pendiente (usuario debe abrir los SVG en su Illustrator
  local antes de imprimir o distribuir masivamente)
