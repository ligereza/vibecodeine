#!/usr/bin/env python3
"""Genera cotizacion_general_eventos.html en dark/neon (paleta rave v4.1 SS0),
con el logo RD real embebido en el header y el plano dark embebido inline.
Ejecutar desde la raiz del repo, despues de correr gen_plano_dark.py.
Salida: datadrops/cotizacion_general_eventos/cotizacion_general_eventos.html
"""
import base64
from pathlib import Path

logo_b64 = base64.b64encode(open("assets/logo/RD_logo_A_transparente.png", "rb").read()).decode()
plano_dark = Path("datadrops/cotizacion_general_eventos/plano_servicio_completo_generico_dark.svg").read_text(encoding="utf-8").strip()

HTML = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cotización general (dark) — Reduciendo Daño Chile</title>
<style>
  :root{
    --bg:#0A0A0A; --panel:#161318; --panel2:#1E1A21; --ink:#F2F2F2; --muted:#A79FA8;
    --magenta:#C800C8; --magenta2:#B100B8; --yellow:#FFD21F; --violet:#8B4DFF;
    --line:#3A2F3D; --white:#FFFFFF;
  }
  *{box-sizing:border-box; margin:0; padding:0;}
  body{
    background:var(--bg); color:var(--ink);
    font-family:"DejaVu Sans", Arial, Helvetica, sans-serif;
    font-size:14px; line-height:1.55;
  }
  .page{max-width:860px; margin:0 auto; padding:36px 44px; background:var(--bg);}
  header.doc{
    display:flex; align-items:center; justify-content:space-between;
    border-bottom:3px solid var(--magenta); padding-bottom:18px; margin-bottom:26px;
    box-shadow:0 22px 34px -30px rgba(200,0,200,.55);
  }
  .brand{display:flex; align-items:center; gap:14px;}
  .brand img.rdlogo{width:76px; height:auto; display:block; filter:drop-shadow(0 0 14px rgba(177,0,184,.55));}
  .brand .name{font-weight:700; font-size:20px; color:var(--ink); text-shadow:0 0 18px rgba(200,0,200,.35);}
  .brand .sub{color:var(--muted); font-size:12px;}
  .doctag{
    background:var(--magenta2); color:var(--white); border:2px solid var(--yellow); border-radius:999px;
    padding:6px 16px; font-weight:700; font-size:12px; letter-spacing:.06em;
    box-shadow:0 0 18px rgba(200,0,200,.45);
  }
  h1{font-size:26px; line-height:1.25; margin-bottom:6px; color:var(--white); text-shadow:0 0 26px rgba(200,0,200,.45);}
  .lead{color:var(--muted); margin-bottom:26px; max-width:640px;}
  h2{
    color:var(--yellow); font-size:17px; letter-spacing:.02em;
    margin:30px 0 10px; padding-bottom:6px; border-bottom:2px solid var(--line);
    text-shadow:0 0 16px rgba(255,210,31,.35);
  }
  h3{font-size:14.5px; margin:16px 0 6px; color:var(--ink);}
  p{margin-bottom:10px;}
  ul{margin:6px 0 12px 20px;}
  li{margin-bottom:6px;}
  .card{
    background:var(--panel); border:1px solid var(--line); border-radius:14px;
    padding:18px 20px; margin:12px 0;
    box-shadow:0 0 0 1px rgba(200,0,200,.22), 0 0 22px -6px rgba(200,0,200,.35);
  }
  table{width:100%; border-collapse:collapse; margin:12px 0; background:var(--panel); border-radius:10px; overflow:hidden;
    box-shadow:0 0 0 1px rgba(200,0,200,.25), 0 0 24px -8px rgba(200,0,200,.4);}
  th{
    background:var(--magenta2); color:var(--white); text-align:left;
    padding:10px 12px; font-size:12.5px; letter-spacing:.04em;
  }
  td{padding:10px 12px; border-bottom:1px solid var(--line); vertical-align:top;}
  tr:last-child td{border-bottom:none;}
  td.num, th.num{text-align:right; white-space:nowrap; font-variant-numeric:tabular-nums;}
  tr.total td{background:var(--panel2); font-weight:700; border-top:2px solid var(--yellow); color:var(--yellow);}
  .destacado td{background:#241428; font-weight:700; color:var(--white);}
  .nota{color:var(--muted); font-size:12px;}
  .plano-wrap{background:var(--panel); border:1px solid var(--magenta); border-radius:14px; padding:12px; margin:12px 0;
    box-shadow:0 0 26px -6px rgba(200,0,200,.5);}
  .plano-wrap svg{width:100%; height:auto; display:block; border-radius:8px;}
  footer.doc{
    margin-top:34px; padding-top:16px; border-top:3px solid var(--magenta);
    display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap;
  }
  .lema{font-weight:700; color:var(--yellow); text-shadow:0 0 16px rgba(255,210,31,.4);}
  .contacto{color:var(--muted); font-size:12.5px; text-align:right;}
  @media print{
    *{-webkit-print-color-adjust:exact; print-color-adjust:exact;}
    .page{max-width:none; padding:10mm 14mm;}
    h2{break-after:avoid;}
    .card, table, .plano-wrap{break-inside:avoid;}
    @page{size:A4; margin:0; background:#0A0A0A;}
    body{background:#0A0A0A;}
  }
</style>
</head>
<body>
<div class="page">

  <header class="doc">
    <div class="brand">
      <img class="rdlogo" alt="RD" src="data:image/png;base64,__LOGO_B64__">
      <div>
        <div class="name">Reduciendo Daño</div>
        <div class="sub">ONG · Chile · desde 2018 · reduciendodano.cl</div>
      </div>
    </div>
    <div class="doctag">COTIZACIÓN GENERAL</div>
  </header>

  <h1>Intervención en terreno para fiestas, festivales y eventos masivos</h1>
  <p class="lead">Documento general de presentación de servicios y tarifas, sin
  lugar ni fecha definidos, pensado para ser reenviado por agencias y
  productoras a sus eventos.</p>

  <h2>Quiénes somos</h2>
  <p>Fundada en 2018, <strong>Reduciendo Daño</strong> es una ONG líder en
  implementación y formulación de políticas e insumos de reducción de daños en
  Chile, pionera en la fabricación y distribución de implementos, reactivos y
  servicios de análisis de sustancias psicoactivas en el país.</p>
  <p>Desarrollamos proyectos de intervención en terreno orientados a fiestas,
  espacios de ocio y eventos donde existe consumo de sustancias psicoactivas,
  acercando herramientas de prevención, reducción de riesgos y educación
  preventiva, y promoviendo decisiones informadas, el autocuidado y espacios
  más seguros.</p>

  <h2>Qué hacemos</h2>

  <div class="card">
    <h3>1 · Stand Informativo</h3>
    <p>Personas capacitadas (analistas químicos, químicos farmacéuticos,
    psicólogos) responden inquietudes, orientan a asistentes y entregan
    consejos preventivos sobre el consumo de sustancias psicoactivas. Se
    distribuye material educativo y elementos de apoyo: protectores auditivos,
    abanicos, suplementos pre y post fiesta y accesorios de reducción de
    riesgos. También pueden entregarse tests de un solo uso.</p>
  </div>

  <div class="card">
    <h3>2 · Stand de Testeo</h3>
    <p>Complementa al stand informativo con <strong>análisis colorimétricos de
    sustancias psicoactivas, gratuitos para los asistentes</strong>. Es uno de
    los ejes centrales de Reduciendo Daño: fuimos la primera organización en
    implementar este tipo de intervenciones en Chile. A partir de los
    resultados se entregan orientaciones personalizadas, incluyendo
    recomendaciones de no consumo ante adulterantes o sustancias con mayor
    potencial de daño del esperado.</p>
  </div>

  <div class="card">
    <h3>3 · Intervención y Contención en Eventos Masivos</h3>
    <p>Rondas preventivas para detectar situaciones que requieran apoyo, y
    contención psicológica en crisis o desregulación emocional que no
    requieran intervención médica, aliviando la carga de los dispositivos
    médicos del evento. Se recomienda un espacio de descanso de baja
    estimulación sensorial junto al stand.</p>
  </div>

  <p><strong>Coordinación operativa:</strong> el equipo trabaja coordinado con
  producción, seguridad privada y equipos médicos del evento. Nuestro enfoque
  prioriza el cuidado, la información y el acompañamiento, evitando prácticas
  estigmatizantes o punitivas.</p>

  <h2>Beneficios para el evento</h2>
  <ul>
    <li><strong>Asistentes:</strong> información preventiva y educativa,
    espacios más seguros, apoyo cercano libre de estigmas, atención temprana
    ante ansiedad, malos viajes o desregulación emocional.</li>
    <li><strong>Producción:</strong> menos conflictos y situaciones críticas,
    menor carga sobre equipos médicos, derivación oportuna a emergencias,
    mejor percepción de seguridad, apoyo al cumplimiento de protocolos y una
    imagen de evento responsable y comprometido con su comunidad.</li>
  </ul>

  <h2>Tarifas (CLP, por día de evento)</h2>
  <table>
    <thead>
      <tr><th>Servicio</th><th>Equipo</th><th class="num">Valor por día</th></tr>
    </thead>
    <tbody>
      <tr><td>Stand Informativo</td><td>6 voluntarios/as</td><td class="num">$250.000</td></tr>
      <tr><td>Stand Informativo + Testeo</td><td>6 voluntarios/as</td><td class="num">$300.000</td></tr>
      <tr class="destacado"><td>Servicio Completo — evento masivo<br>
        <span class="nota">informativo + testeo + contención</span></td>
        <td>15 voluntarios/as</td><td class="num">$500.000</td></tr>
    </tbody>
  </table>

  <h3>Desglose — Servicio Completo evento masivo</h3>
  <table>
    <thead>
      <tr><th>Ítem</th><th>Detalle</th><th class="num">Valor</th></tr>
    </thead>
    <tbody>
      <tr><td>Equipo RD en terreno</td><td>15 voluntarios/as capacitados: analistas químicos, químicos farmacéuticos, psicólogos/as</td><td class="num">$300.000</td></tr>
      <tr><td>Stand informativo</td><td>Material educativo, protectores auditivos, abanicos e insumos preventivos</td><td class="num">$50.000</td></tr>
      <tr><td>Módulo de testeo</td><td>Análisis colorimétrico de sustancias, gratuito para asistentes; reactivos incluidos</td><td class="num">$70.000</td></tr>
      <tr><td>Intervención y contención</td><td>Rondas preventivas + zona de descanso / baja estimulación</td><td class="num">$45.000</td></tr>
      <tr><td>Coordinación operativa</td><td>Briefing previo, montaje y enlace con producción, seguridad y salud</td><td class="num">$35.000</td></tr>
      <tr class="total"><td>Total servicio completo</td><td></td><td class="num">$500.000</td></tr>
    </tbody>
  </table>
  <p class="nota">Los valores del desglose son referenciales dentro del
  paquete; el valor del servicio completo es cerrado por día de evento.</p>

  <h2>Qué necesitamos de la producción</h2>
  <ul>
    <li>Espacio para dos stands contiguos de 3×3 m (informativo + testeo) y una
    zona de contención/descanso de ~3×3 m en sector de baja estimulación
    sensorial (plano referencial abajo).</li>
    <li>3 mesas y sillas para el equipo (coordinable si las llevamos nosotros).</li>
    <li>Punto eléctrico estable e iluminación para la mesa de testeo (lectura
    nocturna). El módulo de testeo requiere ventilación.</li>
    <li>Acreditaciones para el equipo (15 personas en servicio completo; 6 en
    servicios informativos).</li>
    <li>En jornadas de más de 5 horas: alimentación para el equipo (puede
    proporcionarla la producción o añadirse al costo).</li>
    <li>Contacto de coordinación con producción, seguridad y equipo médico,
    briefing previo y acceso para carga/descarga antes de apertura.</li>
  </ul>

  <h2>Plano operativo referencial</h2>
  <div class="plano-wrap">
__PLANO_DARK__
  </div>
  <p class="nota">Distribución referencial: la ubicación final se coordina con
  producción según el recinto. Requiere sector visible, accesible y alejado de
  los parlantes principales.</p>

  <h2>Condiciones</h2>
  <ul>
    <li>Valores en pesos chilenos (CLP), por día/jornada de evento.</li>
    <li>Cotización general sin lugar ni fecha: la ubicación del evento, el
    aforo y la duración pueden ajustar el valor final. Traslados fuera del
    área urbana de origen se coordinan por separado.</li>
    <li>Las intervenciones de Reduciendo Daño Chile tienen fines
    exclusivamente preventivos, educativos y de reducción de riesgos.</li>
    <li>Documento sujeto a confirmación técnica de ONG Reduciendo Daño.</li>
  </ul>

  <footer class="doc">
    <div class="lema">Si vas a hacerlo, reduce daños.</div>
    <div class="contacto">
      reduciendodano.cl · @reduciendodano.cl<br>
      Contacto directo: por definir con coordinación RD
    </div>
  </footer>

</div>
</body>
</html>
"""

out = HTML.replace("__LOGO_B64__", logo_b64).replace("__PLANO_DARK__", "    " + plano_dark)
Path("datadrops/cotizacion_general_eventos/cotizacion_general_eventos.html").write_text(out, encoding="utf-8")
print("OK, bytes:", len(out))
