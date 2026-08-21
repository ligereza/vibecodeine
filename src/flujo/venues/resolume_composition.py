"""Resolve which SSD assets a real Resolume show actually used.

Why this exists
---------------
The SSD index knows which files exist. It cannot tell material that was played
in a show from material that merely sits in a folder, so a folder of 364 assets
looks the same whether it is a tour that ran or a dump nobody opened. That
distinction is the one ``MEMORIA_DIRECCION.md`` §2.12 turns into a report: "the
tool reads the project files to know which assets are really used".

A Resolume composition (``.avc``) is that project file. Measured on the four in
the index: ``DREFGIRA/IMPORT CLAUDIO/SHOWCAUPOLICAN FINAL ANTES DE CAUPO.avc``
carries 37 clip references and 19 of them resolve to exactly one SSD asset each,
landing in ``DREFGIRA/BLOQUE 01 LSDR/`` and ``DREFGIRA/BLOQUE 02 CLASICOS/`` --
the setlist blocks of the tour.

What is being computed
----------------------
Record linkage between two catalogues under a must-abstain rule, not a search.
The only join key the data offers is the file's basename, because the composition
stores absolute paths from a machine that is not this one. A basename that maps
to several SSD assets is not a match; it is an ambiguity, and it stays one.

The resolution rate is a MEASUREMENT, never an assumption. The same four files
give 19/37 for the Caupolican show and 0/72 unambiguous for ``LYON/sampier.avc``,
whose paths point at another machine's Desktop and OneDrive. A tool that reported
one number for "how well this works" would be lying about the second case, so the
rate is reported per composition.

What a resolution does not prove
--------------------------------
That the bytes are the same file. ``full_sha256`` exists for 112 of 45536 assets
in the index, so content identity is unavailable for 99.75% of it. A resolved
reference means "one SSD asset carries this name", which is a candidate, and the
record says so.

Privacy
-------
The stored paths carry real Windows usernames, and more than one distinct user.
``tests/test_privacidad_repo.py`` forbids that pattern in this repository, so
every path leaves this module anonymised. The raw string is never persisted.
"""

from __future__ import annotations

import re
import sqlite3
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path, PureWindowsPath
from typing import Any, Iterable, Mapping, Sequence

CONTRACT = "mak-show-asset-usage-v1"
RESOLVER_VERSION = "basename-linkage-abstain-1"

# Tags Resolume uses for the media a clip points at.
MEDIA_TAGS = ("VideoFile", "AudioFile")

RESOLVED_UNIQUE = "resolved_unique"
AMBIGUOUS = "ambiguous"
NOT_FOUND = "not_found"

_WIN_USER = re.compile(r"(?i)(users[\\/])[^\\/]+")
_DRIVE = re.compile(r"^[A-Za-z]:[\\/]|^\\\\")


def anonymize_path(path: str) -> str:
    """Replace the account segment of a Windows path.

    Not cosmetic: the repository's privacy ratchet rejects a real username in a
    versioned file, and these paths carry several different ones.
    """
    return _WIN_USER.sub(r"\1<usuario>", path or "")


def is_absolute_windows(path: str) -> bool:
    return bool(_DRIVE.match(path or ""))


@dataclass
class Reference:
    """One clip the composition points at."""

    tag: str
    raw_path: str
    basename: str
    absolute: bool
    layer: str = ""
    column: str = ""

    @property
    def safe_path(self) -> str:
        return anonymize_path(self.raw_path)

    @property
    def directory(self) -> str:
        return anonymize_path(str(PureWindowsPath(self.raw_path).parent))


@dataclass
class Resolution:
    reference: Reference
    status: str
    candidates: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "archivo_citado": self.reference.safe_path,
            "basename": self.reference.basename,
            "tipo": self.reference.tag,
            "ruta_absoluta_externa": self.reference.absolute,
            "estado": self.status,
            "assets_en_el_ssd": list(self.candidates),
            **({"nota": "un basename que coincide no prueba los mismos bytes: "
                        "full_sha256 solo existe para 112 de 45536 assets"}
               if self.status == RESOLVED_UNIQUE else {}),
        }


