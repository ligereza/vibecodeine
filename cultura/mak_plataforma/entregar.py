#!/usr/bin/env python3
"""entregar.py -- el cargo ENTREGADOR del organismo MAK.

Cierra el loop codex -> repo: cosecha las piezas de codigo que codex dejo en
estado 'listo', valida que COMPILAN, y las lleva al repo flujo como PR draft
(gated por CI + branch protection). No toca main. Idempotente via un archivo de
estado (codex_delivered.json): un job_id ya entregado no se re-procesa.

Filosofia (ver context/CAPATAZ.md + DOCTRINA_CLAUDE.md): MAK piensa Y entrega,
sin Claude. El gate es el revisor; el humano mergea el draft. Codigo que no
compila NO se entrega (nada a medias).

Uso:
  python3 entregar.py --dry-run          # muestra que haria, sin git ni PR
  python3 entregar.py                     # entrega UNA pieza (la mas vieja no entregada)
  python3 entregar.py --limit 3          # hasta 3 en una corrida
El cron lo dispara periodico; --limit 1 (default) mantiene blast radius chico.
"""
import argparse
import json
import os
import subprocess
import sys

HOME = os.path.expanduser("~")
CODEX_JOBS = os.path.join(HOME, "codex", "jobs.jsonl")
PIEZAS_DIR = os.path.join(HOME, "codex", "piezas")
REPO = os.path.join(HOME, "flujo")
DEST_REL = os.path.join("cultura", "mak_plataforma", "utilidades")
STATE = os.path.join(HOME, "plataforma", "codex_delivered.json")
LOG = os.path.join(HOME, "plataforma", "logs", "entregar.log")


