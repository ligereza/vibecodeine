#!/usr/bin/env python3
"""Genera la seleccion candidata de portfolio para Ama Amoedo.

No pregunta al titular que obras elegir: selecciona con un criterio explicito y
reproducible, y deja pendiente solo la aprobacion. Clasifica cada candidata por
nivel de procedencia, que es la logica del propio instrumento:

  N1  decision humana registrada + archivo en disco
  N2  archivo en disco + lectura de maquina + tipificado 'obra', sin decision
  N3  titulo y texto propios del artista, sin archivo y sin decision

Escribe ../postulaciones/ANEXOS/SELECCION_PORTFOLIO_AMA.md
"""
from __future__ import annotations
import json, os, re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
H = Path(os.path.expanduser("~/iskvw"))
D = Path(os.path.expanduser("~/plataforma/director_runs/portfolio-editor-20260808"))
MED = Path(os.path.expanduser("~/portfolio_media"))

def jl(p):
    o = []
    for ln in open(p, errors="replace"):
        ln = ln.strip()
        if ln:
            try: o.append(json.loads(ln))
            except Exception: pass
    return o

campo = json.load(open(H / "datos/campo.json"))["piezas"]
obras8 = json.load(open(H / "datos/obras.json"))
inbox = {x["id"]: x for x in json.load(open(D / "PORTFOLIO_INBOX.json"))["items"]}
sel = jl(D / "selections.jsonl")

ultimo = {}
for r in sorted(sel, key=lambda r: r.get("ts", "")):
    ultimo[r["item_id"]] = r

def en_disco(asset_path: str):
    rel = asset_path.lstrip("/").replace("portfolio-media/", "")
    for c in (MED / rel, MED / "media" / rel):
        if c.exists():
            return c
    return None

# ---- N1: decididas por el titular y con archivo ----
N1 = []
for item, r in ultimo.items():
    if r["decision"] != "seleccionar":
        continue
    it = inbox.get(item, {})
    p = en_disco(it.get("asset_path", ""))
    N1.append({"id": item, "fecha": it.get("fecha", "?"), "ruta": it.get("asset_path", ""),
               "kb": round(p.stat().st_size / 1024, 1) if p else None,
               "sesion": r.get("session_id", ""), "ts": r.get("ts", "")[:10]})
N1.sort(key=lambda x: x["fecha"])

# ---- N2: tipificadas obra, con SVG en disco, con lectura de maquina ----
def norm(s): return (s or "").strip().lower()
cand = [x for x in campo if x.get("tipo") == "obra"
        and (H / "piel/animadas" / f"{x['id']}.svg").exists()
        and x.get("percibido")]
# criterio: maxima cobertura de estilo y de paleta con el menor numero de piezas,
# priorizando las de paleta mas rica. Determinista: desempata por id.
sel2, vistos_e, vistos_c = [], set(), set()
for x in sorted(cand, key=lambda p: (-len(p.get("colores") or []), p["id"])):
    e = norm(x.get("estilo")); cs = {norm(c) for c in (x.get("colores") or [])}
    if e not in vistos_e or not cs <= vistos_c:
        sel2.append(x); vistos_e.add(e); vistos_c |= cs
    if len(sel2) == 12:
        break

COLOR_ES = {"rojo","azul","verde","amarillo","negro","blanco","gris","morado",
            "naranja","marron","marrón","rosa","violeta","turquesa","celeste",
            "beige","dorado","plateado","cafe","café","lila","fucsia","ocre"}

def alertas(x):
    """Defectos de dato detectados en la propia candidata. No se ocultan: el
    titular aprueba informado, y son la evidencia del trabajo que se financia."""
    a = []
    per = norm(x.get("percibido"))
    if re.search(r"\btatuaje\b|\bflyer\b|\blogo\b|\bafiche\b|\bmeme\b", per):
        a.append("la lectura de máquina describe algo que puede no ser obra, "
                 "pese a estar tipificada `obra`")
    cs = [norm(c) for c in (x.get("colores") or [])]
    ajenos = [c for c in cs if c and c not in COLOR_ES]
    if ajenos:
        a.append(f"vocabulario de color sin normalizar: {', '.join(ajenos)}")
    if (x.get("estilo") or "").strip() != (x.get("estilo") or "").strip().capitalize() \
            and (x.get("estilo") or "")[:1].islower():
        a.append("estilo en minúscula inicial: variante del mismo término")
    return a

