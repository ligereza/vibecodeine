import json

from cultura.mak_plataforma.benchmark import inspect_corpus


def test_benchmark_detects_structural_essay_failure(tmp_path):
    folder = tmp_path / "informes"
    folder.mkdir()
    base = folder / "job"
    base.with_suffix(".json").write_text(
        json.dumps({"formato": "ensayo"}), encoding="utf-8")
    base.with_suffix(".md").write_text("# Informe\nrespuesta sin fuentes\n",
                                        encoding="utf-8")

    result = inspect_corpus(tmp_path)

    kinds = {issue["kind"] for issue in result["issues"]}
    assert "essay_structural_gaps" in kinds


def test_benchmark_detects_factual_topic_declared_as_essay(tmp_path):
    folder = tmp_path / "informes"
    folder.mkdir()
    base = folder / "job"
    base.with_suffix(".json").write_text(json.dumps({
        "formato": "ensayo",
        "topic": "Quien organizo el evento en Santiago",
    }), encoding="utf-8")
    base.with_suffix(".md").write_text("# x\n", encoding="utf-8")

    result = inspect_corpus(tmp_path)

    assert any(issue["kind"] == "route_format_mismatch"
               for issue in result["issues"])


def test_benchmark_accepts_complete_pair(tmp_path):
    folder = tmp_path / "informes"
    folder.mkdir()
    base = folder / "job"
    base.with_suffix(".json").write_text(
        json.dumps({"formato": "informe"}), encoding="utf-8")
    base.with_suffix(".md").write_text("respuesta (https://example.test)\n",
                                        encoding="utf-8")

    result = inspect_corpus(tmp_path)

    assert result["totals"]["products"] == 1
    assert result["totals"]["issues"] == 0
