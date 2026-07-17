"""
Tests de tools/cron_nocturno/nocturno.py (pieza MANIFIESTO #6: CRON
NOCTURNO CON BORRADO, motor-omega).

Omega11 (declarada por el director): la pieza pierde si el borrado es
reversible (papelera/backup) o requiere una decision humana. Estos tests
cubren la mecanica determinista de generate()/purge(); el scheduler real
(Task Scheduler / cron, ver README.md) queda fuera del alcance de pytest.
"""

from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

_CRON_DIR = Path(__file__).resolve().parents[1] / "tools" / "cron_nocturno"
sys.path.insert(0, str(_CRON_DIR))

import nocturno  # noqa: E402


def test_generate_creates_one_file(tmp_path):
    out_dir = tmp_path / "salidas"
    path = nocturno.generate(out_dir=out_dir, day=date(2026, 7, 16))
    assert path.exists()
    assert path.parent == out_dir
    assert path.suffix == ".svg"
    content = path.read_text(encoding="utf-8")
    assert content.startswith("<svg")


def test_generate_respects_env_override(tmp_path, monkeypatch):
    out_dir = tmp_path / "otra_salida"
    monkeypatch.setenv("CRON_NOCTURNO_SALIDAS", str(out_dir))
    path = nocturno.generate(day=date(2026, 7, 16))
    assert path.parent == out_dir
    assert path.exists()


def test_generate_is_deterministic_per_day():
    day = date(2026, 7, 16)
    mode_a = nocturno._pick_mode(day)
    mode_b = nocturno._pick_mode(day)
    fill_a = nocturno._pick_fill_char(day)
    fill_b = nocturno._pick_fill_char(day)
    assert mode_a == mode_b
    assert fill_a == fill_b
    assert mode_a in nocturno.LOOM_MODES


def test_generate_varies_across_days():
    n = len(nocturno.LOOM_MODES)
    modes = {nocturno._pick_mode(date(2026, 7, 1 + (d % 28))) for d in range(n)}
    assert len(modes) > 1  # dias distintos no deben colapsar todos al mismo motivo


def test_purge_deletes_exactly_one_and_logs(tmp_path):
    out_dir = tmp_path / "salidas"
    lapidas = tmp_path / "lapidas.log"
    p1 = nocturno.generate(out_dir=out_dir, day=date(2026, 7, 13))
    p2 = nocturno.generate(out_dir=out_dir, day=date(2026, 7, 14))
    assert p1.exists() and p2.exists()

    today = date(2026, 7, 19)  # domingo
    assert today.weekday() == 6
    removed = nocturno.purge(out_dir=out_dir, lapidas_path=lapidas, today=today, weekday=6)

    assert removed is not None
    assert not removed.exists()
    remaining = sorted(out_dir.glob("variante_*.svg"))
    assert len(remaining) == 1
    assert remaining[0] in (p1, p2)

    log_text = lapidas.read_text(encoding="ascii")
    lines = [line for line in log_text.splitlines() if line.strip()]
    assert len(lines) == 1
    assert lines[0].startswith(today.isoformat())
    assert removed.name in lines[0]


def test_purge_noop_off_schedule(tmp_path):
    out_dir = tmp_path / "salidas"
    lapidas = tmp_path / "lapidas.log"
    nocturno.generate(out_dir=out_dir, day=date(2026, 7, 13))
    nocturno.generate(out_dir=out_dir, day=date(2026, 7, 14))

    wrong_day = date(2026, 7, 15)  # miercoles, no domingo
    assert wrong_day.weekday() != 6
    removed = nocturno.purge(out_dir=out_dir, lapidas_path=lapidas, today=wrong_day, weekday=6)

    assert removed is None
    assert len(list(out_dir.glob("variante_*.svg"))) == 2
    assert not lapidas.exists()


def test_purge_noop_when_not_enough_variants(tmp_path):
    out_dir = tmp_path / "salidas"
    lapidas = tmp_path / "lapidas.log"
    nocturno.generate(out_dir=out_dir, day=date(2026, 7, 13))

    today = date(2026, 7, 19)  # domingo, pero solo hay 1 variante
    removed = nocturno.purge(out_dir=out_dir, lapidas_path=lapidas, today=today, weekday=6)

    assert removed is None
    assert len(list(out_dir.glob("variante_*.svg"))) == 1
    assert not lapidas.exists()


def test_purge_uses_os_remove_permanently_no_trash(tmp_path):
    """Omega11: el archivo debe desaparecer del filesystem por completo,
    no moverse a una papelera/subcarpeta oculta dentro de tmp_path."""
    out_dir = tmp_path / "salidas"
    lapidas = tmp_path / "lapidas.log"
    nocturno.generate(out_dir=out_dir, day=date(2026, 7, 13))
    nocturno.generate(out_dir=out_dir, day=date(2026, 7, 14))

    today = date(2026, 7, 19)
    removed = nocturno.purge(out_dir=out_dir, lapidas_path=lapidas, today=today, weekday=6)
    assert removed is not None

    all_files_after = set()
    for _root, _dirs, files in os.walk(tmp_path):
        all_files_after.update(files)
    assert removed.name not in all_files_after


def test_doomed_choice_is_deterministic_within_a_week():
    filenames = [
        "variante_20260713_field.svg",
        "variante_20260714_border.svg",
        "variante_20260715_gul.svg",
    ]
    monday = date(2026, 7, 13)
    sunday = date(2026, 7, 19)
    assert monday.isocalendar()[1] == sunday.isocalendar()[1]

    ordered = sorted(filenames)
    idx_monday = nocturno._choose_doomed_index(ordered, monday.isocalendar()[1])
    idx_sunday = nocturno._choose_doomed_index(ordered, sunday.isocalendar()[1])
    assert idx_monday == idx_sunday


def test_doomed_choice_no_randomness_same_inputs_same_output():
    filenames = ["a.svg", "b.svg", "c.svg"]
    week = 29
    idx_1 = nocturno._choose_doomed_index(filenames, week)
    idx_2 = nocturno._choose_doomed_index(filenames, week)
    assert idx_1 == idx_2


def test_doomed_choice_different_weeks_can_differ():
    filenames = [f"variante_{i:03d}.svg" for i in range(12)]
    indices = {nocturno._choose_doomed_index(filenames, week) for week in range(1, 53)}
    assert len(indices) > 1  # el hash no debe colapsar todas las semanas al mismo indice
