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
FILTRO = Path(__file__).resolve().parents[1] / "data" / "iskvw_campo_filtro.json"


def cargar_filtro(ruta: Path = FILTRO) -> dict:
    """Que obras entran al campo. Configuracion, NO una puerta que espera.

    El tramo anterior cerro pidiendole al usuario que decidiera cuales de las
    697 eran obra, y su correccion fue de una linea: el objetivo era que el
    sistema TRAGUE lo que le llegue y que el criterio sea configuracion. Es la
    misma leccion ya escrita en este repo para la tarifa RD, los simbolos del
    plano y los tipos de pieza: lo que cambia se edita en un archivo.

    Asi que el default entra en TODO y sumar obras es correr el generador otra
    vez. Si el archivo no esta, no se adivina en silencio: se avisa y se entra
    en todo, que es lo que no pierde nada.
    """
    base = {"incluir": [], "excluir": [], "sin_clasificar": "incluir",
            "sinonimos": {}, "carpetas": []}
    try:
        d = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"aviso: sin filtro utilizable ({ruta.name}: {exc}); "
              f"entra TODO el archivo", file=sys.stderr)
        return base
    for k in base:
        if k in d:
            base[k] = d[k]
    return base


def normalizar(tipo: str, sinonimos: dict) -> str:
    """El tipo tal como lo va a leer el filtro: minusculas y sin sinonimos.

    Medido el 2026-07-27 sobre las 937 fichas del archivo: `tipo_obra` tenia 20
    valores distintos donde debia haber un conjunto fijo, y dos pares eran el
    mismo tipo escrito de dos formas -- tatuaje/tattoo (58 obras partidas en
    dos) y obra/obras. El vocabulario ya quedo cerrado del lado de la
    percepcion; esto arregla lo que quedo escrito antes.
    """
    t = (tipo or "").strip().lower()
    return (sinonimos.get(t) or t)


def de_carpeta(archivo: str) -> str:
    """De que parte del export viene la obra. Es lo primero del `ruta_rel`."""
    return (archivo or "").replace("\\", "/").split("/")[0]


def entra_carpeta(archivo: str, f: dict) -> bool:
    """El origen manda sobre el tipo, y por una razon que no es tecnica.

    Medido el 2026-07-27, ya con el sitio publicado: de 640 obras servidas en
    iskvw.cl solo 208 venian de `posts/`. Habia 141 de `archived_posts/` -- que
    son publicaciones que el usuario ARCHIVO, o sea que decidio sacar de su
    perfil -- y 291 de `other/`, que en un export de Instagram no es el feed.
    Publicar lo archivado revierte una decision suya, y eso no lo arregla
    ninguna prueba verde.

    `carpetas` vacio significa TODAS, igual que `incluir`: el default no
    descarta nada y el criterio se edita en el archivo. Si una carpeta se
    nombra, entra solo esa. Una obra sin ruta no se puede ubicar, asi que
    cuando hay lista, no entra.
    """
    permitidas = [c.strip().lower() for c in (f.get("carpetas") or []) if c]
    if not permitidas:
        return True
    return de_carpeta(archivo).lower() in permitidas


