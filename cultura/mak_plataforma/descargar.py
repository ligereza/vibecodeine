#!/usr/bin/env python3
"""descargar.py -- descargas SEGURAS del organismo MAK.

Solo https, dominios de una allowlist, tamano acotado, sha256 opcional,
manifiesto jsonl. Uso:
    python3 descargar.py URL [--sha256 HASH] [--dest /home/mak/descargas]
"""
import argparse
import hashlib
import json
import os
import sys
import time
import urllib.parse
import urllib.request

ALLOW = {
    "github.com", "raw.githubusercontent.com", "objects.githubusercontent.com",
    "codeload.github.com", "pypi.org", "files.pythonhosted.org",
    "ollama.com", "registry.ollama.ai", "huggingface.co",
    "cdn-lfs.huggingface.co",
}
MAX_BYTES = 2 * 1024 ** 3
DEST_DEFAULT = os.path.expanduser("~/descargas")
MANIFEST = os.path.join(DEST_DEFAULT, "manifest.jsonl")


def dominio_permitido(host):
    host = (host or "").lower()
    return any(host == d or host.endswith("." + d) for d in ALLOW)


def descargar(url, sha256=None, dest=DEST_DEFAULT):
    u = urllib.parse.urlparse(url)
    if u.scheme != "https":
        raise SystemExit("solo https (recibido: %s)" % u.scheme)
    if not dominio_permitido(u.hostname):
        raise SystemExit("dominio fuera de la allowlist: %s\npermitidos: %s"
                         % (u.hostname, ", ".join(sorted(ALLOW))))
    os.makedirs(dest, exist_ok=True)
    nombre = os.path.basename(u.path) or "descarga.bin"
    destino = os.path.join(dest, nombre)
    parcial = destino + ".part"
    req = urllib.request.Request(url, headers={"User-Agent": "mak-organismo/1.0"})
    h = hashlib.sha256()
    total = 0
    with urllib.request.urlopen(req, timeout=60) as r, open(parcial, "wb") as f:
        while True:
            chunk = r.read(1 << 16)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_BYTES:
                f.close()
                os.unlink(parcial)
                raise SystemExit("supera el maximo de 2GB, abortado")
            h.update(chunk)
            f.write(chunk)
    digest = h.hexdigest()
    if sha256 and digest.lower() != sha256.lower():
        os.unlink(parcial)
        raise SystemExit("sha256 NO coincide (esperado %s, real %s); archivo borrado"
                         % (sha256, digest))
    os.replace(parcial, destino)
    reg = {"url": url, "archivo": destino, "bytes": total,
           "sha256": digest, "fecha": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(MANIFEST, "a", encoding="utf-8") as f:
        f.write(json.dumps(reg, ensure_ascii=False) + "\n")
    print("descargado: %s (%d bytes)\nsha256: %s" % (destino, total, digest))
    return destino


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--sha256", default=None)
    ap.add_argument("--dest", default=DEST_DEFAULT)
    a = ap.parse_args()
    try:
        descargar(a.url, a.sha256, a.dest)
    except urllib.error.URLError as e:
        print("descarga fallo: %s" % e, file=sys.stderr)
        sys.exit(1)
