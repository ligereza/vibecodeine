"""Rank the projects worth declaring a role for, and hand back a blank sheet.

The F5 Fondart format needs a `rol_y_exclusiones` slot: between two and six
entries reading "context: what I did. Not mine: what I did not." Measured
2026-09-04 against the portable-SSD index, the archive cannot supply one of
them: `owner_status` is `unknown` for all 917 projects and
`owner_evidence_json` is empty for all 917. Nothing recorded who did what.

That is not a gap a tool can close. A role is a claim a person makes about
their own work, and the format's `invalid_if` refuses to render the document
without it precisely because declaring a role without declaring exclusions
overclaims in something you sign.

What a tool can do is say where the hour is best spent. 917 projects is not a
list anybody fills in before a deadline; the twenty that carry the most
evidence is. This ranks them by what the index actually holds and emits a
worksheet with the two fields empty.

It never writes a role, never guesses one from a folder name, and never
reorders on anything but declared, printed evidence.

    python -m tools.rol_candidatos                     # top 20, as a table
    python -m tools.rol_candidatos --limit 40
    python -m tools.rol_candidatos --context LYON      # one container root
    python -m tools.rol_candidatos --json              # machine-readable
    python -m tools.rol_candidatos --hoja hoja.md      # blank worksheet
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_INDEX = Path(
    "/home/mak/labs/portable-ssd-index-20260813/archivo_index.sqlite"
)
SCHEMA = "mak-rol-candidatos-v1"

# What each signal is worth, and why. The weights are declared here rather than
# tuned, because the ranking exists to order a person's attention, not to score
# the work: a project with native project files and video is one you can say
# more about than a folder of exports, and one whose context holds many
# projects is one where a single declaration pays off across neighbours.
WEIGHTS = {
    "structural": 3.0,   # native project files: the strongest "I made this"
    "video": 2.0,
    "image": 0.5,
    "other": 0.1,
    "pdf": 0.5,
}
DIMENSION_BONUS = {"mixto": 12.0, "3d": 8.0, "motion": 6.0, "2d": 3.0}

# Third-party software and system directories. A tool is not a work: an archive
# folder holding 4193 assets of a VJ application ranks high on evidence and is
# not something to declare a role over. These are flagged, never dropped --
# what is not yours belongs in the *other* half of the slot, the exclusions,
# and dropping it would hide the material that half is made of.
#
# The list is deliberately short and names only what is unambiguously somebody
# else's product. It does NOT try to separate tool from work in general,
# because that separation is not a property of the file: code you wrote can be
# a work depending on how it is presented, and that is a decision you make, not
# a measurement this tool can take. Anything not named here comes back
# `sin_clasificar`, which means unexamined, not approved.
THIRD_PARTY_MARKERS = (
    "nestdrop",
    "resolume",
    "milkdrop",
    "sandisksecureaccess",
    ".spotlight-v100",
    ".trashes",
    ".fseventsd",
    "$recycle.bin",
)


def third_party(context: str, path: str) -> str | None:
    """The marker that makes this somebody else's product, or None.

    None means "not on the list", never "confirmed yours".
    """
    haystack = f"{context}/{path}".casefold()
    for marker in THIRD_PARTY_MARKERS:
        if marker in haystack:
            return marker
    return None


def connect(index: Path) -> sqlite3.Connection:
    if not index.is_file():
        raise SystemExit(
            f"no existe el indice {index}. Monta el SSD o pasa --index."
        )
    con = sqlite3.connect(f"file:{index}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def media_mix(con: sqlite3.Connection) -> dict[str, dict[str, int]]:
    """Assets per media kind, per project. One query, not one per project."""
    mix: dict[str, dict[str, int]] = {}
    for row in con.execute(
        "SELECT m.project_id AS pid, a.media_kind AS kind, COUNT(*) AS n "
        "FROM project_members m JOIN assets a ON a.asset_id = m.asset_id "
        "GROUP BY 1, 2"
    ):
        mix.setdefault(str(row["pid"]), {})[str(row["kind"])] = int(row["n"])
    return mix


def score(project: sqlite3.Row, mix: dict[str, int], siblings: int) -> float:
    """A declared sum, printed alongside every row so it can be argued with."""
    total = sum(WEIGHTS.get(kind, 0.0) * count for kind, count in mix.items())
    total += DIMENSION_BONUS.get(str(project["dimensionality"]), 0.0)
    # A context holding many projects rewards one declaration more than a
    # context holding one, because the exclusions carry across neighbours.
    total += min(20.0, siblings * 0.3)
    return round(total, 2)


def candidates(con: sqlite3.Connection, *, context: str | None,
               limit: int) -> list[dict]:
    mix = media_mix(con)
    siblings: dict[str, int] = {}
    for row in con.execute(
        "SELECT container_root AS root, COUNT(*) AS n FROM projects GROUP BY 1"
    ):
        siblings[str(row["root"])] = int(row["n"])

    query = "SELECT * FROM projects"
    params: tuple = ()
    if context:
        query += " WHERE container_root = ?"
        params = (context,)

    rows = []
    for project in con.execute(query, params):
        pid = str(project["project_id"])
        kinds = mix.get(pid, {})
        marker = third_party(
            str(project["container_root"]), str(project["project_path"]))
        rows.append({
            "kind": "software_de_terceros" if marker else "sin_clasificar",
            "third_party_marker": marker or "",
            "project_id": pid,
            "context": str(project["container_root"]),
            "path": str(project["project_path"]),
            "dimensionality": str(project["dimensionality"]),
            "assets": int(project["asset_count"] or 0),
            "bytes": int(project["bytes"] or 0),
            "media": dict(sorted(kinds.items())),
            "siblings_in_context": siblings.get(str(project["container_root"]), 0),
            "score": score(project, kinds, siblings.get(
                str(project["container_root"]), 0)),
            # The two fields the format needs and the archive cannot supply.
            "part_done": "",
            "part_not_done": "",
            # Recorded so a reader never mistakes a ranking for a finding.
            "owner_status": str(project["owner_status"]),
        })
    # Third-party products sink below everything else rather than disappearing:
    # they are still the material of the exclusions half.
    rows.sort(key=lambda row: (
        row["kind"] == "software_de_terceros",
        -row["score"], -row["assets"], row["path"],
    ))
    return rows[:limit]


def worksheet(rows: list[dict]) -> str:
    """A blank sheet shaped like the slot it feeds. Nothing is pre-filled."""
    lines = [
        "# rol_y_exclusiones — hoja para llenar a mano",
        "",
        "La ranura `rol_y_exclusiones` del formato F5 pide entre 2 y 6 entradas,",
        "con la gramática `{context_label}: {part_done}. No propio: {part_not_done}.`",
        "",
        "El índice del archivo no registra autoría: `owner_status` es `unknown`",
        "en los 917 proyectos. Estas filas están ordenadas por la evidencia que",
        "sí hay, para que el rato que tengas rinda. **Las dos columnas van vacías",
        "a propósito: declarar un rol es una afirmación tuya, no una medición.**",
        "",
        "| # | contexto | proyecto | evidencia | qué hice | qué NO es mío |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for index, row in enumerate(rows, 1):
        evidence = ", ".join(
            f"{count} {kind}" for kind, count in row["media"].items()
        ) or f"{row['assets']} activos"
        label = row["context"]
        if row["kind"] == "software_de_terceros":
            label = f"{row['context']} (!) software de terceros"
        lines.append(
            f"| {index} | {label} | `{row['path']}` | {evidence} |  |  |"
        )
    lines.append("")
    lines.append(
        "Al llenarla, recordá que el formato exige la mitad negativa: una fila"
    )
    lines.append(
        "con `qué hice` y sin `qué NO es mío` es exactamente lo que su"
    )
    lines.append("`invalid_if` rechaza.")
    lines.append("")
    lines.append(
        "Las filas marcadas (!) son producto de otra gente. Van al final y no se"
    )
    lines.append(
        "borran: lo que no es tuyo es justamente el material de la columna de"
    )
    lines.append("exclusiones.")
    lines.append("")
    lines.append(
        "Lo que esta hoja NO decide: si una herramienta tuya es una obra. Un"
    )
    lines.append(
        "script o un sistema que escribiste puede serlo según cómo lo"
    )
    lines.append(
        "presentes, y eso es una decisión tuya, no una propiedad del archivo."
    )
    lines.append(
        "Todo lo no marcado sale como `sin_clasificar`, que significa sin"
    )
    lines.append("examinar, no aprobado.")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tools.rol_candidatos",
        description="Rank projects worth declaring a role for. Declares none.",
    )
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--context", default=None, help="one container root")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--hoja", type=Path, help="write the blank worksheet here")
    args = parser.parse_args(argv)

    con = connect(args.index)
    try:
        rows = candidates(con, context=args.context, limit=max(1, args.limit))
        total = con.execute("SELECT COUNT(*) n FROM projects").fetchone()["n"]
        undeclared = con.execute(
            "SELECT COUNT(*) n FROM projects WHERE owner_status = 'unknown'"
        ).fetchone()["n"]
    finally:
        con.close()

    if args.hoja:
        args.hoja.parent.mkdir(parents=True, exist_ok=True)
        args.hoja.write_text(worksheet(rows), encoding="utf-8")
        print(f"hoja en blanco escrita en {args.hoja}")
        return 0

    if args.json:
        print(json.dumps({
            "schema": SCHEMA,
            "projects_total": total,
            "owner_undeclared": undeclared,
            "candidates": rows,
        }, indent=2, ensure_ascii=False))
        return 0

    print(f"proyectos indexados: {total} | sin autoria declarada: {undeclared}")
    print("el orden es por evidencia disponible; el rol lo declara una persona\n")
    print(f"{'#':>3} {'puntaje':>8} {'activos':>8}  {'contexto':<18} proyecto")
    for index, row in enumerate(rows, 1):
        print(f"{index:>3} {row['score']:>8} {row['assets']:>8}  "
              f"{row['context'][:18]:<18} {row['path'][:56]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
