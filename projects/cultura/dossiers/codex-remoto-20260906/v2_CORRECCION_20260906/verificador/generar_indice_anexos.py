#!/usr/bin/env python3
"""Genera ../INDICE_ANEXOS_20260906.md con datos reales de cada archivo.

Estado de cada anexo:
  LISTO      existe en el paquete y es utilizable tal cual
  BORRADOR   existe pero requiere firma, decision o dato del titular
  FALTANTE   no existe y hace falta para postular o para evaluar
  POSTERIOR  no se necesita para postular; se exige despues (convenio o pago)
"""
from __future__ import annotations
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# (expediente, anexo, ruta relativa o None, extension destino, campo que alimenta,
#  gravedad, estado)
FILAS = [
 # --- Ama Amoedo ---
 ("Ama", "Presupuesto desglosado", "presupuestos/01_ama_amoedo.csv", "xlsx o pdf",
  "c) Presupuesto", "requisito al postular", "LISTO"),
 ("Ama", "Ficha tecnica del instrumento", "postulaciones/ANEXOS/FICHA_TECNICA_IRIS.md", "pdf",
  "d) Anexo del proyecto (optativo)", "optativo", "LISTO"),
 ("Ama", "Salida fechada de la prueba de estado", "evidencia/SALIDA_PRUEBA_ESTADO.txt", "pdf o txt",
  "d) Anexo del proyecto (optativo)", "optativo", "LISTO"),
 ("Ama", "Guion de demostracion y capturas", "postulaciones/ANEXOS/GUION_DEMO.md", "pdf",
  "d) Anexo del proyecto (optativo)", "optativo", "LISTO"),
 ("Ama", "Indice de seleccion candidata", "postulaciones/BORRADORES_SIN_FIRMA/BORRADOR_INDICE_PORTFOLIO.md", "trabajo interno",
  "insumo del portfolio", "insumo", "BORRADOR"),
 ("Ama", "Portfolio artistico, 5 a 20 imagenes con epigrafe", None, "pdf",
  "d) Portfolio", "requisito al postular", "FALTANTE"),
 ("Ama", "Curriculum vitae", None, "pdf",
  "d) CV", "requisito al postular", "FALTANTE"),
 ("Ama", "Documento de identidad", None, "pdf o jpg",
  "a) Informacion personal", "requisito al postular", "FALTANTE"),
 ("Ama", "Cuenta bancaria a nombre del titular", None, "dato",
  "no va en el formulario", "requisito de pago", "POSTERIOR"),
 # --- Difusion ---
 ("Difusion", "Plan y Fundamentacion de la Estrategia de Difusion",
  "postulaciones/02_FONDART_DIFUSION/TEXTO_POR_CAMPO.md", "pdf",
  "anexo de evaluacion", "evaluacion", "LISTO"),
 ("Difusion", "Estrategia de Publicos y Acceso",
  "postulaciones/02_FONDART_DIFUSION/TEXTO_POR_CAMPO.md", "pdf",
  "anexo de evaluacion", "evaluacion", "LISTO"),
 ("Difusion", "Presupuesto desglosado", "presupuestos/03_fondart_difusion.csv", "en el FUP",
  "presupuesto del FUP", "requisito al postular", "LISTO"),
 ("Difusion", "Cronograma de ejecucion", "cronogramas/EJECUCION_2027.md", "en el FUP",
  "cronograma del FUP", "requisito al postular", "LISTO"),
 ("Difusion", "Compromiso de exhibicion o difusion", None, "no aplica",
  "anexo de evaluacion", "eximido por las bases", "POSTERIOR"),
 ("Difusion", "Cartas de compromiso del equipo", None, "no aplica",
  "documento minimo", "no corresponde: sin equipo declarado", "POSTERIOR"),
 ("Difusion", "Perfil Cultura vigente", None, "inscripcion",
  "acceso al FUP", "requisito al postular", "FALTANTE"),
 ("Difusion", "Cedula de identidad y domicilio <=180 dias", None, "pdf",
  "no va en la postulacion", "requisito de convenio", "POSTERIOR"),
 ("Difusion", "Garantia por el monto total", None, "letra de cambio ante notario",
  "no va en la postulacion", "requisito de convenio", "POSTERIOR"),
 # --- Formativas ---
 ("Formativas", "Programa de la Formacion",
  "postulaciones/03_FONDART_FORMATIVAS/TEXTO_POR_CAMPO.md", "pdf",
  "anexo de evaluacion", "evaluacion", "LISTO"),
 ("Formativas", "Diagnostico de Necesidad Formativa",
  "postulaciones/03_FONDART_FORMATIVAS/TEXTO_POR_CAMPO.md", "pdf",
  "anexo de evaluacion", "evaluacion", "LISTO"),
 ("Formativas", "Estrategias de Transferencia de Aprendizajes",
  "postulaciones/03_FONDART_FORMATIVAS/TEXTO_POR_CAMPO.md", "pdf",
  "anexo de evaluacion", "evaluacion", "LISTO"),
 ("Formativas", "Presupuesto desglosado", "presupuestos/04_fondart_formativas.csv", "en el FUP",
  "presupuesto del FUP", "requisito al postular", "LISTO"),
 ("Formativas", "Planilla de compromisos de asistencia, 15 filas",
  "postulaciones/BORRADORES_SIN_FIRMA/FORMATO_COMPROMISOS_FORMativas_15_FILAS.csv", "pdf firmado",
  "anexo de evaluacion", "evaluacion", "BORRADOR"),
 ("Formativas", "Instrucciones de la planilla de compromisos",
  "postulaciones/BORRADORES_SIN_FIRMA/FORMATO_COMPROMISOS_FORMativas_15_FILAS_LEEME.md", "trabajo interno",
  "insumo", "insumo", "LISTO"),
 ("Formativas", "Solicitud de espacio: cotizacion o carta",
  "postulaciones/BORRADORES_SIN_FIRMA/SOLICITUD_ESPACIO_COTIZACION.md", "correo o pdf",
  "anexo de evaluacion", "evaluacion", "BORRADOR"),
 ("Formativas", "Antecedentes de estudios formales y no formales", None, "pdf",
  "anexo de evaluacion", "evaluacion", "FALTANTE"),
 ("Formativas", "Cartas de compromiso del equipo", None, "no aplica",
  "documento minimo", "no corresponde: sin equipo declarado", "POSTERIOR"),
 # --- Creacion alternativa ---
 ("Creacion", "Propuesta creativa",
  "postulaciones/ALTERNATIVA_CREACION/TEXTO_POR_CAMPO.md", "pdf",
  "anexo de evaluacion", "evaluacion", "LISTO"),
 ("Creacion", "Estrategias de difusion de la obra",
  "postulaciones/ALTERNATIVA_CREACION/TEXTO_POR_CAMPO.md", "pdf",
  "anexo de evaluacion", "evaluacion", "LISTO"),
 ("Creacion", "Presupuesto desglosado", "presupuestos/02_fondart_creacion.csv", "en el FUP",
  "presupuesto del FUP", "requisito al postular", "LISTO"),
 ("Creacion", "Compromiso o cotizacion del espacio anfitrion",
  "postulaciones/BORRADORES_SIN_FIRMA/SOLICITUD_ESPACIO_COTIZACION.md", "correo o pdf",
  "anexo de evaluacion", "evaluacion", "BORRADOR"),
 ("Creacion", "Confirmacion de no haber sido seleccionado en Creacion 2026", None, "declaracion en el FUP",
  "restriccion de la linea", "requisito al postular", "FALTANTE"),
 # --- Comunes ---
 ("Ama", "Seleccion candidata de portfolio por nivel de procedencia",
  "postulaciones/ANEXOS/SELECCION_PORTFOLIO_AMA.md", "trabajo interno",
  "insumo del portfolio", "insumo", "LISTO"),
 ("Comun", "Modelo de autorizacion de uso de imagen",
  "postulaciones/BORRADORES_SIN_FIRMA/MODELO_AUTORIZACION_USO_DE_IMAGEN.md", "pdf firmado",
  "solo si se incluyen personas identificables", "no corresponde en esta variante", "POSTERIOR"),
 ("Comun", "Modelo de carta de compromiso de equipo",
  "postulaciones/BORRADORES_SIN_FIRMA/MODELO_CARTA_COMPROMISO_EQUIPO.md", "pdf firmado",
  "solo si se declara equipo", "no corresponde en esta variante", "POSTERIOR"),
 ("Comun", "Matriz de coherencia de los cuatro expedientes",
  "MATRIZ_COHERENCIA_20260906.md", "trabajo interno",
  "control de calidad", "insumo", "LISTO"),
 ("Comun", "Registro de fuentes y citas", "../fuentes/REGISTRO_DE_CITAS.md", "trabajo interno",
  "respaldo de cada requisito", "insumo", "LISTO"),
 ("Comun", "Matriz comparativa de convocatorias", "../fuentes/MATRIZ_COMPARATIVA.csv", "trabajo interno",
  "respaldo normativo", "insumo", "LISTO"),
 ("Comun", "Estado tecnico verificado", "evidencia/ESTADO_TECNICO_VERIFICADO.md", "pdf",
  "respaldo de claims tecnicos", "insumo", "LISTO"),
 ("Comun", "Bases y resoluciones oficiales sin editar", "../fuentes/pdf", "pdf",
  "respaldo normativo", "insumo", "LISTO"),
 ("Comun", "Manifiesto de integridad del paquete", "MANIFIESTO_v2.sha256", "trabajo interno",
  "trazabilidad de version", "insumo", "LISTO"),
]

