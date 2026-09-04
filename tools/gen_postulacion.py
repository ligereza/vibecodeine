"""Build and check a funding application against a convocatoria's own bases.

The bases of a public competition are a contract: they name the sections a
project must answer, the criteria that score it and their weights, the budget
ceilings, and the documents whose absence puts the application out of the
competition before anyone reads it. All of that is checkable by a machine, and
none of it is checkable by rereading a PDF at two in the morning.

This tool reads a convocatoria description from ``data/*.json`` and a project
from a JSON file, and answers three questions:

* Which required sections are missing or still empty, ordered by the score
  they cost, so the effort goes where the points are.
* Whether the budget respects the declared floor, ceiling and percentage caps.
* Which mandatory documents this project's own declared conditions trigger and
  are not attached.

It writes a Markdown draft with every section in place, each labelled with the
criteria it feeds and their weight.

It does not write the applicant's prose. A section the project leaves empty
comes out marked ``[FALTA]`` and is reported as a finding. Inventing content
for a public application would be inventing evidence, and a generated
paragraph that reads as if the artist wrote it is worse than an empty one.

Identifiers here are English per the repository's language rule; the strings a
person reads stay in Spanish, which is the language of the competition.

    python -m tools.gen_postulacion --list
    python -m tools.gen_postulacion --call fondart-regional-creacion-artistica-2027 --template > proyecto.json
    python -m tools.gen_postulacion --call fondart-regional-creacion-artistica-2027 --project proyecto.json
    python -m tools.gen_postulacion --call ... --project proyecto.json --out borrador.md

Exit status is 1 when a blocking finding stands and ``--strict`` was asked for.
"""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BASES_DIR = ROOT / "data"
BASES_GLOB = "*_20*.json"
SCHEMA = "mak-convocatoria-bases-v1"

BLOCKING = "bloqueante"
WARNING = "aviso"

# A document is demanded only when the project itself declares the condition
# that triggers it. The map is explicit so the tool never invents a formality
# the applicant never described, and never hides one they did.
DOCUMENT_TRIGGERS = {
    "autorizacion_derechos_autor": ("conditions", "uses_third_party_works"),
    "cartas_compromiso_equipo": ("conditions", "has_team"),
    "consentimiento_comunidad_indigena": ("conditions", "activities_in_indigenous_territory"),
    "certificado_inhabilidades_menores": ("conditions", "works_with_minors"),
    "permiso_espacio_publico": ("conditions", "activities_in_public_space"),
    "anteproyecto_arquitectura": ("conditions", "ephemeral_architecture"),
    "compromisos_exhibicion": ("conditions", "outreach_in_existing_venues"),
    "estatutos_persona_juridica": ("lead", "is_legal_entity"),
}


def load_calls(directory: Path = BASES_DIR) -> dict[str, dict]:
    """Every bases file in ``data/`` that declares the convocatoria schema."""
    found: dict[str, dict] = {}
    for path in sorted(directory.glob(BASES_GLOB)):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and data.get("schema") == SCHEMA and data.get("id"):
            data["_file"] = str(path.relative_to(ROOT))
            found[str(data["id"])] = data
    return found


def template(bases: dict) -> dict:
    """An empty project shaped like this convocatoria expects."""
    return {
        "schema": "mak-postulacion-v1",
        "call": bases["id"],
        "title": "",
        "lead": {"name": "", "is_legal_entity": False, "is_for_profit": False},
        "duration_months": 0,
        "budget": {
            "requested_from_fund": 0,
            "co_financing": 0,
            "items": [],
            "contingency": 0,
            "lead_fee": 0,
        },
        "conditions": {
            "uses_third_party_works": False,
            "has_team": False,
            "activities_in_indigenous_territory": False,
            "works_with_minors": False,
            "activities_in_public_space": False,
            "ephemeral_architecture": False,
            "outreach_in_existing_venues": False,
        },
        "declared_documents": [],
        "sections": {section["id"]: "" for section in bases["form_sections"]},
    }


def _blank(value: object) -> bool:
    return not isinstance(value, str) or not value.strip()


