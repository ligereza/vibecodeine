#!/usr/bin/env python3
"""
algebra.py — ¿Los vectores del SVG se relacionan con los vectores semánticos?

Prueba empírica. Un spec del motor NO es una lista de opciones: es exactamente
la estructura que las Vector Symbolic Architectures llaman ROLE-FILLER BINDING
más SUPERPOSICIÓN.

    spec = SUMA (rol * figura * gesto)      <- binding + bundling

Eso significa que sobre los specs se puede hacer ÁLGEBRA: analogías,
interpolación, sustitución de roles. Y como el compilador es una función
determinista spec->SVG, esa álgebra semántica se convierte en geometría.

Ejecuta:  python3 motor/algebra.py
"""
import copy, sys, pathlib

if __name__ == "__main__" and __package__ in (None, ""):
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    __package__ = "motor_semantico"


# -- 1. El spec ES una estructura role-filler ----------------------------
def como_bindings(spec):
    """Muestra el spec en notación VSA: rol * relleno."""
    out = []
    for capa in spec["capas"]:
        rol = capa["rol"]
        piezas = [f"figura:{capa['figura']}"] if capa.get("figura") else [f"texto:'{capa['texto']}'"]
        if capa.get("gesto", "quieto") != "quieto":
            piezas.append(f"gesto:{capa['gesto']}")
        out.append(f"({rol} * {' * '.join(piezas)})")
    return "  +  ".join(out)


# -- 2. Operaciones algebraicas sobre specs ------------------------------
def sustituir(spec, viejo, nuevo, campo="figura"):
    """Analogía: reemplaza un filler manteniendo la estructura de roles."""
    s = copy.deepcopy(spec)
    for capa in s["capas"]:
        if capa.get(campo) == viejo:
            capa[campo] = nuevo
    return s


def transferir_estilo(contenido, estilo):
    """spec_A(qué) + spec_B(cómo) -> el contenido de A con el tono/ritmo de B.
    Equivale a unbind del rol 'tono' en A y bind del de B."""
    s = copy.deepcopy(contenido)
    s["tono"] = estilo["tono"]
    ritmos = [c.get("ritmo", "medio") for c in estilo["capas"] if c.get("ritmo")]
    if ritmos:
        for capa in s["capas"]:
            if capa.get("gesto", "quieto") != "quieto":
                capa["ritmo"] = ritmos[0]
    return s


def interpolar(a, b, t):
    """Camino discreto entre dos conceptos. t=0 -> a ; t=1 -> b.
    No hay 'medio disco' — el espacio es discreto — pero sí hay
    una secuencia de pasos mínimos, que es la versión simbólica
    de recorrer una geodésica en un espacio latente."""
    s = copy.deepcopy(a)
    cambios = []
    if a["tono"] != b["tono"]:
        cambios.append(("tono", None, b["tono"]))
    for i, (ca, cb) in enumerate(zip(a["capas"], b["capas"])):
        if ca.get("figura") and cb.get("figura") and ca["figura"] != cb["figura"]:
            cambios.append(("figura", i, cb["figura"]))
        if ca.get("gesto") != cb.get("gesto"):
            cambios.append(("gesto", i, cb.get("gesto", "quieto")))
    n = round(t * len(cambios))
    for campo, idx, val in cambios[:n]:
        if idx is None:
            s[campo] = val
        else:
            s["capas"][idx][campo] = val
    return s


# -- 3. Distancia semántica entre specs ----------------------------------
def distancia(a, b):
    """Cuántas ediciones semánticas separan dos íconos.
    Es una métrica REAL sobre el espacio de conceptos, no sobre píxeles."""
    d = 0
    d += a["composicion"] != b["composicion"]
    d += a["tono"] != b["tono"]
    ca, cb = a["capas"], b["capas"]
    d += abs(len(ca) - len(cb))
    for x, y in zip(ca, cb):
        d += x.get("figura") != y.get("figura")
        d += x.get("gesto", "quieto") != y.get("gesto", "quieto")
    return d


# -- demo ----------------------------------------------------------------
BERLIN = {"slug": "berlin", "composicion": "confrontacion", "tono": "concreto",
          "capas": [{"rol": "lado_izq", "figura": "muro", "gesto": "desplazar_fuera", "ritmo": "lento"},
                    {"rol": "lado_der", "figura": "muro", "gesto": "desplazar_fuera", "ritmo": "lento"},
                    {"rol": "protagonista", "figura": "onda", "gesto": "emanar", "ritmo": "rapido"}]}

TAZ = {"slug": "taz", "composicion": "capas", "tono": "papel",
       "capas": [{"rol": "fondo_amplio", "figura": "grilla", "gesto": "quieto"},
                 {"rol": "protagonista", "figura": "anillo", "gesto": "aparecer_ciclico", "ritmo": "lento"},
                 {"rol": "detalle", "figura": "estrella", "gesto": "aparecer_ciclico", "ritmo": "lento"}]}

ACID = {"slug": "acid", "composicion": "capas", "tono": "atardecer",
        "capas": [{"rol": "fondo_amplio", "figura": "espiral", "gesto": "girar", "ritmo": "muy_lento"},
                  {"rol": "protagonista", "figura": "ojo", "gesto": "latir", "ritmo": "lento"},
                  {"rol": "detalle", "figura": "estrella", "gesto": "respirar", "ritmo": "medio"}]}

if __name__ == "__main__":
    print("=" * 68)
    print("1. UN SPEC ES UNA ESTRUCTURA ROLE-FILLER (notación VSA)")
    print("=" * 68)
    print("BERLÍN =", como_bindings(BERLIN))
    print()
    print("TAZ    =", como_bindings(TAZ))

    print("\n" + "=" * 68)
    print("2. ANALOGÍA — sustituir un filler preservando los roles")
    print("=" * 68)
    print("BERLÍN es 'muro que se parte y emite'.")
    print("¿Qué es lo mismo pero con vigilancia en vez de hormigón?")
    v = sustituir(BERLIN, "muro", "grilla")
    print("  BERLÍN - muro + grilla =", como_bindings(v))

    print("\n" + "=" * 68)
    print("3. TRANSFERENCIA DE ESTILO — unbind/bind del rol 'tono'")
    print("=" * 68)
    t = transferir_estilo(TAZ, ACID)
    print(f"  contenido(TAZ) * estilo(ACID) -> tono '{TAZ['tono']}' -> '{t['tono']}'")

    print("\n" + "=" * 68)
    print("4. INTERPOLACIÓN — camino mínimo entre dos conceptos")
    print("=" * 68)
    for t_ in (0, .34, .67, 1):
        s = interpolar(TAZ, ACID, t_)
        figs = [c.get("figura") for c in s["capas"]]
        print(f"  t={t_:<5} tono={s['tono']:<10} figuras={figs}")

    print("\n" + "=" * 68)
    print("5. DISTANCIA SEMÁNTICA — métrica sobre conceptos, no píxeles")
    print("=" * 68)
    pares = [("BERLÍN", BERLIN, "TAZ", TAZ), ("TAZ", TAZ, "ACID", ACID),
             ("BERLÍN", BERLIN, "ACID", ACID)]
    for na, a, nb, b in pares:
        print(f"  d({na:<7}, {nb:<6}) = {distancia(a, b)}")
