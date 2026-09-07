#!/usr/bin/env python3
"""Lee FICHA_DATOS_TITULAR_20260906.md y dice exactamente que falta.

No inventa nada. Reporta, por campo: si esta completo, que archivo destino
desbloquea y que expedientes quedan bloqueados mientras siga vacio.

Salida 0 siempre: informar no es fallar. Uso:
    python3 verificador/leer_ficha_titular.py [--json]
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FICHA = RAIZ / "FICHA_DATOS_TITULAR_20260906.md"

VACIO = re.compile(r"\[\s*(COMPLETAR|S[ÍI]/NO(?:/PENDIENTE)?|URL o identificador|"
                   r"VIGENTE / PENDIENTE / REVISAR|S[ÍI]/NO \+ explicar|"
                   r"nombre exacto del archivo(?: o PENDIENTE)?|"
                   r"DIFUSI[ÓO]N / CREACI[ÓO]N|CREACI[ÓO]N / DIFUSI[ÓO]N|"
                   r"COMPLETAR o PENDIENTE|\s*)\]", re.I)

# campo -> (destinos, expedientes bloqueados)
MAPA = {
 "Región de domicilio":      (["MATRIZ_REQUISITOS.md §4", "los tres FUP Fondart"], ["Difusion","Formativas","Creacion"]),
 "Comuna de domicilio":      (["campos territoriales del FUP"], ["Difusion","Formativas","Creacion"]),
 "Región/comuna donde se ejecutará": (["campos territoriales del FUP"], ["Difusion","Formativas","Creacion"]),
 "Nombre legal completo":    (["identificacion del FUP", "formulario Ama"], ["Ama","Difusion","Formativas","Creacion"]),
 "RUT":                      (["identificacion del FUP", "formulario Ama"], ["Ama","Difusion","Formativas","Creacion"]),
 "Fecha de nacimiento":      (["formulario Ama, seccion a"], ["Ama"]),
 "Domicilio":                (["identificacion del FUP"], ["Difusion","Formativas","Creacion"]),
 "Correo":                   (["contacto del FUP y del formulario"], ["Ama","Difusion","Formativas","Creacion"]),
 "Teléfono":                 (["contacto del FUP y del formulario"], []),
 "Perfil Cultura":           (["plataforma fondosdecultura"], ["Difusion","Formativas","Creacion"]),
 "Usuario o correo usado":   (["portal vform de Ama Amoedo"], ["Ama"]),
 "Estado de Perfil Cultura": (["plataforma fondosdecultura"], ["Difusion","Formativas","Creacion"]),
 "Cuenta creada en el portal": (["portal vform de Ama Amoedo"], ["Ama"]),
 "CV disponible":            (["adjunto d) del formulario Ama"], ["Ama"]),
 "Documento de identidad disponible": (["adjunto a) del formulario Ama"], ["Ama"]),
 "¿Se mantiene la postulación Formativas?": (["decision de alcance del paquete"], ["Formativas"]),
 "Antecedentes de estudios": (["adjunto de evaluacion de Formativas"], []),
 "Espacio tentativo":        (["adjunto de evaluacion", "presupuesto O-FOR-01"], []),
 "¿Se pueden conseguir 15 compromisos": (["adjunto de evaluacion de Formativas"], []),
 "Línea que se enviará":     (["define Difusion o Creacion"], ["Difusion","Creacion"]),
}

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if not FICHA.exists():
        print(f"NO EXISTE {FICHA}"); return 0
    texto = FICHA.read_text(encoding="utf-8")

    completos, pendientes = [], []
    for linea in texto.splitlines():
        m = re.match(r"^-\s+([^:]{3,60}):\s*(.+)$", linea.strip())
        if not m:
            continue
        campo, valor = m.group(1).strip(), m.group(2).strip()
        candidatos = [k for k in MAPA if k.lower() in campo.lower()]
        clave = max(candidatos, key=len) if candidatos else None
        vacio = bool(VACIO.fullmatch(valor)) or valor in ("`[ ]`", "[ ]")
        vacio = vacio or bool(VACIO.search(valor))
        (pendientes if vacio else completos).append((campo, valor, clave))

    # tabla de portfolio
    filas_pf = re.findall(r"^\|\s*(\d+)\s*\|(.+)\|\s*$", texto, re.M)
    pf_completas = [n for n, resto in filas_pf
                    if not VACIO.search(resto) and "[ ]" not in resto]

    print("# Estado de FICHA_DATOS_TITULAR_20260906.md")
    print(f"\ncampos completados: {len(completos)}   pendientes: {len(pendientes)}")
    print(f"filas de portfolio con datos: {len(pf_completas)} de {len(filas_pf)}")

    if completos:
        print("\n## Campos COMPLETADOS por el titular -> incorporar a estos destinos\n")
        for campo, valor, clave in completos:
            dest = ", ".join(MAPA[clave][0]) if clave else "sin destino mapeado"
            print(f"- **{campo}** = {valor}\n    destino: {dest}")
    else:
        print("\n## Campos COMPLETADOS: ninguno")
        print("\nNo hay ningun dato que incorporar. No se inventa ninguno.")

    print("\n## Campos PENDIENTES y que bloquean\n")
    bloq = {}
    for campo, valor, clave in pendientes:
        exps = MAPA[clave][1] if clave else []
        for e in exps:
            bloq.setdefault(e, []).append(campo)
        marca = ", ".join(exps) if exps else "no bloquea el envio"
        print(f"- {campo}  ->  {marca}")

    print("\n## Bloqueos por expediente\n")
    for e in ["Ama", "Difusion", "Formativas", "Creacion"]:
        n = len(bloq.get(e, []))
        print(f"- **{e}**: {n} campo(s) pendiente(s)" +
              (f" — {', '.join(bloq[e][:4])}{'…' if n > 4 else ''}" if n else ""))

    if a.json:
        print("\n" + json.dumps({"completos": [c[0] for c in completos],
                                 "pendientes": [c[0] for c in pendientes],
                                 "portfolio_filas_con_datos": len(pf_completas),
                                 "bloqueos": bloq}, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