def _thousands(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def required_documents(bases: dict, project: dict) -> list[dict]:
    """Documents whose triggering condition this project declares."""
    conditions = project.get("conditions", {}) or {}
    lead = project.get("lead", {}) or {}
    sources = {"conditions": conditions, "lead": lead}

    triggered = []
    catalogue = list(bases.get("mandatory_documents", [])) + list(
        bases.get("evaluation_documents", [])
    )
    for document in catalogue:
        identifier = str(document["id"])
        if identifier == "individualizacion_socios":
            # Two conditions, not one: only a for-profit legal entity owes it.
            fires = bool(lead.get("is_legal_entity")) and bool(lead.get("is_for_profit"))
        elif not document.get("conditional", True):
            fires = True
        else:
            where, key = DOCUMENT_TRIGGERS.get(identifier, (None, None))
            fires = bool(sources.get(where, {}).get(key)) if where else False
        if fires:
            triggered.append(document)
    return triggered


def weight_by_section(bases: dict) -> dict[str, int]:
    """How much score each section carries, summing the criteria it feeds."""
    weights: dict[str, int] = {}
    for criterion in bases.get("criteria", []):
        for section_id in criterion.get("fed_by_sections", []):
            weights[section_id] = weights.get(section_id, 0) + int(criterion["weight"])
    return weights


def _criteria_by_section(bases: dict) -> dict[str, list[dict]]:
    mapping: dict[str, list[dict]] = {}
    for criterion in bases.get("criteria", []):
        for section_id in criterion.get("fed_by_sections", []):
            mapping.setdefault(section_id, []).append(criterion)
    return mapping


def review(bases: dict, project: dict) -> list[dict]:
    """Every finding, blocking ones first. Empty means nothing blocks."""
    findings: list[dict] = []

    def add(level: str, field: str, detail: str) -> None:
        findings.append({"level": level, "field": field, "detail": detail})

    if project.get("call") != bases["id"]:
        add(
            BLOCKING,
            "call",
            f"el proyecto declara {project.get('call')!r} y se está revisando "
            f"contra {bases['id']!r}",
        )

    # A bases file transcribed from press coverage can carry the deadline and
    # the amount and still be missing the taxative document list that decides
    # admissibility. Saying so is the difference between a check and a false
    # sense of one.
    source = bases.get("source", {})
    if source.get("kind", "official_bases") != "official_bases":
        add(
            WARNING,
            "bases",
            f"estas bases se transcribieron de {source['kind']}, no del documento "
            "oficial: la revisión no cubre lo que ahí no está",
        )
    if not bases.get("criteria"):
        add(
            WARNING,
            "bases.criteria",
            "sin criterios de evaluación transcritos: no se puede decir cuánto "
            "puntaje cuesta una sección vacía",
        )

    if _blank(project.get("title")):
        add(BLOCKING, "title", "sin título")

    deadlines = bases.get("deadlines", {})
    max_months = deadlines.get("max_duration_months")
    duration = project.get("duration_months") or 0
    if max_months and duration > max_months:
        add(BLOCKING, "duration_months", f"{duration} meses supera el máximo de {max_months}")
    # Only demanded where the bases set a limit. Blocking on a field the
    # convocatoria never asks for is the kind of over-demand that teaches the
    # operator to skim past the findings.
    if max_months and not duration:
        add(BLOCKING, "duration_months", "sin duración declarada")

    closes = deadlines.get("closes")
    if closes:
        try:
            days_left = (date.fromisoformat(closes) - date.today()).days
        except ValueError:
            days_left = None
        if days_left is not None:
            if days_left < 0:
                add(BLOCKING, "deadline", f"la convocatoria cerró el {closes}")
            elif days_left <= 7:
                add(WARNING, "deadline", f"cierra el {closes}: quedan {days_left} días")

    budget = project.get("budget", {}) or {}
    requested = budget.get("requested_from_fund") or 0
    amounts = bases.get("amounts", {})
    minimum, maximum = amounts.get("min_per_project"), amounts.get("max_per_project")
    if minimum is not None and requested < minimum:
        add(
            BLOCKING,
            "budget.requested_from_fund",
            f"{_thousands(requested)} está bajo el mínimo de {_thousands(minimum)}",
        )
    if maximum is not None and requested > maximum:
        add(
            BLOCKING,
            "budget.requested_from_fund",
            f"{_thousands(requested)} supera el máximo de {_thousands(maximum)}",
        )

    for cap in bases.get("budget_caps", []):
        base_value = budget.get(cap.get("base", "requested_from_fund")) or 0
        value = budget.get(cap["field"]) or 0
        ceiling = base_value * (cap["max_percent"] / 100.0)
        if base_value and value > ceiling:
            share = value / base_value * 100.0
            add(
                BLOCKING,
                f"budget.{cap['field']}",
                f"{_thousands(value)} es {share:.1f}% del solicitado; el tope es "
                f"{cap['max_percent']}% ({_thousands(ceiling)})",
            )

    sections = project.get("sections", {}) or {}
    weights = weight_by_section(bases)
    empty = [s for s in bases["form_sections"] if _blank(sections.get(s["id"]))]
    scored = bool(bases.get("criteria"))
    for section in sorted(empty, key=lambda s: -weights.get(s["id"], 0)):
        weight = weights.get(section["id"], 0)
        detail = (
            f"vacía; alimenta criterios que pesan {weight}%"
            if scored
            else "vacía; el peso no se puede decir sin los criterios de las bases"
        )
        add(BLOCKING, f"sections.{section['id']}", detail)

    declared = {str(item) for item in project.get("declared_documents", [])}
    for document in required_documents(bases, project):
        if str(document["id"]) not in declared:
            add(
                BLOCKING,
                f"documents.{document['id']}",
                f"{document['name']}: exigido por lo que declara el proyecto y no adjuntado",
            )

    order = {BLOCKING: 0, WARNING: 1}
    findings.sort(key=lambda f: order.get(f["level"], 2))
    return findings


def render(bases: dict, project: dict) -> str:
    """A Markdown draft: every section, in place, with what it is scored on."""
    sections = project.get("sections", {}) or {}
    by_section = _criteria_by_section(bases)
    weights = weight_by_section(bases)
    budget = project.get("budget", {}) or {}

    lines: list[str] = []
    lines.append(f"# {project.get('title') or '[FALTA: título]'}")
    lines.append("")
    lines.append(f"**Convocatoria:** {bases['name']} — {bases['edition']}")
    lines.append(f"**Cierre:** {bases['deadlines']['closes']}")
    lines.append(
        f"**Solicitado al fondo:** ${_thousands(budget.get('requested_from_fund') or 0)} "
        f"{bases['amounts']['currency']}"
    )
    lines.append(f"**Duración:** {project.get('duration_months') or 0} meses")
    lines.append("")
    lines.append(
        "> Borrador generado desde las bases. Las secciones marcadas `[FALTA]` están "
        "vacías en el proyecto: la herramienta no escribe el texto de la postulación."
    )
    lines.append("")

    lines.append("## Dónde está el puntaje")
    lines.append("")
    lines.append("| Criterio | Pondera | Secciones que lo alimentan |")
    lines.append("| --- | ---: | --- |")
    for criterion in sorted(bases["criteria"], key=lambda c: -int(c["weight"])):
        feeders = ", ".join(f"`{s}`" for s in criterion.get("fed_by_sections", []))
        lines.append(f"| {criterion['name']} | {criterion['weight']}% | {feeders} |")
    lines.append("")

    for section in bases["form_sections"]:
        criteria = by_section.get(section["id"], [])
        label = ", ".join(f"{c['name']} {c['weight']}%" for c in criteria) or "sin criterio directo"
        lines.append(f"## {section['title']}")
        lines.append("")
        lines.append(f"*Se evalúa en: {label} — peso total {weights.get(section['id'], 0)}%*")
        lines.append("")
        lines.append(f"<!-- {section['guidance']} -->")
        lines.append("")
        content = sections.get(section["id"])
        lines.append(content.strip() if not _blank(content) else "[FALTA]")
        lines.append("")

    triggered = required_documents(bases, project)
    declared = {str(item) for item in project.get("declared_documents", [])}
    lines.append("## Documentos que este proyecto debe adjuntar")
    lines.append("")
    if bases.get("mandatory_documents_warning"):
        lines.append(f"> {bases['mandatory_documents_warning']}")
        lines.append("")
    if not triggered:
        lines.append("Ninguno según las condiciones declaradas en el proyecto.")
    else:
        for document in triggered:
            mark = "x" if str(document["id"]) in declared else " "
            lines.append(f"- [{mark}] {document['name']}")
    lines.append("")

    source = bases.get("source", {})
    lines.append("---")
    lines.append("")
    lines.append(
        f"Bases leídas el {source.get('read_on', 'sin fecha')}: {source.get('bases_pdf', '')}"
    )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tools.gen_postulacion",
        description="Draft and check a funding application against its own bases.",
    )
    parser.add_argument("--list", action="store_true", help="list the known convocatorias")
    parser.add_argument("--call", help="id of the convocatoria to work against")
    parser.add_argument("--project", type=Path, help="JSON file describing the project")
    parser.add_argument("--template", action="store_true", help="print an empty project JSON")
    parser.add_argument("--out", type=Path, help="write the Markdown draft to this file")
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    parser.add_argument("--strict", action="store_true", help="exit 1 if anything blocks")
    args = parser.parse_args(argv)

    calls = load_calls()
    if not calls:
        print(f"no hay bases con schema {SCHEMA} en {BASES_DIR}", file=sys.stderr)
        return 3

    if args.list or not args.call:
        print(f"convocatorias declaradas en {BASES_DIR.relative_to(ROOT)}/:")
        for identifier, bases in calls.items():
            print(f"  {identifier}")
            print(f"      {bases['name']}")
            print(f"      cierre {bases.get('deadlines', {}).get('closes', '?')} "
                  f"| archivo {bases['_file']}")
        return 0

    bases = calls.get(args.call)
    if bases is None:
        print(f"convocatoria desconocida: {args.call}", file=sys.stderr)
        return 3

    if args.template:
        print(json.dumps(template(bases), indent=2, ensure_ascii=False))
        return 0

    if not args.project:
        print("falta --project (o pide --template para partir)", file=sys.stderr)
        return 3
    try:
        project = json.loads(args.project.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"no se pudo leer {args.project}: {error}", file=sys.stderr)
        return 3

    findings = review(bases, project)
    draft = render(bases, project)

    if args.out:
        args.out.write_text(draft, encoding="utf-8")

    if args.json:
        print(json.dumps({"call": bases["id"], "findings": findings}, indent=2,
                         ensure_ascii=False))
    else:
        if args.out:
            print(f"borrador escrito en {args.out}")
        elif not findings:
            print(draft)
        blocking = [f for f in findings if f["level"] == BLOCKING]
        print(f"\nhallazgos: {len(blocking)} bloqueantes, "
              f"{len(findings) - len(blocking)} avisos")
        for finding in findings:
            mark = "!" if finding["level"] == BLOCKING else "-"
            print(f"  {mark} {finding['field']}: {finding['detail']}")

    if args.strict and any(f["level"] == BLOCKING for f in findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
