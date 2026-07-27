#!/usr/bin/env python3
"""Las obras del archivo, con posiciones que SON distancia medida.

El defecto que esto corrige estaba declarado dentro de la propia piel: las
posiciones salian de un hash del identificador. Estables, pero no significan
nada -- y el que mira lee la cercania como si significara. El
`doublecup/svg/README.md` ya habia escrito esa misma advertencia sobre su
pieza:

    "las posiciones de nodo se reparten por rango en cada eje: la cercania
     entre nodos no es distancia semantica y el espectador la va a leer como
     si lo fuera"

Aca la posicion sale de los embeddings que MAK ya calculo. La proyeccion 2D es
un calculo de UNA SOLA VEZ: no hay razon para hacerla en el navegador de cada
visitante ni para mandarle 697 vectores de 768 dimensiones. Se hace en la caja,
donde estan los datos, y viaja el resultado -- unos 60 KB contra 2 MB.

Corre EN MAK (ahi vive el indice del micelio):

    python3 gen_campo_iskvw.py --salida ~/campo.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

INDEX = Path(os.path.expanduser("~/research/memoria/index.jsonl"))
FICHAS = Path(os.path.expanduser("~/curatoria/fichas/fichas.jsonl"))


def vectores_por_obra():
    """Un vector por obra del corpus, promediando sus fragmentos."""
    import numpy as np

    grupos = {}
    with INDEX.open(encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            try:
                e = json.loads(linea)
            except ValueError:
                continue
            if e.get("dir") != "corpus" or not e.get("vec"):
                continue
            grupos.setdefault(e["path"], []).append(e["vec"])
    ids, vecs = [], []
    for path, lista in sorted(grupos.items()):
        ids.append(Path(path).stem)
        vecs.append(np.mean(np.array(lista, dtype=np.float32), axis=0))
    return ids, (np.array(vecs, dtype=np.float32) if vecs else np.zeros((0, 0)))


def proyectar(m, k=3, perplejidad=30):
    """768 dimensiones -> 2, conservando VECINDAD. Medido, no supuesto.

    Se probaron tres metodos sobre las 697 obras reales, con la misma metrica:

        PCA                      3.8% de varianza conservada
        layout por fuerzas      16.4% de vecindad conservada
        t-SNE (init PCA)        41.8% de vecindad conservada

    Se queda t-SNE. Los dos primeros quedan escritos porque el numero es el
    argumento: sin medirlo, cualquiera de los tres "se ve bien" y dos de ellos
    harian que el campo afirme una cercania que no existe.

    Que mide `vecindad`: de los k vecinos mas afines de cada obra en 768
    dimensiones, cuantos siguen siendo de los k mas cercanos en el plano. Es
    exactamente lo que el campo afirma cuando pone dos obras juntas. Se
    publica en la salida: si algun dia baja, la afirmacion se debilita y hay
    que decirlo, no esconderlo.

    Por que k=3 y no un numero comodo. Medido sobre las 697:

        k    vecindad   azar    ventaja sobre el azar
        3      48.9%    0.4%    x113
        5      45.4%    0.7%     x63
        8      41.8%    1.1%     x36
        50     42.2%    7.2%      x6

    El porcentaje apenas se mueve, pero la ventaja sobre el azar se desploma:
    la proyeccion es fuerte en los vecinos INMEDIATOS y floja en la distancia
    media. Y los inmediatos son justamente los que se ven cuando el diafragma
    esta cerrado y el visitante enfoca una obra. Asi que k no es un parametro
    libre: es cuantas obras se ven alrededor de la enfocada.

    Necesita scikit-learn. Sin el, no se inventa una proyeccion peor y se
    falla: un campo con posiciones falsas es peor que no tener campo.
    """
    import numpy as np
    from sklearn.manifold import TSNE

    n = len(m)
    if n < 5:
        return np.zeros((n, 2), dtype=np.float32), 0.0

    v = m / (np.linalg.norm(m, axis=1, keepdims=True) + 1e-9)
    sim = v @ v.T
    np.fill_diagonal(sim, -1.0)
    vecinos = np.argpartition(-sim, k, axis=1)[:, :k]

    xy = TSNE(n_components=2, perplexity=min(perplejidad, (n - 1) / 3),
              init="pca", random_state=7, max_iter=1000).fit_transform(v)

    d2 = ((xy[:, None, :] - xy[None, :, :]) ** 2).sum(axis=2)
    np.fill_diagonal(d2, 1e9)
    cercanos = np.argpartition(d2, k, axis=1)[:, :k]
    vecindad = sum(len(set(vecinos[i]) & set(cercanos[i])) for i in range(n)) / (n * k)

    xy = xy - xy.mean(axis=0)
    return (xy / (np.abs(xy).max() or 1.0)).astype(np.float32), vecindad


def titulos_y_datos():
    """Lo que MAK percibio, por id de obra. Va como metadato, nunca como voz."""
    datos = {}
    if not FICHAS.exists():
        return datos
    with FICHAS.open(encoding="utf-8", errors="replace") as fh:
        for linea in fh:
            try:
                f = json.loads(linea)
            except ValueError:
                continue
            if f.get("fuente") != "ig":
                continue
            v = f.get("vision") or {}
            desc = (v.get("descripcion") or "").strip()
            if not desc:
                continue
            datos[f.get("id", "")] = {
                "archivo": f.get("ruta_rel") or "",
                "colores": v.get("colores") or [],
                "estilo": v.get("estilo") or "",
                # La descripcion viaja como METADATO: ubica la obra y sirve
                # para buscar. La piel NO la muestra como texto del artista.
                "percibido": desc[:180],
            }
    return datos


def trazar_archivo(base: Path, destino: Path, fichas: dict) -> tuple[int, int]:
    """Cada obra como contorno vectorial. Es lo unico que puede viajar.

    Medido sobre el archivo real: 1,6 GB de imagen se vuelven 4,9 MB de trazo,
    con 649 obras y mediana de 28 subtrazos. Y el visitante no baja los 4,9 MB
    -- baja los pocos KB de la obra donde freno.

    Escribe SOLO si el trazado salio. La primera version abria el archivo antes
    de trazar y dejo 60 SVG de cero bytes que parecian trazos validos: un
    archivo vacio servido como obra es la misma mentira que el resto del
    sistema persigue, escrita en disco.
    """
    from ..plano import trazador as T  # type: ignore

    # Parametros PARA FOTOGRAFIA, distintos de los del plano. Los del plano
    # estan afinados para iconos de alto contraste y verificados byte a byte
    # contra el trazador del navegador: no se tocan.
    #
    # Con los del plano, el archivo real dio 13.5% de siluetas legibles,
    # mediana de 156 subtrazos y 42% de ruido: una foto de un tatuaje no se
    # reduce a un contorno, se rompe en cientos de fragmentos. Subiendo el
    # area minima y la tolerancia:
    #
    #     area 0.0006 tol 0.75  ->  13.5% legible, 42% ruido, 18 MB   (plano)
    #     area 0.01   tol 2.0   ->  60%   legible,  2% ruido, 4.9 MB  (esto)
    #     area 0.03   tol 3.5   ->  82%   legible, pero 1 KB por obra
    #
    # Se queda el del medio: el ultimo es mas legible de lejos y pierde el
    # detalle que hace falta cuando una obra resuelve y se mira de cerca.
    T.AREA_MINIMA, T.TOLERANCIA = 0.01, 2.0

    destino.mkdir(parents=True, exist_ok=True)
    ok = fallo = 0
    for oid, d in fichas.items():
        origen = base / (d.get("archivo") or "")
        if not origen.is_file():
            continue
        salida = destino / f"{oid}.svg"
        if salida.exists():
            continue
        try:
            svg = T.trazar(origen.read_bytes())
        except Exception:
            fallo += 1          # video o imagen sin contraste: no se escribe nada
            continue
        salida.write_text(svg, encoding="utf-8")
        ok += 1
    return ok, fallo


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--salida", type=Path,
                    default=Path(os.path.expanduser("~/campo.json")))
    # Los vectores viven en MAK y sklearn vive en Windows. En vez de instalar
    # media ciencia de datos en la caja, se exportan una vez y se proyecta
    # donde estan las herramientas.
    ap.add_argument("--vectores", type=Path, default=None,
                    help="JSON {ids, v} exportado desde la caja")
    ap.add_argument("--meta", type=Path, default=None,
                    help="JSON de fichas exportado desde la caja")
    args = ap.parse_args()

    if args.vectores:
        import numpy as np
        d = json.loads(args.vectores.read_text(encoding="utf-8"))
        ids, m = d["ids"], np.array(d["v"], dtype=np.float32)
    elif INDEX.exists():
        ids, m = vectores_por_obra()
    else:
        print("no encuentro el indice ni --vectores", file=sys.stderr)
        return 1
    if len(ids) < 3:
        print(f"solo {len(ids)} obras en el corpus: no alcanza para proyectar",
              file=sys.stderr)
        return 1

    xy, vecindad = proyectar(m)
    meta = (json.loads(args.meta.read_text(encoding="utf-8"))
            if args.meta else titulos_y_datos())

    piezas = []
    for i, oid in enumerate(ids):
        # el id del corpus es "<hash>-<slug>"; el hash es el de la ficha
        corto = oid.split("-", 1)[0]
        d = meta.get(corto, {})
        piezas.append({
            "id": oid,
            "x": round(float(xy[i][0]), 4),
            "y": round(float(xy[i][1]), 4),
            "colores": d.get("colores", [])[:3],
            "estilo": d.get("estilo", ""),
            "percibido": d.get("percibido", ""),
            "archivo": d.get("archivo", ""),
        })

    salida = {
        "version": 1,
        "piezas": piezas,
        "meta": {
            "obras": len(piezas),
            "con_percepcion": sum(1 for p in piezas if p["percibido"]),
            # De los vecinos reales de cada obra, que fraccion sigue siendo
            # vecina en el plano. El campo AFIRMA que lo cercano se parece:
            # esto lo mide. Si baja, la afirmacion es debil y se dice.
            "vecindad_conservada": round(vecindad, 4),
        },
    }
    args.salida.write_text(json.dumps(salida, ensure_ascii=False),
                           encoding="utf-8")
    kb = args.salida.stat().st_size / 1024
    print(f"{args.salida}: {len(piezas)} obras, "
          f"{salida['meta']['con_percepcion']} con percepcion, "
          f"vecindad conservada {salida['meta']['vecindad_conservada']:.1%} "
          f"({kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