def info(rel):
    if rel is None:
        return ("—", "—", "no existe")
    p = RAIZ / rel
    if not p.exists():
        return ("—", "—", "**RUTA NO ENCONTRADA**")
    if p.is_dir():
        arch = sorted(x for x in p.iterdir() if x.is_file())
        kb = sum(x.stat().st_size for x in arch) / 1024
        return (f"{len(arch)} archivos", f"{kb:,.1f} KB", f"`{rel}/`")
    kb = p.stat().st_size / 1024
    return (p.suffix.lstrip(".") or "sin ext", f"{kb:,.1f} KB", f"`{rel}`")

L = ["# Indice demostrable de anexos — 6 de septiembre de 2026", "",
 "Generado por `verificador/generar_indice_anexos.py`, que lee el tamano y la",
 "extension reales de cada archivo. Una ruta marcada **RUTA NO ENCONTRADA** es un",
 "error del indice, no del paquete.", "",
 "| Estado | Significado |", "|---|---|",
 "| `LISTO` | Existe en el paquete y es utilizable tal cual |",
 "| `BORRADOR` | Existe, pero requiere firma, decision o dato del titular |",
 "| `FALTANTE` | No existe y hace falta para postular o para evaluar |",
 "| `POSTERIOR` | No se necesita para postular: se exige despues, o esta eximido |", ""]

