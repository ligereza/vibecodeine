import json

import pytest

from cultura.mak_research.grammar import (
    discover_library,
    expand_program,
    load_contract,
    compress_program,
    resume_experiment,
    run_experiment,
)


pytestmark = pytest.mark.mak

MANIFEST = "/home/mak/work/grammar-lab-20260912/corpus_manifest.json"


def test_library_is_inferred_from_repeated_fragments():
    context = load_contract(MANIFEST)
    library = discover_library(context["partitions"]["construction"])

    names = {operation["name"] for operation in library["operations"]}
    assert names == {"text_layer_marca_v1", "repeat_layer_group_v1"}
    assert "text_mark_v1" not in names
    assert all(operation["source_examples"] for operation in library["operations"])
    assert all(operation["declared_cost"]["before_bytes"] > 0
               for operation in library["operations"])


def test_learned_program_expands_losslessly():
    context = load_contract(MANIFEST)
    library = discover_library(context["partitions"]["construction"])

    for row in context["rows"]:
        program = compress_program(row, library)
        assert expand_program(program, library) == row

    calls = compress_program(context["by_slug"]["08-red-global"], library)["parts"]
    assert any(part["node"]["op"] == "call" for part in calls)


def test_run_checkpoint_and_resume(tmp_path):
    output = tmp_path / "grammar-run"
    stopped = run_experiment(
        corpus=MANIFEST,
        generations=3,
        seed=42,
        max_candidates=24,
        output=output,
        stop_after_generation=0,
    )
    assert stopped["status"] == "stopped"
    checkpoint = json.loads((output / "checkpoint.json").read_text())
    assert checkpoint["completed_generations"] == [0]
    assert checkpoint["candidate_count"] == 12

    completed = resume_experiment(output / "checkpoint.json")
    assert completed["status"] == "completed"
    checkpoint = json.loads((output / "checkpoint.json").read_text())
    metrics = json.loads((output / "metrics.json").read_text())
    assert checkpoint["completed_generations"] == [0, 1, 2]
    assert checkpoint["candidate_count"] == 24
    assert metrics["vocabulary_comparison"]["expanded"]["expanded_exact_count"] == 8
    assert metrics["final_reserved_evaluation"]["invalid_records_preserved"] == [
        "10-inclusividad"
    ]
    assert len(list((output / "svg").glob("*.svg"))) == 22
    assert len(list((output / "programs").glob("*.json"))) == 24
