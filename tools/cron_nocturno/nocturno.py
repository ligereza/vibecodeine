"""
tools/cron_nocturno/nocturno.py -- pieza MANIFIESTO #6: CRON NOCTURNO CON
BORRADO (motor-omega, projects/tapiz).

Concepto: cada noche el motor genera UNA variante de telar (loom) nueva.
Una vez por semana, borra UNA variante sin mirar (regla de freno del
motor). Todo local, stdlib + la libreria real projects/tapiz/vibecode/loom.py
(se importa, no se reescribe). Sin red, sin API de Claude/Anthropic.

Omega11 (condicion de fracaso, declarada por el director): la pieza PIERDE
si el borrado es reversible (papelera/backup/copia oculta) o si requiere
una decision humana (confirmacion, revision antes de borrar). Por eso
purge():
  - usa os.remove() -- borrado real de filesystem, sin papelera, sin
    backup previo, sin prompt de confirmacion;
  - elige el archivo condenado con un hash SHA-256 del numero de semana
    ISO (nunca con el modulo random, nunca mirando contenido/edad de los
    archivos): auditable a mano, pero ciego;
  - corre desatendido via Task Scheduler / cron (ver README.md), no por
    input() ni por un humano decidiendo cual borrar.

Modos:
  generate -- crea la variante SVG de HOY en salidas/. El motivo (loom
    mode) y el caracter de relleno se derivan deterministicamente de la
    fecha: mismo dia -> misma pieza; dia distinto -> casi siempre motivo
    distinto (20 modos disponibles: field/border/medallion/mihrab mas los
    motifs-plugin de vibecode/motifs/). La fuente digerida es el propio
    loom.py -- el motor se teje a si mismo cada noche.
  purge -- si HOY es el dia configurado (default: domingo, weekday=6) y
    hay >= min_variants (default 2) variantes acumuladas, borra UNA de
    forma permanente y deja una linea en lapidas.log (fecha + nombre de
    archivo, NUNCA contenido).

Salidas (gitignoradas -- el director debe agregar el patron de abajo a
.gitignore; este modulo no lo edita):
    tools/cron_nocturno/salidas/

lapidas.log SI se versiona (es evidencia/registro de la pieza corriendo,
no un artefacto generado descartable).

CLI:
    py tools/cron_nocturno/nocturno.py generate
    py tools/cron_nocturno/nocturno.py purge
    py tools/cron_nocturno/nocturno.py generate --out DIR --date YYYY-MM-DD
    py tools/cron_nocturno/nocturno.py purge --out DIR --lapidas RUTA --weekday 6

Overrides sin flags (utiles para tests y para cron sin argv custom):
    CRON_NOCTURNO_SALIDAS  -- directorio de salidas (default: salidas/)
    CRON_NOCTURNO_LAPIDAS  -- ruta de lapidas.log (default: lapidas.log)

Como libreria:
    from nocturno import generate, purge
    generate(out_dir=Path("..."), day=date(2026, 7, 16))
    purge(out_dir=..., lapidas_path=..., today=..., weekday=6)
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional, Sequence

# --- Importa el motor loom como libreria (solo lectura de su API, no se
# reescribe). Mismo patron que projects/tapiz/vibecode_spaces.py y
# tests/test_tapiz_vibecode.py: el paquete "vibecode" vive fuera de
# src/flujo, se agrega su carpeta padre al sys.path.
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[1]
_TAPIZ_DIR = _REPO_ROOT / "projects" / "tapiz"
if str(_TAPIZ_DIR) not in sys.path:
    sys.path.insert(0, str(_TAPIZ_DIR))

from vibecode.loom import LOOM_MODES  # noqa: E402
from vibecode.svg_export import render_svg  # noqa: E402

# Fuente digerida cada noche: el propio loom.py (el motor se teje a si
# mismo). Constante a proposito: lo que cambia noche a noche es el motivo
# (LOOM_MODES) y el caracter de relleno, no el texto de entrada.
_LOOM_SOURCE_PATH = _TAPIZ_DIR / "vibecode" / "loom.py"

# Caracteres de relleno ASCII-safe (evita problemas de consola cp1252 en
# Windows; ver gotcha conocido del repo sobre encoding en terminal).
_FILL_CHARS: Sequence[str] = (".", "+", "*", "#")

_DEFAULT_OUT_DIR = _HERE / "salidas"
_DEFAULT_LAPIDAS = _HERE / "lapidas.log"

_VARIANT_PREFIX = "variante_"
_VARIANT_SUFFIX = ".svg"

_DEFAULT_PURGE_WEEKDAY = 6  # date.weekday(): lunes=0 .. domingo=6
_MIN_VARIANTS_FOR_PURGE = 2


def _seed_for_date(day: date) -> int:
    """Entero deterministico derivado de la fecha (YYYYMMDD)."""
    return int(day.strftime("%Y%m%d"))


def _pick_mode(day: date, modes: Sequence[str] = LOOM_MODES) -> str:
    """Motivo loom del dia, deterministico (mismo dia -> mismo motivo)."""
    if not modes:
        raise ValueError("LOOM_MODES esta vacio")
    return modes[_seed_for_date(day) % len(modes)]


def _pick_fill_char(day: date) -> str:
    """Caracter de relleno del dia, deterministico."""
    return _FILL_CHARS[_seed_for_date(day) % len(_FILL_CHARS)]


def _digest_source() -> str:
    return _LOOM_SOURCE_PATH.read_text(encoding="utf-8")


def _variant_filename(day: date, mode: str) -> str:
    return f"{_VARIANT_PREFIX}{day.strftime('%Y%m%d')}_{mode}{_VARIANT_SUFFIX}"


def _resolve_out_dir() -> Path:
    env_override = os.environ.get("CRON_NOCTURNO_SALIDAS")
    return Path(env_override) if env_override else _DEFAULT_OUT_DIR


def _resolve_lapidas_path() -> Path:
    env_override = os.environ.get("CRON_NOCTURNO_LAPIDAS")
    return Path(env_override) if env_override else _DEFAULT_LAPIDAS


def generate(out_dir: Optional[Path] = None, day: Optional[date] = None) -> Path:
    """
    Genera UNA variante SVG para `day` (default: hoy) en `out_dir`
    (default: tools/cron_nocturno/salidas/ o CRON_NOCTURNO_SALIDAS).
    Deterministico: mismo dia siempre produce el mismo motivo/caracter
    (una segunda corrida el mismo dia sobreescribe el mismo archivo, no
    duplica).
    """
    day = day or date.today()
    out_dir = Path(out_dir) if out_dir is not None else _resolve_out_dir()
    out_dir.mkdir(parents=True, exist_ok=True)

    mode = _pick_mode(day)
    fill_char = _pick_fill_char(day)
    text = _digest_source()

    svg = render_svg(
        text,
        mode=mode,
        fill_char=fill_char,
        title=f"cron_nocturno {day.isoformat()} ({mode})",
    )

    path = out_dir / _variant_filename(day, mode)
    path.write_text(svg, encoding="utf-8")
    return path


def _list_variants(out_dir: Path) -> List[Path]:
    if not out_dir.is_dir():
        return []
    found = [
        p
        for p in out_dir.iterdir()
        if p.is_file() and p.name.startswith(_VARIANT_PREFIX) and p.name.endswith(_VARIANT_SUFFIX)
    ]
    return sorted(found, key=lambda p: p.name)


def _week_number(day: date) -> int:
    return day.isocalendar()[1]


def _iso_week_key(day: date) -> str:
    """Clave unica de semana ISO (anio + semana), ej. '2026-W29'."""
    iso = day.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def _already_purged_this_week(lapidas_path: Path, today: date) -> bool:
    """True si lapidas.log ya registra un borrado en la misma semana ISO que
    `today`. Es la guarda que hace real el 'UNA vez por semana': sin esto, un
    trigger duplicado de Task Scheduler/cron o una corrida manual el mismo
    domingo borraria mas de una variante en silencio."""
    if not lapidas_path.exists():
        return False
    week_key = _iso_week_key(today)
    try:
        for line in lapidas_path.read_text(encoding="ascii").splitlines():
            fecha = line.split(" ", 1)[0].strip()
            if not fecha:
                continue
            try:
                if _iso_week_key(date.fromisoformat(fecha)) == week_key:
                    return True
            except ValueError:
                continue  # linea ajena/corrupta: no bloquea, solo se ignora
    except OSError:
        return False
    return False


def _choose_doomed_index(filenames: Sequence[str], week_number: int) -> int:
    """
    Indice del archivo condenado dentro de `filenames` (deben venir YA
    ordenados por el llamador, para que el resultado sea reproducible sin
    importar el orden de iteracion del filesystem).

    Deterministico por semana ISO: el mismo week_number siempre da el
    mismo indice, sin importar que dia exacto de esa semana corre purge().
    Hash SHA-256, no random: cualquiera puede recalcularlo a mano
    (auditable) pero no mira contenido/edad/tamano de los archivos, solo
    el conteo (ciego). Esta es la regla de freno del motor.
    """
    if not filenames:
        raise ValueError("no hay variantes para elegir")
    digest = hashlib.sha256(str(week_number).encode("ascii")).hexdigest()
    return int(digest, 16) % len(filenames)


def _choose_doomed(paths: Sequence[Path], week_number: int) -> Path:
    ordered = sorted(paths, key=lambda p: p.name)
    names = [p.name for p in ordered]
    idx = _choose_doomed_index(names, week_number)
    return ordered[idx]


def purge(
    out_dir: Optional[Path] = None,
    lapidas_path: Optional[Path] = None,
    today: Optional[date] = None,
    weekday: int = _DEFAULT_PURGE_WEEKDAY,
    min_variants: int = _MIN_VARIANTS_FOR_PURGE,
) -> Optional[Path]:
    """
    Borrado ciego semanal. No-op si HOY no es `weekday`, si lapidas.log ya
    registra un borrado en esta misma semana ISO (guarda anti-doble-trigger:
    cron duplicado o corrida manual el mismo domingo), o si hay menos de
    `min_variants` variantes en `out_dir`. Si corre: elige UNA variante por
    hash de la semana ISO (ver _choose_doomed_index), la borra con
    os.remove() -- permanente, sin papelera, sin backup, sin confirm -- y
    deja una lapida (fecha + nombre de archivo, nunca contenido) en
    `lapidas_path`. Devuelve la ruta borrada, o None si no hizo nada.
    """
    today = today or date.today()
    if today.weekday() != weekday:
        return None

    lapidas_path = Path(lapidas_path) if lapidas_path is not None else _resolve_lapidas_path()
    if _already_purged_this_week(lapidas_path, today):
        return None  # ya hubo lapida esta semana ISO: UNA por semana es UNA

    out_dir = Path(out_dir) if out_dir is not None else _resolve_out_dir()
    variants = _list_variants(out_dir)
    if len(variants) < min_variants:
        return None

    week_number = _week_number(today)
    doomed = _choose_doomed(variants, week_number)

    os.remove(doomed)  # permanente: Omega11 -- sin papelera, sin backup

    lapidas_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lapidas_path, "a", encoding="ascii", newline="\n") as f:
        f.write(f"{today.isoformat()} {doomed.name}\n")

    return doomed


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="nocturno.py",
        description="Pieza MANIFIESTO #6: cron nocturno con borrado ciego semanal (motor-omega).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    gen = sub.add_parser("generate", help="Genera la variante de hoy.")
    gen.add_argument(
        "--out", type=Path, default=None,
        help="Directorio de salidas (default: salidas/ o CRON_NOCTURNO_SALIDAS)",
    )
    gen.add_argument(
        "--date", type=_parse_date, default=None,
        help="Fecha a usar en vez de hoy (YYYY-MM-DD)",
    )

    pur = sub.add_parser("purge", help="Borrado ciego semanal si corresponde.")
    pur.add_argument("--out", type=Path, default=None)
    pur.add_argument("--lapidas", type=Path, default=None)
    pur.add_argument("--date", type=_parse_date, default=None, help="Fecha a usar como 'hoy' (YYYY-MM-DD)")
    pur.add_argument(
        "--weekday", type=int, default=_DEFAULT_PURGE_WEEKDAY,
        help="0=lunes .. 6=domingo (default: 6, domingo)",
    )
    pur.add_argument("--min-variants", type=int, default=_MIN_VARIANTS_FOR_PURGE)

    args = parser.parse_args(argv)

    if args.cmd == "generate":
        path = generate(out_dir=args.out, day=args.date)
        print(f"variante generada: {path}")
        return 0

    if args.cmd == "purge":
        removed = purge(
            out_dir=args.out,
            lapidas_path=args.lapidas,
            today=args.date,
            weekday=args.weekday,
            min_variants=args.min_variants,
        )
        if removed is None:
            print("purge: no-op (fuera de horario o variantes insuficientes)")
        else:
            print(f"purge: borrada {removed}")
        return 0

    return 1  # pragma: no cover -- argparse ya exige un subcomando valido


if __name__ == "__main__":
    raise SystemExit(main())