orden = ["Ama", "Difusion", "Formativas", "Creacion", "Comun"]
nombres = {"Ama": "Ama Amoedo 2026 — Artistas",
           "Difusion": "Fondart Difusion 2027 — SE ENVIA",
           "Formativas": "Fondart Actividades Formativas 2027",
           "Creacion": "Fondart Creacion 2027 — ALTERNATIVA de Difusion",
           "Comun": "Transversales a los cuatro expedientes"}
errores = 0
conteo = {}
for exp in orden:
    L += [f"## {nombres[exp]}", "",
          "| Anexo | Estado | Gravedad | Archivo en el paquete | Ext. | Tamano | Formato de entrega | Campo que alimenta |",
          "|---|---|---|---|---|---|---|---|"]
    for e, anexo, rel, fmt, campo, grav, est in FILAS:
        if e != exp:
            continue
        ext, kb, ruta = info(rel)
        if "NO ENCONTRADA" in ruta:
            errores += 1
        conteo[est] = conteo.get(est, 0) + 1
        L.append(f"| {anexo} | **{est}** | {grav} | {ruta} | {ext} | {kb} | {fmt} | {campo} |")
    L.append("")

L += ["---", "", "## Recuento", "",
      "| Estado | Anexos |", "|---|---:|"]
for k in ("LISTO", "BORRADOR", "FALTANTE", "POSTERIOR"):
    L.append(f"| `{k}` | {conteo.get(k, 0)} |")
L += [f"| **total** | **{sum(conteo.values())}** |", "",
 "## Los FALTANTE, uno por uno", "",
 "| Anexo | Expediente | Quien lo produce | Bloquea |", "|---|---|---|---|",
 "| Portfolio artistico | Ama | el titular decide y arma | **si**, requisito al postular |",
 "| Curriculum vitae | Ama | el titular | **si**, requisito al postular |",
 "| Documento de identidad | Ama | el titular | **si**, requisito al postular |",
 "| Perfil Cultura vigente | los tres Fondart | el titular en la plataforma | **si**, sin el no hay FUP |",
 "| Antecedentes de estudios | Formativas | el titular | no: baja Curriculo (20%) |",
 "| Confirmacion Creacion 2026 | Creacion | el titular verifica | **si**, seria causal de exclusion |",
 "",
 "## Los BORRADOR, uno por uno", "",
 "| Anexo | Que le falta | Bloquea |", "|---|---|---|",
 "| Planilla de 15 compromisos | 15 firmas de terceros | no: baja Viabilidad (10%) |",
 "| Solicitud de espacio | enviarla y recibir carta o cotizacion | no: baja Viabilidad (10%) |",
 "| Indice de seleccion candidata | decision del titular sobre las piezas | es insumo del portfolio |",
 "",
 "## Nota sobre los tres anexos de evaluacion de cada Fondart", "",
 "Estan **dentro** del archivo `TEXTO_POR_CAMPO.md` de su expediente, como",
 "secciones. Para adjuntarlos hay que exportar cada seccion como PDF por separado.",
 "Las versiones limpias, sin tablas ni notas internas, estan en `PARA_COPIAR/`.", ""]

(RAIZ / "INDICE_ANEXOS_20260906.md").write_text("\n".join(L), encoding="utf-8")
print(f"INDICE_ANEXOS_20260906.md: {sum(conteo.values())} anexos, "
      f"{conteo.get('LISTO',0)} LISTO, {conteo.get('BORRADOR',0)} BORRADOR, "
      f"{conteo.get('FALTANTE',0)} FALTANTE, {conteo.get('POSTERIOR',0)} POSTERIOR")
if errores:
    print(f"ERROR: {errores} ruta(s) no encontrada(s)")
    raise SystemExit(1)
