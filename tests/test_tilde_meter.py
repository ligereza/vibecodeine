"""Tests de desktop/tilde_meter.py (medidor del proyecto tilde, standalone).

Puro stdlib: no toca tkinter, red, ni la GUI. Se agrega desktop/ al path.
"""

import json
import sys
from pathlib import Path

DESKTOP_DIR = Path(__file__).resolve().parents[1] / "desktop"
sys.path.insert(0, str(DESKTOP_DIR))

import tilde_meter  # noqa: E402


def test_count_marks():
    marks = tilde_meter.count_marks("¿Cuántos años tiene el niño?")
    assert marks["¿"] == 1 and marks["á"] == 1 and marks["ñ"] == 2
    assert tilde_meter.count_marks("sin marcas") == {}


def test_strip_marks():
    assert tilde_meter.strip_marks("año") == "ano"
    assert tilde_meter.strip_marks("camión") == "camion"
    assert tilde_meter.strip_marks("¿qué?") == "que?"


def test_degraded_words_detecta_colapso():
    original = "El año pasado compré un camión"
    compressed = "el ano pasado compre un camion grande"
    pairs = dict(map(tuple, tilde_meter.degraded_words(original, compressed)))
    assert pairs.get("año") == "ano"
    assert pairs.get("compré") == "compre"
    assert pairs.get("camión") == "camion"


def test_degraded_words_sin_falsos_positivos():
    # la palabra con marca sobrevive intacta -> no es degradacion
    assert tilde_meter.degraded_words("el año nuevo", "plan para el año nuevo") == []


def test_measure_survival():
    m = tilde_meter.measure("¿año?", "ano")
    assert m["marks_in"] == 2 and m["marks_out"] == 0 and m["survival"] == 0.0
    m2 = tilde_meter.measure("sin marcas", "output")
    assert m2["survival"] is None


def test_measure_and_log_escribe_jsonl(tmp_path):
    log = tmp_path / "log.jsonl"
    r = tilde_meter.measure_and_log("¿año?", "ano", path=str(log))
    assert r["marks_in"] == 2
    entry = json.loads(log.read_text(encoding="utf-8").strip())
    assert entry["original"] == "¿año?" and "ts" in entry


def test_summarize_agrega(tmp_path):
    log = tmp_path / "log.jsonl"
    tilde_meter.measure_and_log("el año", "el ano", path=str(log))
    tilde_meter.measure_and_log("¿qué año?", "que ano", path=str(log))
    s = tilde_meter.summarize(path=str(log))
    assert s["samples"] == 2
    assert s["avg_survival"] == 0.0
    degraded = dict(s["words_most_degraded"])
    assert degraded.get("año -> ano") == 2
    assert tilde_meter.summarize(path=str(tmp_path / "no_existe.jsonl")) == {"samples": 0}