def log(msg):
    line = msg.rstrip()
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def cargar_estado():
    """Devuelve (job_ids entregados, slugs entregados). Un slug ya entregado no
    se re-entrega (evita spam de PRs por el mismo util cuando el backlog cicla)."""
    try:
        with open(STATE, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            ids = set(data.get("entregados") or [])
            slugs = set(data.get("slugs") or [])
            return ids, slugs
    except (OSError, ValueError):
        pass
    return set(), set()


def guardar_estado(entregados, slugs):
    try:
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        with open(STATE, "w", encoding="utf-8") as f:
            json.dump({"entregados": sorted(entregados), "slugs": sorted(slugs)},
                      f, ensure_ascii=False, indent=1)
    except OSError as e:
        log("WARN no pude guardar estado: %s" % e)


def leer_smoke_meta(md_rel):
    """Lee el meta JSON que generar.py (via codex_lib.guardar_pieza) escribe
    al final de la pieza .md -- ahi vive smoke_ok/smoke_stderr_tail (F2b/#139),
    NO en jobs.jsonl. Busca la ULTIMA ocurrencia de la marca (el meta es
    siempre lo ultimo que escribe guardar_pieza) para no confundirse si el
    codigo generado tiene un comentario que por casualidad contiene el texto
    "meta: ". Devuelve {} si el archivo no existe, no tiene la marca, o el
    meta no es JSON valido (ej. agente_libre.py escribe un meta de TEXTO
    plano, no json -- compatibilidad hacia atras/otros modos, ver
    leer_jobs_listos)."""
    full_md = os.path.join(PIEZAS_DIR, md_rel)
    try:
        with open(full_md, encoding="utf-8") as f:
            texto = f.read()
    except OSError:
        return {}
    marca = "\n---\nmeta: "
    i = texto.rfind(marca)
    if i == -1:
        return {}
    try:
        meta = json.loads(texto[i + len(marca):].strip())
    except ValueError:
        return {}
    return meta if isinstance(meta, dict) else {}


def leer_jobs_listos(bypass_smoke=False):
    """Jobs con estado listo y sin error, en orden de aparicion (mas viejo
    primero).

    F2b/#139: ademas exige smoke_ok (el sandbox de generar.py corrio Y dio
    "PRUEBAS OK" / rc==0) salvo bypass_smoke=True (--sin-smoke, bypass
    humano explicito y logueado). smoke_ok se enriquece desde el meta de la
    pieza (leer_smoke_meta) si jobs.jsonl no lo trae directo.

    Compatibilidad: jobs VIEJOS (de antes de F2b) o de modos que nunca
    corren sandbox (revisar/testear/debug/mejora-libre) no tienen smoke_ok
    -> queda None -> PASAN con warning (transicion suave, no retroactivo).
    Solo smoke_ok == False EXPLICITO se rechaza (marca estado
    "rechazado_smoke", mismo mecanismo de estados que ya usa el archivo --
    en memoria para esta corrida; jobs.jsonl es un ledger append-only y no
    se reescribe)."""
    out = []
    try:
        with open(CODEX_JOBS, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    j = json.loads(line)
                except ValueError:
                    continue
                if j.get("estado") != "listo" or (j.get("error") or "").strip():
                    continue
                if not (j.get("job_id") and j.get("path")):
                    continue
                if "smoke_ok" not in j:
                    meta = leer_smoke_meta(j["path"])
                    if "smoke_ok" in meta:
                        j["smoke_ok"] = meta["smoke_ok"]
                        if meta["smoke_ok"] is False:
                            j["smoke_stderr_tail"] = meta.get("smoke_stderr_tail", "")
                smoke_ok = j.get("smoke_ok")
                if smoke_ok is None:
                    log("WARN %s: sin smoke_ok (job viejo o modo sin sandbox) -- pasa"
                        % j["job_id"])
                elif smoke_ok is False:
                    if bypass_smoke:
                        log("BYPASS --sin-smoke: %s entra pese a smoke_ok=False"
                            % j["job_id"])
                    else:
                        j["estado"] = "rechazado_smoke"
                        log("RECHAZADO_SMOKE %s: %s"
                            % (j["job_id"], (j.get("smoke_stderr_tail") or "")[:200]))
                        continue
                out.append(j)
    except OSError as e:
        log("ERROR no pude leer %s: %s" % (CODEX_JOBS, e))
    return out


def extraer_codigo(md_path):
    """Devuelve el codigo .py de una pieza. Prefiere el .py crudo (mismo prefijo);
    si no existe, parsea el bloque ```python del .md. None si no hay codigo."""
    py_path = os.path.join(PIEZAS_DIR, os.path.splitext(md_path)[0] + ".py")
    if os.path.exists(py_path):
        try:
            with open(py_path, encoding="utf-8") as f:
                code = f.read()
            if code.strip():
                return code, py_path
        except OSError:
            pass
    # fallback: bloque fenced del .md
    full_md = os.path.join(PIEZAS_DIR, md_path)
    try:
        with open(full_md, encoding="utf-8") as f:
            md = f.read()
    except OSError:
        return None, None
    marker = "```python"
    i = md.find(marker)
    if i == -1:
        return None, None
    j = md.find("```", i + len(marker))
    if j == -1:
        return None, None
    code = md[i + len(marker):j].strip("\n")
    return (code if code.strip() else None), full_md


def compila(code):
    """True si el codigo es sintacticamente valido. No lo EJECUTA."""
    try:
        compile(code, "<pieza>", "exec")
        return True, ""
    except SyntaxError as e:
        return False, "SyntaxError: %s (linea %s)" % (e.msg, e.lineno)


def slug_de(path):
    base = os.path.splitext(os.path.basename(path))[0]
    # path = YYYYMMDD-HHMMSS-slug ; quitar el timestamp de 15 chars si esta
    partes = base.split("-", 2)
    return partes[2] if len(partes) == 3 else base


def git(*args, check=True):
    r = subprocess.run(["git", "-C", REPO] + list(args),
                       capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError("git %s -> %s" % (" ".join(args), r.stderr.strip()))
    return r


def entregar_una(job, dry_run):
    job_id = job["job_id"]
    slug = slug_de(job["path"])
    code, src = extraer_codigo(job["path"])
    if not code:
        log("SKIP %s (%s): sin codigo extraible" % (job_id, slug))
        return "skip"
    ok, err = compila(code)
    if not ok:
        log("SKIP %s (%s): no compila -- %s" % (job_id, slug, err))
        return "skip"

    dest_file = "%s.py" % slug
    dest_rel = os.path.join(DEST_REL, dest_file)
    branch = "capataz/%s-%s" % (slug[:40], job_id.split("-")[-1])
    pedido = (job.get("pedido") or "").replace("\n", " ")[:200]

    if dry_run:
        log("DRY-RUN entregaria %s (%s) -> %s en rama %s [%d bytes, compila OK]"
            % (job_id, slug, dest_rel, branch, len(code)))
        return "dry"

    # rama limpia desde origin/main (no importa en que rama este el clon)
    git("fetch", "origin", "--quiet")
    git("checkout", "-B", branch, "origin/main", "--quiet")
    dest_abs = os.path.join(REPO, DEST_REL)
    os.makedirs(dest_abs, exist_ok=True)
    with open(os.path.join(REPO, dest_rel), "w", encoding="utf-8") as f:
        f.write(code if code.endswith("\n") else code + "\n")
    git("add", dest_rel)
    msg = ("feat(mak): utilidad autogenerada -- %s\n\n"
           "Cosechada por el entregador MAK del job codex %s.\n"
           "Pedido: %s\n"
           "Codigo por deepseek-coder via codex; compila OK. Draft para review humano.\n\n"
           "Co-Authored-By: MAK entregador <mak@organismo>" % (slug, job_id, pedido))
    git("commit", "-q", "-m", msg)
    git("push", "-u", "origin", branch, "--quiet")
    pr = subprocess.run(
        ["gh", "pr", "create", "--draft", "--base", "main", "--head", branch,
         "--title", "feat(mak): utilidad autogenerada -- %s" % slug,
         "--body", ("Utilidad stdlib autogenerada por codex y cosechada por el "
                    "entregador MAK (job %s).\n\n**Pedido:** %s\n\n"
                    "Compila OK. Draft: revision humana antes de merge. "
                    "CI dual-OS decide.\n\nParte del loop autonomo MAK->repo "
                    "(ver context/CAPATAZ.md)." % (job_id, pedido))],
        cwd=REPO, capture_output=True, text=True)
    url = (pr.stdout or pr.stderr).strip().splitlines()[-1] if (pr.stdout or pr.stderr) else "?"
    if pr.returncode != 0:
        log("WARN PR fallo para %s: %s" % (job_id, pr.stderr.strip()[:200]))
        return "skip"
    log("ENTREGADO %s (%s) -> %s" % (job_id, slug, url))
    return "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=1)
    ap.add_argument("--sin-smoke", action="store_true",
                    help="bypass humano explicito del gate smoke_ok (F2b/#139): "
                         "entrega igual piezas con smoke_ok=False. Queda logueado.")
    args = ap.parse_args()

    if args.sin_smoke:
        log("AVISO: --sin-smoke activo -- gate de smoke-run desactivado por "
            "decision humana explicita esta corrida")

    entregados, slugs_hechos = cargar_estado()
    jobs = leer_jobs_listos(bypass_smoke=args.sin_smoke)
    # dedup por slug: quedarse con el job MAS NUEVO de cada slug no entregado
    por_slug = {}
    for j in jobs:
        if j["job_id"] in entregados:
            continue
        s = slug_de(j["path"])
        if s in slugs_hechos:
            continue
        prev = por_slug.get(s)
        if prev is None or j["job_id"] > prev["job_id"]:
            por_slug[s] = j
    pendientes = sorted(por_slug.values(), key=lambda j: j["job_id"])
    log("entregar: %d listos, %d slugs ya entregados, %d slugs nuevos pendientes"
        % (len(jobs), len(slugs_hechos), len(pendientes)))
    if not pendientes:
        log("nada que entregar")
        return 0

    hechos = 0
    for job in pendientes:
        if hechos >= args.limit:
            break
        res = entregar_una(job, args.dry_run)
        if not args.dry_run and res in ("ok", "skip"):
            # marcar entregado (skip incluido: no reintentar codigo roto en loop)
            entregados.add(job["job_id"])
            if res == "ok":
                slugs_hechos.add(slug_de(job["path"]))
        if res == "ok":
            hechos += 1
    if not args.dry_run:
        guardar_estado(entregados, slugs_hechos)
    log("entregar: fin (%d entregados esta corrida)" % hechos)
    return 0


if __name__ == "__main__":
    sys.exit(main())