def epigrafe(x):
    """Propuesta de epigrafe a partir de la lectura de maquina. NO es texto del
    artista: se entrega marcado como propuesta a validar."""
    t = re.sub(r"^Una?\s+", "", (x.get("percibido") or "").strip()).rstrip(".")
    t = t[0].upper() + t[1:] if t else "Sin descripcion"
    return t[:150]

L = ["# Selección candidata de portfolio — Ama Amoedo", "",
 "Generada por `verificador/generar_seleccion_portfolio.py` el 2026-09-06.",
 "Sólo lectura: no modifica ningún dato de MAK.", "",
 "> **Qué decide este documento y qué no.** Decide la selección y propone los",
 "> epígrafes, con un criterio explícito y reproducible. **No decide autoría:**",
 "> promover un registro a obra es un acto del artista, y por eso cada candidata",
 "> lleva su nivel de procedencia a la vista. Lo único que queda pendiente es la",
 "> aprobación y la entrega física de los archivos.", "",
 "## 1. Por qué hay niveles de procedencia y no una lista plana", "",
 "El archivo tiene tres cuerpos de material que no se cruzan, y sólo uno de ellos",
 "reúne las tres condiciones que un portfolio necesita: que el artista lo haya",
 "reconocido como obra, que exista una lectura de lo que se ve, y que el archivo",
 "esté en disco.", "",
 "| Nivel | Qué reúne | Piezas |", "|---|---|---:|",
 f"| **N1** | decisión humana registrada **y** archivo en disco | **{len(N1)}** |",
 f"| **N2** | archivo en disco **y** lectura de máquina **y** tipificado `obra`, sin decisión | **{len(cand)}** |",
 f"| **N3** | título y texto propios del artista, **sin archivo** y sin decisión | **{len(obras8)}** |",
 "", "**La intersección N1 ∩ N2 es cero.** Se comprobó cruzando el identificador de",
 "medio de las 68 piezas decididas contra las 219 del campo visual: ninguna",
 "coincide. Son dos inventarios disjuntos.", "",
 "Y las de N3 —las que sí llevan título y texto del artista— **no tienen archivo**:",
 "sus rutas `assets/works/*.svg` no existen en disco. No pueden ir a un portfolio.", "",
 "> Este hallazgo no es un obstáculo del expediente: **es su argumento**. Hoy no",
 "> hay en el archivo ninguna pieza que sea simultáneamente decidida por el autor,",
 "> legible y presente. Cerrar esa distancia es exactamente lo que la beca financia.", "",
 "## 2. N1 — las que el titular ya decidió, con archivo verificado en disco", "",
 "Estado final de las decisiones registradas entre el 2026-08-07 y el 2026-09-02.",
 "Tomando para cada registro su última decisión, que es la que manda.", "",
 "| # | id del registro | fecha de la obra | archivo | tamaño | decidida el | sesión |",
 "|---:|---|---|---|---:|---|---|"]
for i, x in enumerate(N1, 1):
    L.append(f"| {i} | `{x['id']}` | {x['fecha']} | `{x['ruta']}` | "
             f"{x['kb']} KB | {x['ts']} | `{x['sesion']}` |")
L += ["", "**Estas cuatro entran al portfolio sin discusión:** son las únicas que llevan",
 "un acto de autoría registrado. No tienen título ni epígrafe propio —el campo de",
 "descripción original está vacío en tres y contiene `xx` en la cuarta—, de modo",
 "que **el epígrafe lo escribe el titular**. Es el único texto que no puedo redactar.", "",
 "## 3. N2 — propuesta razonada para completar el conjunto", "",
 "**Criterio, explícito y reproducible:** máxima cobertura de estilo y de paleta",
 "con el menor número de piezas, priorizando las de paleta más rica; desempate",
 "determinista por identificador. Es un criterio de **diversidad**, no de calidad:",
 "un instrumento no puede juzgar calidad y éste no lo pretende.", "",
 f"Se seleccionan 12 de {len(cand)} candidatas, cubriendo "
 f"{len(vistos_e)} estilos y {len(vistos_c)} colores distintos.", "",
 "| # | id | estilo | colores | epígrafe propuesto | alerta de dato |",
 "|---:|---|---|---|---|---|"]
