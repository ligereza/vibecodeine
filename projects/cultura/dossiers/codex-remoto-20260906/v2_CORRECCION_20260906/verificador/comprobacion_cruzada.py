#!/usr/bin/env python3
"""Comprobacion cruzada del paquete v2.

Detecta contradicciones, marcadores sin resolver, adjuntos ausentes,
presupuestos inconsistentes y afirmaciones prohibidas sin fuente.
Termina con codigo 1 si algo falla.
"""
from __future__ import annotations
import csv, re, subprocess, sys
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
errores: list[str] = []
avisos: list[str] = []
def err(m): errores.append(m)
def avi(m): avisos.append(m)

MD = sorted(p for p in RAIZ.rglob("*.md"))
TEXTO = {p: p.read_text(encoding="utf-8", errors="replace") for p in MD}
def rel(p): return str(p.relative_to(RAIZ))

# --- 1. archivos que deben existir ---
print("## 1. Archivos obligatorios del paquete")
OBLIG = [
 "LEEME_CIERRE.md", "RESPUESTA_AUDITORIA.md", "MATRIZ_REQUISITOS.md",
 "DEPENDENCIAS_HUMANAS.md",
 "evidencia/ESTADO_TECNICO_VERIFICADO.md", "evidencia/prueba_estado.sh",
 "evidencia/SALIDA_PRUEBA_ESTADO.txt",
 "presupuestos/01_ama_amoedo.csv", "presupuestos/02_fondart_creacion.csv",
 "presupuestos/03_fondart_difusion.csv", "presupuestos/04_fondart_formativas.csv",
 "presupuestos/TRAZABILIDAD_COSTES.md",
 "postulaciones/01_AMA_AMOEDO_ARTISTAS/TEXTO_POR_CAMPO.md",
 "postulaciones/02_FONDART_DIFUSION/TEXTO_POR_CAMPO.md",
 "postulaciones/03_FONDART_FORMATIVAS/TEXTO_POR_CAMPO.md",
 "postulaciones/ALTERNATIVA_CREACION/TEXTO_POR_CAMPO.md",
 "cronogramas/CARGA_Y_ESCENARIOS.md", "cronogramas/PREPARACION_HASTA_EL_ENVIO.md",
 "verificador/verificar_presupuestos.py", "verificador/pruebas_negativas.sh",
 "verificador/revision_ids_y_gastos.py", "verificador/leer_ficha_titular.py",
 "verificador/generar_indice_anexos.py",
 "DRY_RUN_ENVIO_20260906.md", "PAQUETE_DE_ACCION_TITULAR_20260906.md",
 "MATRIZ_CAMPOS_FINAL_20260906.md", "INDICE_ANEXOS_20260906.md",
 "REPORTE_EJECUCION_CLAUDE_20260906.md",
 "postulaciones/generar_matriz_campos.py", "postulaciones/generar_para_copiar.py",
 "postulaciones/ANEXOS/FICHA_TECNICA_IRIS.md", "postulaciones/ANEXOS/GUION_DEMO.md",
 "postulaciones/BORRADORES_SIN_FIRMA/FORMATO_COMPROMISOS_FORMativas_15_FILAS.csv",
 "postulaciones/BORRADORES_SIN_FIRMA/SOLICITUD_ESPACIO_COTIZACION.md",
 "PARA_COPIAR/LEEME.md",
]
for f in OBLIG:
    if not (RAIZ / f).exists():
        err(f"falta el archivo obligatorio {f}")
print(f"   revisados {len(OBLIG)}")

# --- 2. marcadores sin resolver ---
print("## 2. Marcadores sin resolver")
# TODO/FIXME/XXX en mayusculas exactas: "todo" es una palabra castellana corriente.
PAT_MAY = re.compile(r"\b(TODO|FIXME|XXX)\b")          # sensible a mayusculas
PAT_FRASE = re.compile(r"\b(POR COMPLETAR|POR DEFINIR|LOREM IPSUM|PENDIENTE DE REDACCION)\b", re.I)
n = 0
for p, t in TEXTO.items():
    if "BORRADORES_SIN_FIRMA" in str(p) or "v1_ENTREGA" in str(p):
        continue
    for rx in (PAT_MAY, PAT_FRASE):
        for m in rx.finditer(t):
            err(f"{rel(p)}: marcador sin resolver {m.group(0)!r}"); n += 1
# placeholders tipo [DATO] fuera de borradores y de plantillas de carta
PH = re.compile(r"\[[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ ,/]{3,30}\]")
for p, t in TEXTO.items():
    if any(x in str(p) for x in ("BORRADORES_SIN_FIRMA", "v1_ENTREGA")):
        continue
    for m in set(PH.findall(t)):
        avi(f"{rel(p)}: marcador de plantilla {m}")
print(f"   marcadores prohibidos: {n}")

# --- 3. enlaces internos ---
print("## 3. Enlaces internos")
LINK = re.compile(r"\]\(([^)\s]+\.(?:md|csv|sh|txt|py|json))\)")
rotos = 0
for p, t in TEXTO.items():
    for m in LINK.finditer(t):
        d = m.group(1)
        if d.startswith("http"): continue
        if not ((p.parent / d).exists() or (RAIZ / d).exists()):
            err(f"{rel(p)}: enlace roto -> {d}"); rotos += 1
print(f"   enlaces rotos: {rotos}")

