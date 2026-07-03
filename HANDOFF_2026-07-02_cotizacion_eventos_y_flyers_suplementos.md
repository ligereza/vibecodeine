# HANDOFF 2026-07-02 - cotizacion general eventos + reversos QR suplementos

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
   editorial). Se crearon 2 reversos con QR en el sistema institucional crema.

## Archivos entregados

EVENTOS (datadrops/cotizacion_general_eventos/):
- cotizacion_general_eventos.md (fuente editable)
- cotizacion_general_eventos.html (membretado RD, imprimir a PDF con Ctrl+P)
- plano_servicio_completo_generico.svg (formato 2970x2100 del Plano/Rider Pro
  web, con la simbologia tecnica y LEYENDA TECNICA del tool - 13 simbolos)
- rider_servicio_completo_generico.txt (checklist 17 requerimientos del tool)
- pedido_original.txt (pedido del jefe)

SUPLEMENTOS (svg/suplementos_rd/02_editables_svg/):
- 09_post_fiesta_back_qr_editable.svg (reverso Post Fiesta: ficha + QR)
- 10_linea_suplementos_back_qr_editable.svg (reverso linea general + QR)
Contenido verbatim/subconjunto del JSON maestro aprobado
(projects/piezas_vectoriales/suplementos_rd/01_contenido/). QR vectorial
decodifica exacto a https://reduciendodano.cl (v2 25x25, EC=M, zona blanca
4 modulos). Validador flujo: 10/10 SVGs OK.

Paquete de envio de flyers recomendado (QA):
- Par general: 01_linea_suplementos_rd_editable.svg + 10 (reverso QR)
- Par Post Fiesta: 08_post_fiesta_editable.svg + 09 (reverso QR)
- Frentes individuales 02-07 ya existentes.

## Variantes DARK / NEON (pedido posterior del jefe)

Sistema rave oficial de linea_editorial/v4.1.md (Negro RD #0A0A0A, Blanco
ceramico #F2F2F2, Magenta RD #C800C8, Amarillo RD #FFD21F). Logo RD Version A
REAL extraido del composite oficial rave_edit_rd_real_v5.png por recorte +
chroma key (NO regenerado con IA) y guardado como
assets/logo/RD_logo_A_transparente.png (asset que v4.1 marcaba PENDIENTE).

- svg/suplementos_rd/02_editables_svg/11_post_fiesta_back_qr_dark_editable.svg
- svg/suplementos_rd/02_editables_svg/12_linea_suplementos_back_qr_dark_editable.svg
  (validator OK; QR mantiene tarjeta blanca para escaneo; sin filtros SVG)
- datadrops/cotizacion_general_eventos/cotizacion_general_eventos_dark.html
- datadrops/cotizacion_general_eventos/plano_servicio_completo_generico_dark.svg
  (misma simbologia/leyenda del PlanoTool en paleta rave + sello RD)

LINEA COMPLETA DARK (2026-07-03, pedido del jefe "todos adaptados"):
- svg/suplementos_rd/05_dark_neon/ — los 8 FRENTES de la linea en sistema
  rave (01 linea general a 08 post fiesta), generados con
  .claude/skills/entregas-rd/generadores/gen_dark_fronts.py desde el JSON
  maestro. Cajas de altura dinamica con texto centrado, ajuste de linea por
  pixeles, logo real embebido, validator 8/8 OK.
- Pre Fiesta usa acento magenta RD para diferenciarse de Hongos (violeta).

VECTORIZADOS (2026-07-03): gen_vectorizar.py (fontTools, curvas DejaVu
reales) genero los 12 vectorizados: 8 frentes dark + 2 reversos dark en
svg/suplementos_rd/06_dark_vectorizado_svg/ y los 2 reversos crema 09/10 en
03_final_vectorizado_svg/ (pendiente historico resuelto). Galeria nueva:
04_preview/preview_flyers_dark.html con editable+vectorizado por pieza.

Nota editorial: la version CREMA sigue siendo la valida para impresion de
suplementos segun v4.1 §6.H; las dark son variantes digitales/nocturnas
(uso que v4.1 asigna a la Version A del logo y al sistema rave).

## Comandos de uso

```bash
py -m flujo suplementos validate svg/suplementos_rd/02_editables_svg/09_post_fiesta_back_qr_editable.svg
py -m flujo suplementos validate svg/suplementos_rd/02_editables_svg/10_linea_suplementos_back_qr_editable.svg
py -m flujo plano jobs/<job>/evento_masivo_generico.json --rider
```

## Riesgos o pendientes reales

- Datos de contacto directo (correo/telefono) del documento de cotizacion:
  "por definir con coordinacion RD". Confirmar con el jefe antes de enviar.
- WhatsApp real de RD sigue sin definir (pendiente historico del brief);
  los reversos usan solo web + redes (contenido aprobado).
- No existen versiones vectorizadas (texto a curvas) de 09/10 en
  03_final_vectorizado_svg/; generarlas en Illustrator si la imprenta lo pide.
- Faltan reversos QR de los 6 productos individuales (02-07) si se quiere el
  sistema frente/reverso completo.
- Issue #6 [SUPLEMENTOS] etiqueta Omega 3 sigue estado/por-revisar (24-jun).
- MATERIAL NUEVO del chat de diseno: NO llego al repo (origin/main sin
  commits nuevos; ningun issue posterior al 24-jun) y no aparece en Adobe
  Creative Cloud (solo 4 videos Firefly del 31-ene y biblioteca del 10-abr;
  los proyectos de Adobe Express no son listables por API). Falta que el
  usuario indique donde esta o lo suba.

## Reporte Formal de Verificacion y Tolerancia Cero a Errores

- py -m compileall src/flujo: no aplica (no se toco codigo Python del paquete)
- py -m pytest tests/ -q: no aplica (docs/SVG/datadrops solamente)
- cd web && npm run build:context: no aplica (web/ no se toco)
- py -m flujo suplementos validate (10 SVGs de 02_editables_svg): OK
- py -m flujo plano evento_masivo_generico.json --validate: OK
- QA independiente (subagente): paleta/contraste/margenes/estructura OK,
  QR decodificado por matriz = https://reduciendodano.cl exacto
- Render visual verificado (cairosvg + Chromium) en cotizacion, plano y flyers
