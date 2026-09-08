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
import threading
import time
import urllib.parse
import urllib.request
from contextlib import contextmanager

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows director has no fcntl
    fcntl = None

ALLOW = {
    "github.com", "raw.githubusercontent.com", "objects.githubusercontent.com",
    "codeload.github.com", "pypi.org", "files.pythonhosted.org",
    "ollama.com", "registry.ollama.ai", "huggingface.co",
    "cdn-lfs.huggingface.co",
}
MAX_BYTES = 2 * 1024 ** 3
DEST_DEFAULT = os.path.expanduser("~/descargas")
MANIFEST = os.path.join(DEST_DEFAULT, "manifest.jsonl")
_DOWNLOAD_LOCK = threading.RLock()


@contextmanager
def _exclusive_download_lock(destination):
    """Prevent two workers from sharing the same .part file."""
    with _DOWNLOAD_LOCK:
        lock_path = os.path.abspath(destination) + ".lock"
        parent = os.path.dirname(lock_path)
        os.makedirs(parent, exist_ok=True)
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)


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
    with _exclusive_download_lock(destino):
        partial_path = destino + ".part"
        req = urllib.request.Request(
            url, headers={"User-Agent": "mak-organismo/1.0"})
        h = hashlib.sha256()
        total = 0
        with urllib.request.urlopen(req, timeout=60) as r, open(partial_path, "wb") as f:
            while True:
                chunk = r.read(1 << 16)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_BYTES:
                    f.close()
                    os.unlink(partial_path)
                    raise SystemExit("exceeds the 2GB limit; aborted")
                h.update(chunk)
                f.write(chunk)
        digest = h.hexdigest()
        if sha256 and digest.lower() != sha256.lower():
            os.unlink(partial_path)
            raise SystemExit(
                "sha256 mismatch (expected %s, got %s); file removed"
                % (sha256, digest))
        os.replace(partial_path, destino)
        reg = {"url": url, "archivo": destino, "bytes": total,
               "sha256": digest, "fecha": time.strftime("%Y-%m-%d %H:%M:%S")}
        manifest = os.path.join(dest, "manifest.jsonl")
        with open(manifest, "a", encoding="utf-8") as f:
            f.write(json.dumps(reg, ensure_ascii=False) + "\n")
            f.flush()
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
