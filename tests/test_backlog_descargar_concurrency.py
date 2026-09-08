import hashlib
import importlib.util
import json
import threading
import time
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]


def _load_module(name, relative):
    spec = importlib.util.spec_from_file_location(
        name, RAIZ / relative)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


backlog = _load_module("backlog_codex_under_test",
                       "cultura/mak_plataforma/backlog_codex.py")
descargar = _load_module("download_under_test",
                         "cultura/mak_plataforma/descargar.py")


def test_backlog_concurrent_deduplicates_candidate(tmp_path, monkeypatch):
    path = str(tmp_path / "backlog_codex.txt")
    monkeypatch.setattr(backlog, "BACKLOG_TXT", path)
    monkeypatch.setattr(backlog, "_fuente_modulos", lambda: ["tarea unica"])
    monkeypatch.setattr(backlog, "_fuente_hallazgos", lambda: [])
    monkeypatch.setattr(backlog, "_fuente_salud", lambda: [])

    threads = [threading.Thread(target=backlog.main) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    lines = [line for line in Path(path).read_text().splitlines() if line]
    assert len(lines) == 1
    assert lines[0].startswith("tarea unica # auto ")


class _Respuesta:
    def __init__(self, data):
        self.data = data

    def read(self, _size):
        data, self.data = self.data, b""
        return data

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def test_download_uses_destination_manifest_and_serializes_partial(
        tmp_path, monkeypatch):
    destination = tmp_path / "custom"
    content = b"contenido de prueba"
    active = {"n": 0, "max": 0}
    guard = threading.Lock()

    def open_url(_request, timeout=60):
        assert timeout == 60
        with guard:
            active["n"] += 1
            active["max"] = max(active["max"], active["n"])
        time.sleep(0.03)
        with guard:
            active["n"] -= 1
        return _Respuesta(content)

    monkeypatch.setattr(descargar.urllib.request, "urlopen", open_url)
    url = "https://github.com/example/repo/raw/main/archivo.bin"
    threads = [threading.Thread(target=descargar.descargar,
                                args=(url,), kwargs={"dest": str(destination)})
               for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=3)

    assert active["max"] == 1
    file_path = destination / "archivo.bin"
    assert file_path.read_bytes() == content
    records = [json.loads(line) for line in
               (destination / "manifest.jsonl").read_text().splitlines()]
    assert len(records) == 2
    assert all(record["sha256"] == hashlib.sha256(content).hexdigest()
               for record in records)