@dataclass
class CompositionRecord:
    contract: str
    resolver_version: str
    source_path: str
    source_name: str
    composition_name: str
    tool: str
    tool_version: str
    canvas: tuple[int, int] | None
    decks: int
    layers: int
    columns: int
    relative_paths_declared: bool
    references: list[Reference] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def distinct_basenames(self) -> set[str]:
        return {r.basename for r in self.references}

    def summary(self) -> dict[str, Any]:
        absolute = sum(1 for r in self.references if r.absolute)
        return {
            "contract": self.contract,
            "resolver_version": self.resolver_version,
            "source_name": self.source_name,
            "composition_name": self.composition_name,
            "tool": f"{self.tool} {self.tool_version}".strip(),
            "lienzo_px": list(self.canvas) if self.canvas else None,
            "decks": self.decks,
            "layers": self.layers,
            "columns": self.columns,
            "rutas_relativas_declaradas": self.relative_paths_declared,
            "referencias": len(self.references),
            "referencias_absolutas_externas": absolute,
            "basenames_distintos": len(self.distinct_basenames),
            "avisos": list(self.warnings),
        }


def _text_value(node: ET.Element) -> str | None:
    value = node.get("value")
    if value:
        return value
    for child in node.iter():
        candidate = child.get("value") or ""
        if PureWindowsPath(candidate).suffix:
            return candidate
    return None


def parse_composition(path: str | Path) -> CompositionRecord:
    """Read one ``.avc`` composition. Read-only; never writes to the source."""
    source = Path(path).expanduser()
    root = ET.parse(source).getroot()
    if root.tag != "Composition":
        raise ValueError(f"not a Resolume Composition document: {source}")
    version = root.find("versionInfo")
    tool = version.get("name", "") if version is not None else ""
    tool_version = ""
    if version is not None:
        parts = [version.get(k) for k in
                 ("majorVersion", "minorVersion", "microVersion")]
        tool_version = ".".join(p for p in parts if p)
    info = root.find("CompositionInfo")
    canvas: tuple[int, int] | None = None
    composition_name = ""
    if info is not None:
        composition_name = info.get("name", "")
        try:
            canvas = (int(info.get("width", "0")), int(info.get("height", "0")))
        except ValueError:
            canvas = None

    references: list[Reference] = []
    seen: set[tuple[str, str]] = set()
    for tag in MEDIA_TAGS:
        for node in root.iter(tag):
            raw = _text_value(node)
            if not raw:
                continue
            key = (tag, raw)
            if key in seen:
                continue
            seen.add(key)
            references.append(Reference(
                tag=tag, raw_path=raw,
                basename=PureWindowsPath(raw).name.casefold(),
                absolute=is_absolute_windows(raw)))

    warnings: list[str] = []
    if not references:
        warnings.append("la composicion no cita ningun archivo de medios")
    collisions = {}
    for reference in references:
        collisions.setdefault(reference.basename, set()).add(reference.raw_path)
    repeated = {b: v for b, v in collisions.items() if len(v) > 1}
    if repeated:
        warnings.append(
            f"{len(repeated)} basename(s) se citan desde directorios distintos "
            "dentro de la misma composicion, asi que el basename no distingue "
            "esos archivos ni siquiera aca: "
            + ", ".join(sorted(repeated)[:3]))
    external = sum(1 for r in references if r.absolute)
    if external and external == len(references):
        warnings.append(
            "todas las rutas son absolutas de otra maquina: la composicion no "
            "es autocontenida y su material puede no estar en este disco")

    def _count(tag: str) -> int:
        try:
            return int(root.get(tag, "0"))
        except ValueError:
            return 0

    return CompositionRecord(
        contract=CONTRACT, resolver_version=RESOLVER_VERSION,
        source_path=str(source), source_name=source.name,
        composition_name=composition_name, tool=tool, tool_version=tool_version,
        canvas=canvas, decks=_count("numDecks"), layers=_count("numLayers"),
        columns=_count("numColumns"),
        relative_paths_declared=(root.get("compositionIsRelative") == "1"),
        references=references, warnings=warnings)


def index_basenames(index_path: str | Path) -> dict[str, list[str]]:
    """Map every SSD basename to the assets that carry it. Read-only."""
    path = Path(index_path).expanduser()
    con = sqlite3.connect("file:" + str(path) + "?mode=ro", uri=True)
    try:
        mapping: dict[str, list[str]] = {}
        for (relative,) in con.execute("SELECT relative_path FROM assets"):
            mapping.setdefault(
                str(relative).rsplit("/", 1)[-1].casefold(), []).append(str(relative))
        return mapping
    finally:
        con.close()


