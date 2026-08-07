import json

from cultura.mak_plataforma.benchmark import build_rescue_queue, inspect_corpus


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
    assert result["queue"][0]["next_action"] == "review_then_repair_or_archive"


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


def test_benchmark_since_excludes_old_products(tmp_path):
    folder = tmp_path / "informes"
    folder.mkdir()
    path = folder / "old.json"
    path.write_text(json.dumps({"formato": "ensayo"}), encoding="utf-8")
    path.with_suffix(".md").write_text("# x\n", encoding="utf-8")
    since = path.stat().st_mtime + 1

    result = inspect_corpus(tmp_path, since=since)

    assert result["totals"]["products"] == 0


def test_benchmark_creates_non_destructive_rescue_queue(tmp_path):
    folder = tmp_path / "informes"
    folder.mkdir()
    base = folder / "bad"
    base.with_suffix(".json").write_text(json.dumps({
        "formato": "ensayo", "topic": "Quien organizo el evento",
    }), encoding="utf-8")
    base.with_suffix(".md").write_text("# viejo\n", encoding="utf-8")

    result = inspect_corpus(tmp_path)
    queue = build_rescue_queue(result)

    assert result["rescue_queue"] == queue
    assert len(queue) == 2
    row = next(item for item in queue
               if item["issue"] == "route_format_mismatch")
    assert row["status"] == "pending_review"
    assert row["preserve_original"] is True
    assert row["source_json"].endswith("bad.json")
    assert row["source_markdown"].endswith("bad.md")
    assert row["next_action"] == "review_then_relabel_as_informe"
