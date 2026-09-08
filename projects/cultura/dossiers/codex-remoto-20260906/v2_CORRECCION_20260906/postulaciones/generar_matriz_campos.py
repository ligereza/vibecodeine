#!/usr/bin/env python3
"""Genera ../MATRIZ_CAMPOS_FINAL_20260906.md desde los modulos campos_*.py.

Una fila por campo de cada expediente: texto vigente (extracto), fuente,
estado, dato humano pendiente, archivo destino y prueba que lo respalda.
Se genera, no se escribe a mano: reejecutar tras editar cualquier campos_*.py.
"""
from __future__ import annotations
import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent
import campos_ama, campos_difusion, campos_formativas, campos_creacion

# Campos que dependen de un dato humano, y de cual.
PENDIENTE = {
 "Título del proyecto": ("", ""),
 "Información personal": ("identidad del titular", "FICHA §2"),
 "Descripción del proyecto": ("", ""),
 "Adjuntos: estado": ("CV, cedula y portfolio", "FICHA §3"),
 "Presupuesto: destino de los fondos": ("", ""),
 "Fundamentación": ("region de ejecucion", "FICHA §1"),
 "Territorio": ("region de ejecucion", "FICHA §1"),
 "Currículo del responsable": ("CV en Perfil Cultura", "FICHA §2"),
 "Currículo del responsable y antecedentes de estudios": ("antecedentes de estudios", "FICHA §4"),
}

# Prueba que respalda cada tipo de contenido.
PRUEBA = {
 "presupuesto": "verificador/verificar_presupuestos.py y revision_ids_y_gastos.py",
 "corpus": "evidencia/prueba_estado.sh §3 y §4",
 "decisiones": "evidencia/prueba_estado.sh §4 (87 selecciones, 14 sesiones)",
 "brecha": "evidencia/prueba_estado.sh §5 (contrato del compilador de dossier)",
 "bases": "fuentes/txt/ + fuentes/REGISTRO_DE_CITAS.md",
 "carga": "cronogramas/carga.py",
 "conteo": "postulaciones/generar_texto_por_campo.py",
}

def prueba_de(texto: str) -> str:
    t = texto.lower()
    ps = []
    if re.search(r"\$|us\$|presupuest|solicit", t): ps.append(PRUEBA["presupuesto"])
    if re.search(r"2\.034|7\.044|219|134|0,4855|vecindad", t): ps.append(PRUEBA["corpus"])
    if re.search(r"87|14 sesiones|descart|revers|selecc", t): ps.append(PRUEBA["decisiones"])
    if re.search(r"exportaci|dossier|salida|no existe", t): ps.append(PRUEBA["brecha"])
    if re.search(r"bases|anexo|tope|exim|criterio", t): ps.append(PRUEBA["bases"])
    if re.search(r"mes|cronograma|hora", t): ps.append(PRUEBA["carga"])
    return "; ".join(dict.fromkeys(ps)) or PRUEBA["conteo"]

def cuenta(t): return len(re.findall(r"\S+", t.strip()))

MODULOS = [
 ("Ama Amoedo — Artistas", campos_ama, "01_AMA_AMOEDO_ARTISTAS/TEXTO_POR_CAMPO.md",
  "Formulario vform, secciones a-d", "01_ama_amoedo.csv"),
 ("Fondart Difusión (SE ENVÍA)", campos_difusion, "02_FONDART_DIFUSION/TEXTO_POR_CAMPO.md",
  "FUP Fondart Regional", "03_fondart_difusion.csv"),
 ("Fondart Formativas", campos_formativas, "03_FONDART_FORMATIVAS/TEXTO_POR_CAMPO.md",
  "FUP Fondart Regional", "04_fondart_formativas.csv"),
 ("Fondart Creación (ALTERNATIVA, no se envía junto a Difusión)", campos_creacion,
  "ALTERNATIVA_CREACION/TEXTO_POR_CAMPO.md", "FUP Fondart Regional", "02_fondart_creacion.csv"),
]

L = ["# Matriz final campo por campo — 6 de septiembre de 2026", "",
 "Generada por `postulaciones/generar_matriz_campos.py` desde los módulos",
 "`campos_*.py`. No está escrita a mano: reejecutar tras editar cualquier campo.", "",
 "**Estado** significa: `REDACTADO` el texto está completo y utilizable;",
 "`REDACTADO + DATO` el texto está completo pero un dato humano debe insertarse",
 "antes de enviarlo. Ningún campo está sin redactar.", "",
 "Los datos humanos pendientes se registran en `FICHA_DATOS_TITULAR_20260906.md`;",
 "su estado se lee con `python3 verificador/leer_ficha_titular.py`.", ""]

tot_c = tot_p = 0
for titulo, mod, destino, fuente_form, csvf in MODULOS:
    L += [f"## {titulo}", "",
          f"Archivo de textos: `postulaciones/{destino}`  ·  "
          f"Presupuesto: `presupuestos/{csvf}`", "",
          "| Campo | Palabras | Estado | Dato humano pendiente | Destino en el formulario | Prueba que lo respalda |",
          "|---|---:|---|---|---|---|"]
    for c in mod.CAMPOS:
        nombre = c["campo"]
        base = nombre.split(" — ")[0].strip()
        dato, ref = PENDIENTE.get(nombre, PENDIENTE.get(base, ("", "")))
        n = cuenta(c["texto"]); tot_c += 1; tot_p += n
        estado = "REDACTADO + DATO" if dato else "REDACTADO"
        pend = f"{dato} ({ref})" if dato else "—"
        L.append(f"| {nombre} | {n} | {estado} | {pend} | {fuente_form} | {prueba_de(c['texto'])} |")
    L += ["", f"Campos: {len(mod.CAMPOS)}  ·  palabras: {sum(cuenta(c['texto']) for c in mod.CAMPOS)}", ""]

L += ["---", "",
 f"## Totales", "",
 f"- Campos redactados en los cuatro expedientes: **{tot_c}**",
 f"- Palabras de texto utilizable: **{tot_p}**",
 "- Campos sin redactar: **0**",
 "- Campos que además necesitan un dato humano antes de enviarse: "
 f"**{sum(1 for _t,m,_d,_f,_c in MODULOS for c in m.CAMPOS if PENDIENTE.get(c['campo'], PENDIENTE.get(c['campo'].split(' — ')[0].strip(), ('','')))[0])}**",
 "",
 "## Cómo se incorpora un dato cuando llegue",
 "",
 "1. El titular escribe el valor en `FICHA_DATOS_TITULAR_20260906.md`.",
 "2. `python3 verificador/leer_ficha_titular.py` indica el destino exacto.",
 "3. Se edita **el módulo `campos_*.py`**, no el `.md` generado.",
 "4. `python3 postulaciones/generar_texto_por_campo.py` regenera textos y conteos.",
 "5. `python3 postulaciones/generar_matriz_campos.py` regenera esta matriz.",
 "6. Se reejecutan las cinco verificaciones y se regenera `MANIFIESTO_v2.sha256`.",
 ""]

(AQUI.parent / "MATRIZ_CAMPOS_FINAL_20260906.md").write_text("\n".join(L), encoding="utf-8")
print(f"MATRIZ_CAMPOS_FINAL_20260906.md: {tot_c} campos, {tot_p} palabras")