def resolve_references(record: CompositionRecord,
                       basenames: Mapping[str, Sequence[str]]
                       ) -> list[Resolution]:
    """Link each reference to the SSD, abstaining whenever the name is shared.

    The hypothesis being used is "within this corpus a basename identifies one
    file". It is checked rather than assumed: every reference whose basename maps
    to more than one asset is returned as ``ambiguous`` and contributes nothing
    to the usage claim.
    """
    out: list[Resolution] = []
    for reference in record.references:
        candidates = tuple(basenames.get(reference.basename, ()))
        if not candidates:
            status = NOT_FOUND
        elif len(candidates) == 1:
            status = RESOLVED_UNIQUE
        else:
            status = AMBIGUOUS
        out.append(Resolution(reference, status, candidates))
    return out


def usage_report(record: CompositionRecord,
                 resolutions: Sequence[Resolution]) -> dict[str, Any]:
    """What this show used, what is missing, and what could not be decided."""
    by_status: dict[str, list[Resolution]] = {}
    for resolution in resolutions:
        by_status.setdefault(resolution.status, []).append(resolution)
    unique = by_status.get(RESOLVED_UNIQUE, [])
    ambiguous = by_status.get(AMBIGUOUS, [])
    missing = by_status.get(NOT_FOUND, [])
    total = len(resolutions)
    used_assets = sorted({r.candidates[0] for r in unique})
    containers = sorted({a.split("/", 1)[0] for a in used_assets})
    rate = (len(unique) / total) if total else 0.0
    report = {
        "schema": CONTRACT,
        "resolver_version": RESOLVER_VERSION,
        "composicion": record.summary(),
        "tasa_resolucion_inequivoca": round(rate, 4),
        "conteos": {
            "referencias": total,
            RESOLVED_UNIQUE: len(unique),
            AMBIGUOUS: len(ambiguous),
            NOT_FOUND: len(missing),
        },
        "assets_usados": used_assets,
        "contenedores_tocados": containers,
        "referencias": [r.as_dict() for r in resolutions],
        "limites": [
            "El basename es la unica clave de union disponible: la composicion "
            "guarda rutas de otra maquina. Una coincidencia de nombre es "
            "candidata, no identidad de bytes.",
            "full_sha256 existe para 112 de 45536 assets del indice, asi que la "
            "verificacion por contenido no esta disponible para el 99,75 %.",
            "Una referencia no encontrada NO prueba que el archivo no exista: "
            "puede vivir en la maquina que produjo la composicion y nunca haber "
            "estado en este disco.",
            "La tasa de resolucion es de ESTA composicion y no se extrapola: "
            "medida sobre los cuatro .avc del indice va de 0 a 19 de 37.",
        ],
    }
    if ambiguous:
        report["limites"].append(
            f"{len(ambiguous)} referencia(s) quedan sin decidir porque su nombre "
            "lo llevan varios assets del disco; no se elige uno.")
    return report


def orphan_candidates(container: str, used_assets: Iterable[str],
                      index_path: str | Path) -> dict[str, Any]:
    """Assets in a container that no analysed composition references.

    Deliberately named ``candidates``. An asset absent from the compositions we
    could read is not proven unused: only four compositions exist in the index,
    and the shows they describe are not every show. This is a starting list for
    a person, never a delete list.
    """
    path = Path(index_path).expanduser()
    used = set(used_assets)
    con = sqlite3.connect("file:" + str(path) + "?mode=ro", uri=True)
    try:
        rows = [(r[0], int(r[1])) for r in con.execute(
            "SELECT relative_path, bytes FROM assets "
            "WHERE relative_path = ? OR relative_path LIKE ?",
            (container, container + "/%"))]
    finally:
        con.close()
    unreferenced = [(rel, size) for rel, size in rows if rel not in used]
    return {
        "schema": "mak-orphan-candidates-v1",
        "contenedor": container,
        "assets_en_el_contenedor": len(rows),
        "referenciados_por_una_composicion_leida": len(rows) - len(unreferenced),
        "sin_referencia_conocida": len(unreferenced),
        "bytes_sin_referencia": sum(size for _rel, size in unreferenced),
        "advertencia": (
            "sin_referencia_conocida NO significa inutilizado. Solo se leyeron "
            "las composiciones presentes en el indice; un asset puede usarse en "
            "un show cuya composicion no esta aca, o como material fuente de "
            "otro archivo. Esta lista es un punto de partida para una persona, "
            "no una lista de borrado."),
        "mayores_sin_referencia": [
            {"asset": rel, "bytes": size}
            for rel, size in sorted(unreferenced, key=lambda x: -x[1])[:20]],
    }