def entra(tipo: str, f: dict) -> bool:
    """Una sola regla, en un solo lugar, para que la salida pueda explicarla."""
    if not tipo:
        return f.get("sin_clasificar", "incluir") != "excluir"
    incluir = [normalizar(x, f["sinonimos"]) for x in f.get("incluir") or []]
    excluir = [normalizar(x, f["sinonimos"]) for x in f.get("excluir") or []]
    if incluir and tipo not in incluir:
        return False
    return tipo not in excluir


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

    try:
        from sklearn.manifold import TSNE
    except ImportError as exc:
        # Failing here is the designed behaviour, stated in the docstring above:
        # a field with invented positions is worse than no field. What was NOT
        # designed is failing as a raw ModuleNotFoundError traceback. sklearn is
        # deliberately absent on MAK -- the comment in main() says the vectors
        # are exported and projected on the box that has the tooling -- so the
        # message has to name that, not leave a stack trace behind.
        raise SystemExit(
            "scikit-learn no esta instalado en esta caja, y es a proposito: los "
            "vectores viven en MAK y la proyeccion corre donde estan las "
            "herramientas. Exporta con --vectores/--meta y proyecta alla, o "
            "instala scikit-learn aca si de verdad quieres proyectar en esta "
            "maquina. No se inventa una proyeccion peor: un campo con "
            "posiciones falsas es peor que no tener campo. "
            f"({exc})") from exc

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
            # Una obra sin descripcion NO se descarta. Antes se hacia, y era el
            # mismo defecto en chico: una cuarta parte del archivo no tiene
            # percepcion todavia, y descartarla aca la borraba del campo sin
            # que nadie lo viera. Entra con lo que tenga.
            datos[f.get("id", "")] = {
                "archivo": f.get("ruta_rel") or "",
                "colores": v.get("colores") or [],
                "estilo": v.get("estilo") or "",
                # El tipo puede venir de la percepcion nueva (vision.tipo_obra,
                # vocabulario cerrado) o de la vieja, que lo escribia en el
                # campo `categoria` de la ficha. Se leen los dos: el archivo ya
                # tiene material de las dos corridas.
                "tipo": (v.get("tipo_obra") or f.get("categoria") or ""),
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
    # Import absoluto: este archivo es un script de `tools/`, no un modulo del
    # paquete, asi que un `from ..plano import` levanta ImportError antes de
    # trazar nada. Estaba escrito relativo y nunca se ejecuto por esta via.
    from flujo.plano import trazador as T  # type: ignore

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


def escribir_indice_trazos(dir_trazos: Path) -> int:
    """La lista de obras que TIENEN trazo, para que la piel no pida las que no.

    Medido el 2026-07-27: 640 de las 697 obras tienen trazo (las 57 restantes son
    video o imagen sin contraste suficiente). Sin esta lista la piel pedia el
    trazo de cualquiera y el navegador registraba un 404 por cada una. Un 404
    esperado no es un error, pero ensucia la consola y con eso vuelve
    indistinguible un fallo de verdad -- y "cero errores de consola" es el
    criterio con el que se acepta una entrega en este repo.

    No necesita ni los vectores ni la caja: lee el directorio y escribe.
    """
    hashes = sorted(p.stem for p in dir_trazos.glob("*.svg")
                    if p.is_file() and p.stat().st_size > 0)
    salida = dir_trazos / "_indice.json"
    salida.write_text(json.dumps({"version": 1, "trazos": hashes}),
                      encoding="utf-8")
    print(f"{salida}: {len(hashes)} trazos")
    return 0


def _contar_carpetas(piezas: list) -> dict:
    """De donde salio lo que quedo. Va en la salida para que el alcance de lo
    publicado sea legible sin abrir el archivo: eso es justo lo que no se vio."""
    c = {}
    for p in piezas:
        k = de_carpeta(p.get("archivo", "")) or "(sin ruta)"
        c[k] = c.get(k, 0) + 1
    return dict(sorted(c.items(), key=lambda x: -x[1]))


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
    ap.add_argument("--filtro", type=Path, default=FILTRO,
                    help="que tipos entran (default: data/iskvw_campo_filtro.json, "
                         "que entra en todo)")
    ap.add_argument("--indice-trazos", type=Path, default=None,
                    metavar="DIR",
                    help="solo escribe DIR/_indice.json con los trazos que hay "
                         "y termina; no necesita vectores ni la caja")
    args = ap.parse_args()

    if args.indice_trazos:
        return escribir_indice_trazos(args.indice_trazos)

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

    meta = (json.loads(args.meta.read_text(encoding="utf-8"))
            if args.meta else titulos_y_datos())
    filtro = cargar_filtro(args.filtro)

    # El filtro se aplica ANTES de proyectar, no despues: t-SNE ubica cada obra
    # respecto de las demas, asi que sacar obras del resultado dejaria a las que
    # quedan colocadas por vecinas que ya no estan. Filtrar despues seria
    # exactamente el defecto que este archivo persigue -- una posicion que
    # afirma una cercania que no se midio.
    tipos, carpetas = {}, {}
    for oid in ids:
        d = meta.get(oid.split("-", 1)[0], {})
        tipos[oid] = normalizar(d.get("tipo", ""), filtro["sinonimos"])
        carpetas[oid] = d.get("archivo", "")
    quedan = [i for i, oid in enumerate(ids)
              if entra_carpeta(carpetas[oid], filtro) and entra(tipos[oid], filtro)]
    fuera = len(ids) - len(quedan)
    if not quedan:
        print("el filtro dejo el campo vacio: revisa "
              f"{args.filtro.name} ('incluir' vacio = todos)", file=sys.stderr)
        return 1
    if len(quedan) < 3:
        print(f"el filtro dejo {len(quedan)} obras: no alcanza para proyectar",
              file=sys.stderr)
        return 1
    if fuera:
        import numpy as np
        ids = [ids[i] for i in quedan]
        m = np.asarray(m)[quedan]

    xy, vecindad = proyectar(m)

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
            "tipo": tipos[oid],
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
            # Que dejo afuera el filtro y con que regla. Va en el archivo para
            # que un campo mas chico de lo esperado se explique solo, en vez de
            # parecer material perdido.
            "filtradas": fuera,
            "filtro": {k: filtro[k] for k in
                       ("incluir", "excluir", "sin_clasificar", "carpetas")},
            "por_carpeta": _contar_carpetas(piezas),
            "sin_clasificar": sum(1 for p in piezas if not p["tipo"]),
            "tipos": sorted({p["tipo"] for p in piezas if p["tipo"]}),
        },
    }
    args.salida.write_text(json.dumps(salida, ensure_ascii=False),
                           encoding="utf-8")
    kb = args.salida.stat().st_size / 1024
    print(f"{args.salida}: {len(piezas)} obras "
          f"({fuera} fuera por filtro, "
          f"{salida['meta']['sin_clasificar']} sin tipo), "
          f"{salida['meta']['con_percepcion']} con percepcion, "
          f"vecindad conservada {salida['meta']['vecindad_conservada']:.1%} "
          f"({kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