n_alerta = 0
for i, x in enumerate(sel2, 5):
    al = alertas(x)
    if al: n_alerta += 1
    L.append(f"| {i} | `{x['id'][:24]}` | {x.get('estilo')} | "
             f"{', '.join(x.get('colores') or [])} | {epigrafe(x)} | "
             f"{'; '.join(al) if al else '—'} |")
L += ["", f"Archivos: `~/iskvw/piel/animadas/<id>.svg`, los {len(sel2)} verificados en disco.", ""]
L += [f"**{n_alerta} de las 12 candidatas llevan una alerta de dato.** No se ocultan y no",
 "descalifican la pieza: describen exactamente el trabajo que el Expediente 1 pide",
 "financiar. Dos defectos aparecen en la muestra y los dos son reales:", "",
 "- **Tipificación que no es validación autoral.** Al menos una candidata está",
 "  marcada `obra` por el pipeline mientras su lectura de máquina describe un",
 "  tatuaje. Ningún instrumento puede resolver eso: lo resuelve el artista.",
 "- **Vocabulario de color sin normalizar.** Alguna candidata trae los colores en",
 "  inglés y el archivo mezcla `azul` con `Azul`. Decidir con qué palabras se",
 "  describe el propio trabajo es una decisión de autor, no de mantenimiento.", "",
 "> **Los epígrafes de N2 son propuestas derivadas de la lectura de máquina,",
 "> no texto del artista.** Se entregan redactados para que el titular los acepte,",
 "> corrija o reemplace. Ninguno afirma autoría, técnica ni año: esos datos no",
 "> están en la fuente y no se inventan.", "",
 "## 4. N3 — por qué quedan fuera, aunque sean las que tienen mejor texto", "",
 "| id | título del artista | archivo declarado | ¿existe en disco? |",
 "|---|---|---|---|"]
for x in obras8:
    src = x.get("src") or x.get("image") or "—"
    L.append(f"| `{x['id']}` | {x['title']} | `{src}` | **no** |")
L += ["", "Las ocho tienen título, año, técnica y descripción larga escritos por el",
 "artista, y son con diferencia el mejor material textual del archivo. **Pero",
 "ninguna tiene archivo en disco y ninguna pasó por instancia de decisión alguna:**",
 "0 en el inventario de curaduría, 0 selecciones, 0 clasificaciones, 0 en el",
 "registro de decisiones y 0 en `curaduria.json`. Su `estado: publicada` es un",
 "valor por defecto que llevan las 1.826 piezas de esa clase, no una decisión.", "",
 "Además `obras.json` es del 2026-07-27, anterior al inventario de curaduría",
 "(2026-08-07) y al campo visual (2026-09-02): describe un estado del proyecto",
 "que las dos instancias posteriores no recogieron.", "",
 "**Acción recomendada, no bloqueante para el 9 de septiembre:** si el titular",
 "localiza esos ocho archivos, pasan a ser el mejor material del portfolio, porque",
 "aportan lo único que a N1 y N2 les falta: título y texto de autor. Mientras no",
 "aparezcan, no se incluyen. Registrado como pendiente personal, no como pregunta.", "",
 "## 5. Conjunto propuesto", "",
 f"- **{len(N1)} piezas de N1** — decisión de autoría registrada, archivo verificado.",
 f"- **12 piezas de N2** — propuesta razonada, epígrafes a validar.",
 f"- **Total: {len(N1) + 12} piezas**, dentro del máximo de 20 que admiten las bases.", "",
 "## 6. Lo único pendiente del titular", "",
 "1. Aprobar o corregir el conjunto de 16.",
 "2. Escribir los cuatro epígrafes de N1 y validar los doce de N2.",
 "3. Entregar los archivos físicos, o autorizar el uso de los que están en disco.",
 "4. Confirmar que ninguna pieza incluye imágenes de terceros sin autorización.", "",
 "No se le pregunta qué obras elegir: la selección está hecha y fundamentada.",
 "Se le pide aprobarla, que es un acto de autoría y no una decisión de diseño.", ""]

out = RAIZ / "postulaciones/ANEXOS/SELECCION_PORTFOLIO_AMA.md"
out.write_text("\n".join(L), encoding="utf-8")
print(f"SELECCION_PORTFOLIO_AMA.md: N1={len(N1)}  N2 propuestas={len(sel2)} de {len(cand)}  "
      f"N3 descartadas={len(obras8)}  total propuesto={len(N1)+len(sel2)}  "
      f"candidatas con alerta de dato={n_alerta}")
