# PLAN VSCODE -- capa de indice y digest de informes (director: Cauce)

REGLA DURA: NO edites watchdog.sh, worker.py, interfaz.py, cola.py,
research.py, panel.py ni tests existentes (otro agente trabaja ahi).
Solo creas archivos NUEVOS.

1. indice.py: recorre ~/research/informes/ y ~/research/paneles/,
   genera informes/INDEX.md y paneles/INDEX.md: tabla fecha | tema |
   fuentes (del meta del .json) | link al .md. Stdlib puro, py3.11.
2. digest.py: extrae la seccion RESUMEN de cada informe de los ultimos
   7 dias y arma ~/research/DIGEST.md (un parrafo por informe + ruta).
3. Ambos idempotentes (correr 2 veces = mismo resultado) y tolerantes a
   .json corrupto (saltar con warning, no morir).
4. VERIFICACION: correlos contra los informes reales que ya existen
   (hay 3 informes + 1 panel) y pega la salida + head de INDEX.md y
   DIGEST.md en tu reporte.
Reporta en ~/research/REPORTE_VSCODE.md con salida real de comandos.

# FASE 2 -- exportar.py (archivo nuevo)

Convierte un informe .md a HTML autocontenido para compartir:
python3 exportar.py informes/<archivo>.md -> mismo nombre .html.
Estetica: fondo #0b0a09, texto #d8d3c8, acento #9db67c, monospace,
max-width 720px. Sin dependencias externas (stdlib; conversion md
simple: titulos, listas, links, negrita basta).

# FASE 3 -- estadisticas.py (archivo nuevo)

Lee el meta de todos los .json (informes/ y paneles/) y genera
~/research/USO.md: llamadas acumuladas por proveedor, errores mas
frecuentes (agrupados), busquedas Tavily totales (creditos usados
estimados: basic=1, advanced=2), duracion promedio. Sirve para vigilar
rate limits. Tolerante a json corrupto.

# FASE FINAL -- revision cruzada

Revisa el trabajo del otro agente SIN editarlo: watchdog.sh (bug fd
9>&- aplicado?), test_research_lib.py (corre verde?), worker/interfaz
(progreso /status funciona? token opcional? jobs.jsonl?). Prueba
kill-revive del watchdog dos veces seguidas (segunda vez DEBE revivir).
Escribe hallazgos en ~/research/REVISION_CRUZADA.md seccion
"## VSCode revisa Antigravity". Luego lee la seccion donde el te
reviso y corrige SOLO tus archivos. Itera hasta cerrar hallazgos.
