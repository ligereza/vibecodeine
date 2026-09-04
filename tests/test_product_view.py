from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from flujo.knowledge.application_research_package import compile_application_research_package
from flujo.knowledge.portfolio_dossier import compile_portfolio_dossier
from flujo.knowledge.product_plan import compile_product_plan
from flujo.knowledge.product_view import (
    ARCHIVE_VIEW_SCHEMA,
    ProductViewError,
    project_archive_portfolio_view,
    project_product_view,
    render_archive_portfolio_markdown,
    render_product_markdown,
    stable_json,
    validate_archive_portfolio_view,
    validate_product_view,
)


def _products() -> tuple[dict, dict, dict]:
    from product_chain_fixtures import _chain

    opportunity, practice, fit, programs, possibility, frontier, evidence_return = _chain()
    plan = compile_product_plan(opportunity, practice, fit, programs, possibility, frontier, evidence_return)
    dossier = compile_portfolio_dossier(plan, practice)
    package = compile_application_research_package(plan, opportunity)
    return plan, dossier, package


def _products_with_technical_context() -> tuple[dict, dict, dict]:
    from product_chain_fixtures import _technical_context
    from product_chain_fixtures import _chain

    opportunity, practice, fit, programs, possibility, frontier, evidence_return = _chain()
    plan = compile_product_plan(
        opportunity, practice, fit, programs, possibility, frontier, evidence_return
    )
    context = copy.deepcopy(_technical_context())
    context["provenance"]["archive_id"] = practice["archive_id"]
    context["provenance"]["snapshot_id"] = practice["snapshot_id"]
    dossier = compile_portfolio_dossier(plan, practice, context)
    package = compile_application_research_package(plan, opportunity)
    return plan, dossier, package


def _real_archive_path() -> Path:
    path = Path(__file__).parents[1] / "iskvw" / "datos" / "archivo.json"
    if not path.is_file():
        pytest.skip("requires the generated physical iskvw archive")
    return path


def test_view_is_traceable_and_fail_closed() -> None:
    plan, dossier, package = _products()
    view = project_product_view(plan, dossier, package)
    assert validate_product_view(view) is True
    assert view["lineage"]["shared_product_plan_hash"] is True
    assert view["control"]["publication"] is False
    assert all(row["evidence_refs"] for row in view["claims"] if row["status"] == "supported")
    markdown = render_product_markdown(view)
    assert "borrador interno" in markdown
    assert "No es una publicación" in markdown
    assert "path" not in markdown


def test_foreign_lineage_fails_closed() -> None:
    plan, dossier, package = _products()
    bad = copy.deepcopy(package)
    bad["input_hashes"]["product_plan"] = "sha256:" + "f" * 64
    with pytest.raises(ProductViewError, match="application_package_product_plan_hash_mismatch"):
        project_product_view(plan, dossier, bad)


def test_malformed_rows_fail_closed() -> None:
    plan, dossier, package = _products()
    bad = copy.deepcopy(plan)
    bad["selected_programs"] = ["not-a-program"]
    with pytest.raises(ProductViewError, match="product_plan.selected_program_must_be_object"):
        project_product_view(bad, dossier, package)


def test_deterministic_and_non_mutating() -> None:
    plan, dossier, package = _products()
    originals = copy.deepcopy((plan, dossier, package))
    first = project_product_view(plan, dossier, package)
    second = project_product_view(copy.deepcopy(plan), copy.deepcopy(dossier), copy.deepcopy(package))
    assert first == second
    assert stable_json(first) == stable_json(second)
    assert (plan, dossier, package) == originals


def test_technical_evidence_reaches_view_without_promotion() -> None:
    plan, dossier, package = _products_with_technical_context()
    view = project_product_view(plan, dossier, package)

    assert validate_product_view(view) is True
    assert len(view["technical_evidence"]) == 1
    relation = view["technical_evidence"][0]
    assert relation["predicate"] == "technical_surface_match_candidate"
    assert relation["status"] == "candidate"
    assert relation["artistic_truth"] is False
    assert relation["asset_selection"] is False
    assert view["lineage"]["technical_context_hash"].startswith("sha256:")
    assert view["provenance"]["technical_evidence_is_provenance_only"] is True
    markdown = render_product_markdown(view)
    assert "Evidencia técnica auxiliar" in markdown
    assert "no prueban autoría ni identidad de obra" in markdown
    assert "relative_path" not in markdown


def test_tampered_technical_evidence_fails_closed() -> None:
    plan, dossier, package = _products_with_technical_context()
    view = project_product_view(plan, dossier, package)

    promoted = copy.deepcopy(view)
    promoted["technical_evidence"][0]["artistic_truth"] = True
    with pytest.raises(ProductViewError, match="technical_evidence_0_promotion"):
        validate_product_view(promoted)

    leaked = copy.deepcopy(view)
    leaked["technical_evidence"][0]["relative_path"] = "private/native.psd"
    with pytest.raises(ProductViewError, match="field_set_invalid"):
        validate_product_view(leaked)


