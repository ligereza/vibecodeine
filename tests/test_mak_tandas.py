import json
import subprocess
import sys

from cultura.mak_plataforma import tandas


def test_provider_plan_burns_premium_before_free_and_local():
    plan = tandas.provider_plan(["ollama", "groq", "watsonx", "aws", "cerebras"])
    assert plan == ["watsonx", "aws", "cerebras", "groq", "ollama"]


def test_provider_plan_survives_without_temporary_credits():
    plan = tandas.provider_plan(["ollama", "groq", "cerebras"],
                                allow_premium=False)
    assert plan == ["cerebras", "groq", "ollama"]


def test_build_brief_is_provider_agnostic_but_structured():
    brief = tandas.build_brief(
        "mak_quality", "b001", providers=["watsonx", "ollama"])
    assert brief["schema"] == tandas.SCHEMA_VERSION
    assert brief["provider_plan"] == ["watsonx", "ollama"]
    assert brief["result_required"] == list(tandas.RESULT_REQUIRED)
    assert "Cada item debe poder sobrevivir" in brief["prompt"]


def test_validate_result_accepts_atomic_items():
    ok, errors = tandas.validate_result({
        "items": [{
            "claim": "old MAK reports mixed event questions with essays",
            "evidence": ["~/research/informes/x.md"],
            "files": ["cultura/mak_plataforma/trabajo.py"],
            "confidence": "high",
            "action": "refute",
            "reject_reason": "",
        }]
    })
    assert ok is True
    assert errors == []


def test_validate_result_reject_requires_reason():
    ok, errors = tandas.validate_result({
        "items": [{
            "claim": "",
            "evidence": [],
            "files": [],
            "confidence": "low",
            "action": "reject",
            "reject_reason": "",
        }]
    })
    assert ok is False
    assert "item_0_reject_without_reason" in errors


def test_append_ledger_does_not_persist_secrets(tmp_path):
    path = tmp_path / "external_batches.jsonl"
    saved = tandas.append_ledger({
        "area": "rd_evidence",
        "batch_id": "rd01",
        "provider": "watsonx",
        "status": "ok",
        "items": 3,
        "errors": [],
        "api_key": "secret",
    }, path=str(path))
    row = json.loads(path.read_text(encoding="utf-8"))
    assert saved == row
    assert "api_key" not in row
    assert row["provider"] == "watsonx"


def test_write_brief_persists_provider_agnostic_contract(tmp_path):
    brief = tandas.build_brief("svg_pipeline", "svg01",
                               providers=["aws", "groq", "ollama"])
    path = tandas.write_brief(brief, out_dir=str(tmp_path))
    data = json.loads((tmp_path / "svg_pipeline-svg01.json").read_text(
        encoding="utf-8"))
    assert path == str(tmp_path / "svg_pipeline-svg01.json")
    assert data["schema"] == tandas.SCHEMA_VERSION
    assert data["area"] == "svg_pipeline"
    assert data["provider_plan"] == ["aws", "groq", "ollama"]
    assert "prompt" in data


def test_summarize_ledger_is_deterministic(tmp_path):
    path = tmp_path / "external_batches.jsonl"
    tandas.append_ledger({"area": "mak_quality", "batch_id": "a",
                          "provider": "watsonx", "status": "ok",
                          "items": 2}, path=str(path))
    tandas.append_ledger({"area": "mak_quality", "batch_id": "b",
                          "provider": "ollama", "status": "invalid",
                          "items": 0, "errors": ["bad"]}, path=str(path))
    summary = tandas.summarize_ledger(str(path))
    assert summary["total"] == 2
    assert summary["by_area"] == {"mak_quality": 2}
    assert summary["by_provider"] == {"watsonx": 1, "ollama": 1}
    assert summary["by_status"] == {"ok": 1, "invalid": 1}


def test_cli_brief_outputs_portable_json():
    result = subprocess.run(
        [sys.executable, "-m", "cultura.mak_plataforma.tandas", "brief",
         "tool_archaeology", "tools01", "--providers", "aws,ollama"],
        capture_output=True, text=True, timeout=20)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["area"] == "tool_archaeology"
    assert data["provider_plan"] == ["aws", "ollama"]


def test_cli_validate_rejects_bad_json():
    result = subprocess.run(
        [sys.executable, "-m", "cultura.mak_plataforma.tandas", "validate"],
        input="not json", capture_output=True, text=True, timeout=20)
    assert result.returncode == 2
    assert json.loads(result.stdout)["errors"] == ["not_json"]