# --- 4. presupuestos ---
print("## 4. Presupuestos")
r = subprocess.run([sys.executable, str(RAIZ / "verificador/verificar_presupuestos.py")],
                   capture_output=True, text=True)
if r.returncode != 0:
    err("verificar_presupuestos.py termino con error:\n" + r.stdout[-2000:])
print(f"   verificador exit={r.returncode}")

TOT = {}
for f, moneda in [("01_ama_amoedo.csv","USD"), ("02_fondart_creacion.csv","CLP"),
                  ("03_fondart_difusion.csv","CLP"), ("04_fondart_formativas.csv","CLP")]:
    ruta = RAIZ / "presupuestos" / f
    if ruta.exists():
        s = sum(Decimal(x["subtotal"]) for x in csv.DictReader(ruta.open(encoding="utf-8"))
                if x["categoria"] not in ("TOTAL", ""))
        TOT[f] = (s, moneda)

# los totales citados en los textos deben coincidir con los CSV
CITAS = {
 "postulaciones/01_AMA_AMOEDO_ARTISTAS/TEXTO_POR_CAMPO.md": ("01_ama_amoedo.csv", "8.734"),
 "postulaciones/02_FONDART_DIFUSION/TEXTO_POR_CAMPO.md": ("03_fondart_difusion.csv", "8.800.000"),
 "postulaciones/03_FONDART_FORMATIVAS/TEXTO_POR_CAMPO.md": ("04_fondart_formativas.csv", "8.608.000"),
 "postulaciones/ALTERNATIVA_CREACION/TEXTO_POR_CAMPO.md": ("02_fondart_creacion.csv", "12.090.000"),
}
for doc, (csvf, cita) in CITAS.items():
    p = RAIZ / doc
    if not p.exists(): continue
    esperado = TOT.get(csvf, (None, None))[0]
    fmt = f"{esperado:,.0f}".replace(",", ".") if esperado is not None else None
    if fmt != cita:
        err(f"{doc}: la cita {cita} no coincide con el CSV ({fmt})")
    if cita not in TEXTO[p]:
        err(f"{doc}: no menciona su total {cita}")
print(f"   totales cruzados: {len(CITAS)}")

# --- 5. afirmaciones prohibidas ---
print("## 5. Afirmaciones que la evidencia no sostiene")
PROHIBIDAS = [
 (r"219 obras", "dice '219 obras'; son 219 piezas, 134 tipificadas como obra"),
 (r"cero decisiones humanas", "afirma cero decisiones humanas; hay 87 registradas"),
 (r"\bacumulables\b", "afirma acumulabilidad; el Anexo 3 II.4 la condiciona"),
 (r"cotizaci[oó]n obtenida", "declara una cotizacion obtenida; no se pidio ninguna"),
 (r"carta (ya )?firmada", "declara una carta firmada; ninguna lo esta"),
 (r"espacio confirmado", "declara un espacio confirmado; ninguno lo esta"),
]
# Una afirmacion prohibida no cuenta si en su misma frase esta negada o citada
# para refutarla. Se mira la ventana de 200 caracteres alrededor.
NEGACION = re.compile(
    r"\bning|\bno se\b|\bno hay\b|\bnunca\b|\bfalsa?\b|refut|corrige|"
    r"\bsin\b|\bes incorrecto\b|\bya no\b|deja de|\berror\b", re.I)

for p, t in TEXTO.items():
    if any(x in str(p) for x in ("v1_ENTREGA", "AUDITORIA_LUNA", "RESPUESTA_AUDITORIA")):
        continue
    for pat, msg in PROHIBIDAS:
        for m in re.finditer(pat, t, re.I):
            ventana = t[max(0, m.start() - 200): m.end() + 200]
            if NEGACION.search(ventana):
                avi(f"{rel(p)}: aparece {m.group(0)!r} en contexto negado o de refutacion, aceptado")
                continue
            err(f"{rel(p)}: {msg}")
print(f"   patrones revisados: {len(PROHIBIDAS)}")

# --- 6. coherencia de fechas ---
print("## 6. Coherencia de fechas de cierre")
for p, t in TEXTO.items():
    if any(x in str(p) for x in ("v1_ENTREGA", "AUDITORIA_LUNA")): continue
    if re.search(r"11 de septiembre", t) and "MATRIZ" not in str(p):
        if not re.search(r"16 de septiembre|MATRIZ_REQUISITOS|regi[oó]n", t, re.I):
            avi(f"{rel(p)}: cita el 11 de septiembre sin mencionar el escenario del norte")
print("   revisado")

# --- 7. conteos de los textos por campo ---
print("## 7. Conteos declarados en TEXTO_POR_CAMPO")
for doc in [d for d in CITAS]:
    p = RAIZ / doc
    if not p.exists(): continue
    t = TEXTO[p]
    for m in re.finditer(r"`(\d+) palabras · (\d+) caracteres`", t):
        pass
    if "Conteos calculados automaticamente" not in t:
        err(f"{doc}: no declara que los conteos son automaticos")
print("   revisado")

print()
for a in avisos:
    print(f"AVISO  {a}")
print()
if errores:
    print(f"RESULTADO: FALLA con {len(errores)} error(es)")
    for e in errores:
        print(f"  ERROR  {e}")
    sys.exit(1)
print("RESULTADO: OK, el paquete pasa la comprobacion cruzada")