def test_cli_carries_technical_evidence(tmp_path: Path) -> None:
    plan, dossier, package = _products_with_technical_context()
    paths = []
    for name, value in (("plan", plan), ("dossier", dossier), ("package", package)):
        path = tmp_path / f"{name}.json"
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        paths.append(str(path))
    completed = subprocess.run(
        [sys.executable, "tools/render_product_view.py", *paths, "--format", "json"],
        cwd=Path(__file__).parents[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert len(output["technical_evidence"]) == 1
    assert output["technical_evidence"][0]["artistic_truth"] is False


def test_cli_json_and_markdown(tmp_path: Path) -> None:
    plan, dossier, package = _products()
    paths = []
    for name, value in (("plan", plan), ("dossier", dossier), ("package", package)):
        path = tmp_path / f"{name}.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        paths.append(str(path))
    command = [sys.executable, "tools/render_product_view.py", *paths]
    as_json = subprocess.run(command + ["--format", "json"], cwd=Path(__file__).parents[1], capture_output=True, text=True)
    assert as_json.returncode == 0, as_json.stderr
    assert json.loads(as_json.stdout)["schema"] == "mak-product-view-v1"
    as_markdown = subprocess.run(command, cwd=Path(__file__).parents[1], capture_output=True, text=True)
    assert as_markdown.returncode == 0, as_markdown.stderr
    assert as_markdown.stdout.startswith("# MAK")


def _archive_fixture() -> dict:
    return {
        "version": 1,
        "fuente": "todo",
        "generado": "2026-08-27T12:00:00",
        "piezas": [
            {
                "id": "work-a",
                "titulo": "Obra A",
                "clase": "obra",
                "fecha": "2026",
                "resumen": "Una obra declarada.",
                "etiquetas": ["a", "visual"],
                "peso": 3,
                "medio": {"tipo": "imagen", "src": "assets/work-a.png"},
                "estado": "publicada",
            },
            {
                "id": "observed-b",
                "titulo": "",
                "clase": "obra",
                "fecha": None,
                "resumen": None,
                "etiquetas": ["corpus"],
                "peso": 2,
                "medio": {"tipo": "imagen", "src": "posts/observed-b.mp4"},
                "estado": "publicada",
                "extra": {"percibido": "Una forma azul observada."},
            },
            {
                "id": "code-c",
                "titulo": "Herramienta C",
                "clase": "codigo",
                "fecha": None,
                "resumen": None,
                "etiquetas": ["code"],
                "peso": 5,
                "medio": {"tipo": "texto"},
                "estado": "publicada",
            },
        ],
        "vinculos": [
            {"de": "observed-b", "a": "work-a", "peso": 0.8, "clase": "semantico"},
            {"de": "code-c", "a": "work-a", "peso": 0.4, "clase": "etiqueta"},
        ],
        "meta": {"por_clase": {"obra": 2, "codigo": 1}},
    }


def test_archive_view_separates_declared_observed_and_practice() -> None:
    archive = _archive_fixture()
    view = project_archive_portfolio_view(archive, max_items_per_format=1)

    assert view["schema"] == ARCHIVE_VIEW_SCHEMA
    assert validate_archive_portfolio_view(view) is True
    assert [row["format_id"] for row in view["formats"]] == [
        "declared-works", "observed-field", "practice-context",
    ]
    assert view["selection"]["declared_work_count"] == 1
    assert view["selection"]["observed_field_count"] == 1
    assert view["selection"]["practice_context_count"] == 1
    observed = next(row for row in view["items"] if row["item_id"] == "observed-b")
    assert observed["title"] is None
    assert observed["observed_description"] == "Una forma azul observada."
    assert observed["observed_description_is_not_author_statement"] is True
    assert "declared_work" not in observed["roles"]
    markdown = render_archive_portfolio_markdown(view)
    assert "Campo observado (no son títulos autorales)" in markdown
    assert "Práctica y código (contexto, no obra automáticamente)" in markdown
    assert "Obra A" in markdown


def test_archive_view_is_deterministic_and_non_mutating() -> None:
    archive = _archive_fixture()
    original = copy.deepcopy(archive)
    first = project_archive_portfolio_view(archive, max_items_per_format=2)
    reordered = copy.deepcopy(archive)
    reordered["piezas"].reverse()
    reordered["vinculos"].reverse()
    second = project_archive_portfolio_view(reordered, max_items_per_format=2)
    assert first == second
    assert stable_json(first) == stable_json(second)
    assert archive == original


def test_archive_view_rejects_private_media_and_foreign_links() -> None:
    private = _archive_fixture()
    private["piezas"][0]["medio"]["src"] = "/home/mak/private.png"
    with pytest.raises(ProductViewError, match="private_path"):
        project_archive_portfolio_view(private)

    foreign = _archive_fixture()
    foreign["vinculos"][0]["a"] = "not-in-archive"
    with pytest.raises(ProductViewError, match="endpoint_unknown"):
        project_archive_portfolio_view(foreign)


def test_real_archive_view_preserves_source_counts() -> None:
    archive_path = _real_archive_path()
    archive = json.loads(archive_path.read_text(encoding="utf-8"))
    view = project_archive_portfolio_view(archive, max_items_per_format=2)
    assert validate_archive_portfolio_view(view) is True
    assert view["source"]["path_hint"] == "iskvw/datos/archivo.json"
    assert view["catalog"]["piece_count"] == len(archive["piezas"])
    assert view["catalog"]["link_count"] == len(archive["vinculos"])
    assert view["selection"]["declared_work_count"] == sum(
        p.get("clase") == "obra" and bool(p.get("titulo")) and bool(p.get("resumen"))
        for p in archive["piezas"]
    )
    assert view["selection"]["omitted_piece_count"] > 0


def test_cli_archive_mode_uses_existing_general_source(tmp_path: Path) -> None:
    _real_archive_path()
    output_path = tmp_path / "archive-view.json"
    command = [
        sys.executable, "tools/render_product_view.py",
        "--archive", "iskvw/datos/archivo.json",
        "--max-items-per-format", "2",
        "--format", "json", "--output", str(output_path),
    ]
    completed = subprocess.run(
        command,
        cwd=Path(__file__).parents[1],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert result["schema"] == ARCHIVE_VIEW_SCHEMA
    assert validate_archive_portfolio_view(result) is True
