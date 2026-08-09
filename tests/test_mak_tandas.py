import json
import inspect
import subprocess
import sys

from cultura.mak_plataforma import tandas
from cultura.mak_plataforma import providers


def test_provider_plan_burns_premium_before_free_and_local():
    plan = tandas.provider_plan(["ollama", "groq", "watsonx", "aws", "cerebras"])
    assert plan == ["watsonx", "aws", "cerebras", "groq", "ollama"]


def test_provider_plan_survives_without_temporary_credits():
    plan = tandas.provider_plan(["ollama", "groq", "cerebras"],
                                allow_premium=False)
    assert plan == ["cerebras", "groq", "ollama"]


def test_typed_provider_route_prefers_vision_capability_and_keeps_fallback():
    route = providers.route_task("visual", available=["ollama", "aws"])
    assert route["schema"] == "faro-provider-route-v1"
    assert route["provider"] == "aws"
    assert route["fallback_chain"] == []
    assert providers.route_task("judge", available=["watsonx", "ollama"])["provider"] == "ollama"


def test_survival_provider_call_routes_to_ollama(monkeypatch):
    seen = {}

    def fake_call(prompt, base_url=None, model=None, max_tokens=2500, temperature=0.1,
                  response_format=None):
        seen.update({"prompt": prompt, "model": model, "max_tokens": max_tokens})
        return "{}"

    from cultura.mak_plataforma import discernment
    monkeypatch.setattr(discernment, "call_ollama", fake_call)
    monkeypatch.setattr(providers, "load_env", lambda: None)
    assert providers.call("ollama", "brief", model="local") == "{}"
    assert seen == {"prompt": "brief", "model": "local", "max_tokens": 2500}


def test_build_brief_is_provider_agnostic_but_structured():
    brief = tandas.build_brief(
        "mak_quality", "b001", providers=["watsonx", "ollama"])
    assert brief["schema"] == tandas.SCHEMA_VERSION
    assert brief["provider_plan"] == ["watsonx", "ollama"]
    assert brief["result_required"] == list(tandas.RESULT_REQUIRED) + ["product"]
    assert "Cada item debe poder sobrevivir" in brief["prompt"]
    assert "PAQUETE DE EVIDENCIA LOCAL: no incluido" in brief["prompt"]
    assert brief["product_contract"] == ["verdict", "defect_class", "queue_action"]
    assert "CONTRATO DE PRODUCTO" in brief["prompt"]


def test_build_brief_declares_identity_envelope():
    brief = tandas.build_brief("rd_evidence", "identity01",
                               providers=["watsonx"])
    identity = brief["work"]["identity"]
    assert identity["schema"] == "mak-identity-v1"
    assert identity["kind"] == "report"
    assert identity["source_id"] == "rd_evidence:identity01"
    assert identity["entities"]["venue"] == []
    assert brief["work"]["evidence_required"] == [
        "source_manifest", "provider_output", "local_review"]


def test_build_brief_can_include_bounded_evidence():
    brief = tandas.build_brief(
        "adobe_rescue", "b001", providers=["aws"], include_evidence=True,
        max_evidence_chars=5000)
    assert "PAQUETE DE EVIDENCIA LOCAL" in brief["prompt"]
    assert "tools/adobe_panel/README.md" in brief["prompt"]
    assert len(brief["prompt"]) < 12000


def test_profile_prompt_requires_exact_evidence_kind():
    brief = tandas.build_brief("iskvw_curation", "iskvw01",
                               providers=["watsonx"])
    assert "evidence_kind DEBE ser exactamente: artwork_context" in brief["prompt"]


def test_story_record_profile_does_not_use_artwork_contract():
    brief = tandas.build_brief("portfolio_record", "story01",
                               providers=["aws"])
    assert brief["product_contract"] == ["record_kind", "relations", "unknowns"]
    assert "record_kind=story_record" in brief["prompt"]
    assert brief["promotion_policy"]["allowed_formats"] == ["registro"]


def test_area_prompts_name_the_failure_conditions_for_quality_and_opportunities():
    quality = tandas.build_brief("mak_quality", "quality01", providers=["watsonx"])
    opportunity = tandas.build_brief("opportunity_radar", "opportunity01",
                                     providers=["watsonx"])
    assert "format=revision" in quality["prompt"]
    assert "evidence_kind=local_corpus" in quality["prompt"]
    assert "elegibilidad concreta" in opportunity["prompt"]
    assert "source como URL oficial" in opportunity["prompt"]


def test_build_brief_accepts_round_instruction():
    brief = tandas.build_brief(
        "mak_quality", "r002", providers=["watsonx"],
        instruction="Refute the previous batch; do not repeat claims.")
    assert "INSTRUCCION DE ESTA RONDA" in brief["prompt"]
    assert "Refute the previous batch" in brief["prompt"]


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


def test_validate_product_contract_requires_area_fields():
    payload = {"items": [{"product": {"verdict": "accept"}}]}
    ok, errors = tandas.validate_product_contract(payload, "mak_quality")
    assert ok is False
    assert "item_0_missing_product_defect_class" in errors


def test_validate_product_contract_accepts_complete_area_fields():
    payload = {"items": [{"product": {
        "verdict": "archive", "defect_class": "wrong_format",
        "queue_action": "quarantine",
    }}]}
    assert tandas.validate_product_contract(payload, "mak_quality") == (True, [])


def test_ingest_never_promotes_public_curation_from_model_status(tmp_path):
    common = tmp_path / "common_ledger.jsonl"
    payload = {"items": [{
        "claim": "la obra ya debe publicarse",
        "evidence": ["iskvw/datos/campo.json"],
        "files": ["iskvw/datos/campo.json"],
        "confidence": "high",
        "action": "curate",
        "reject_reason": "",
        "format": "curatoria",
        "evidence_kind": "artwork_context",
        "product": {
            "artwork_reading": "lectura concreta",
            "selection": "serie propia",
            "public_status": "publicada",
        },
    }]}

    result = tandas.ingest_result(
        payload, "iskvw_curation", common_path=str(common),
        use_ollama=False, strict_product=True)

    assert result["status"] == "reject"
    assert result["review"]["verdict"] == "reject"
    rows = [json.loads(line) for line in common.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 1
    assert rows[0]["type"] == "reject"


def test_validate_evidence_paths_rejects_invented_files():
    payload = {"items": [{"files": ["does/not/exist.py"]}]}
    ok, errors = tandas.validate_evidence_paths(payload)
    assert ok is False
    assert errors == ["item_0_missing_evidence_path_0"]


def test_validate_evidence_paths_accepts_repo_files():
    payload = {"items": [{"files": ["cultura/mak_plataforma/trabajo.py"]}]}
    assert tandas.validate_evidence_paths(payload) == (True, [])


def test_evidence_package_includes_explicit_rescue_files(tmp_path):
    report = tmp_path / "historical.md"
    report.write_text("contenido historico que debe ser revisado", encoding="utf-8")

    evidence = tandas.evidence_package(
        "mak_quality", paths=[str(report)], max_chars=5000)

    assert str(report) in evidence
    assert "contenido historico" in evidence


def test_validate_evidence_paths_resolves_unique_evidence_pack_basename():
    payload = {"items": [{"files": ["database.py"]}]}
    assert tandas.validate_evidence_paths(payload, area="rd_evidence") == (True, [])


def test_validate_evidence_paths_rejects_unknown_basename():
    payload = {"items": [{"files": ["invented.py"]}]}
    assert tandas.validate_evidence_paths(payload, area="rd_evidence") == (
        False, ["item_0_missing_evidence_path_0"])


def test_validate_evidence_paths_accepts_explicit_batch_files(tmp_path):
    report = tmp_path / "historical.md"
    report.write_text("old report", encoding="utf-8")
    payload = {"items": [{"files": ["historical.md"]}]}
    assert tandas.validate_evidence_paths(
        payload, area="mak_quality", extra_paths=[str(report)]) == (True, [])


def test_explicit_batch_cannot_escape_to_an_existing_repo_file(tmp_path):
    report = tmp_path / "historical.md"
    report.write_text("old report", encoding="utf-8")
    payload = {"items": [{"files": ["context/LAST_HANDOFF.md"]}]}
    ok, errors = tandas.validate_evidence_paths(
        payload, area="mak_quality", extra_paths=[str(report)])
    assert ok is False
    assert errors == ["item_0_missing_evidence_path_0"]


def test_parse_provider_json_accepts_fenced_json():
    assert tandas._parse_provider_json("```json\n{\"items\": []}\n```") == {"items": []}


def test_product_response_schema_requires_area_contract():
    schema = tandas._product_response_schema("tool_archaeology")
    product = schema["properties"]["items"]["items"]["properties"]["product"]
    assert product["required"] == ["existing_path", "reuse_test", "decision"]


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


def test_cli_brief_can_include_evidence():
    result = subprocess.run(
        [sys.executable, "-m", "cultura.mak_plataforma.tandas", "brief",
         "svg_pipeline", "svg01", "--providers", "watsonx",
         "--with-evidence", "--max-evidence-chars", "5000"],
        capture_output=True, text=True, timeout=20)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "cultura/mak_codex/iconos.py" in data["prompt"]


def test_cli_validate_rejects_bad_json():
    result = subprocess.run(
        [sys.executable, "-m", "cultura.mak_plataforma.tandas", "validate"],
        input="not json", capture_output=True, text=True, timeout=20)
    assert result.returncode == 2
    assert json.loads(result.stdout)["errors"] == ["not_json"]


def test_provider_env_aliases_normalize_ibm_names(monkeypatch, tmp_path):
    env = tmp_path / ".env"
    env.write_text(
        "IBM_CLOUD_APIKEY=ibm-key\n"
        "IBM_PROJECT_ID=ibm-project\n"
        "IBM_CLOUD_URL=https://example.ibm\n"
        "AWS_REGION=us-west-2\n",
        encoding="utf-8",
    )
    for key in ("WATSONX_API_KEY", "WATSONX_PROJECT_ID", "WATSONX_URL",
                "AWS_DEFAULT_REGION"):
        monkeypatch.delenv(key, raising=False)
    providers.load_env(str(env))
    assert providers.os.environ["WATSONX_API_KEY"] == "ibm-key"
    assert providers.os.environ["WATSONX_PROJECT_ID"] == "ibm-project"
    assert providers.os.environ["WATSONX_URL"] == "https://example.ibm"
    assert providers.os.environ["AWS_DEFAULT_REGION"] == "us-west-2"


def test_provider_env_candidates_include_mak_research_directory():
    assert "~/research/research.env" in inspect.getsource(providers.load_env)


def test_run_external_batch_persists_raw_and_ingests(monkeypatch, tmp_path):
    common = tmp_path / "common_ledger.jsonl"
    batch = tmp_path / "external_batches.jsonl"
    out_dir = tmp_path / "tandas"

    def fake_call(provider, prompt, model=None, max_tokens=2500, temperature=0.1):
        assert provider == "watsonx"
        assert "AREA: tool_archaeology" in prompt
        assert "Find omissions" in prompt
        assert model == "fake-model"
        assert max_tokens == 123
        return json.dumps({"items": [{
            "claim": "existing archaeology tool should be reused",
            "evidence": ["tools/contexto_repo.py"],
            "files": ["tools/contexto_repo.py"],
            "confidence": "high",
            "action": "reuse",
            "reject_reason": "",
            "product": {"existing_path": "tools/contexto_repo.py",
                         "reuse_test": "tests/test_mak_tandas.py",
                         "decision": "reuse"},
        }]})

    monkeypatch.setattr(tandas.external_providers, "call", fake_call)
    result = tandas.run_external_batch(
        "tool_archaeology", "r001", "watsonx", model="fake-model",
        out_dir=str(out_dir), common_path=str(common), batch_path=str(batch),
        use_ollama=False, max_tokens=123, instruction="Find omissions")
    assert result["status"] == "accepted"
    assert (out_dir / "tool_archaeology-r001-watsonx.raw.txt").is_file()
    rows = [json.loads(line) for line in common.read_text(encoding="utf-8").splitlines()]
    assert [row["type"] for row in rows] == ["decision", "evidence"]
    batch_row = json.loads(batch.read_text(encoding="utf-8"))
    assert batch_row["provider"] == "watsonx"
    assert batch_row["status"] == "accepted"


def test_run_external_batch_closes_visual_files_to_explicit_images(monkeypatch, tmp_path):
    common = tmp_path / "common_ledger.jsonl"
    batch = tmp_path / "external_batches.jsonl"
    out_dir = tmp_path / "tandas"
    image = tmp_path / "frame.jpg"
    image.write_bytes(b"jpeg")
    seen = {}

    def fake_call(provider, prompt, model=None, max_tokens=2500, temperature=0.1,
                  image_paths=None):
        seen["prompt"] = prompt
        seen["images"] = image_paths
        return json.dumps({"items": [{
            "claim": "lectura visual acotada",
            "evidence": [str(image)],
            "files": [str(image)],
            "confidence": "medium",
            "action": "curate",
            "reject_reason": "",
            "format": "curatoria",
            "evidence_kind": "artwork_context",
            "product": {"artwork_reading": "forma y color",
                         "selection": "candidato local",
                         "public_status": "revision_local"},
        }]})

    monkeypatch.setattr(tandas.external_providers, "call", fake_call)
    result = tandas.run_external_batch(
        "iskvw_curation", "visual01", "aws", paths=[], image_paths=[str(image)],
        out_dir=str(out_dir), common_path=str(common), batch_path=str(batch),
        use_ollama=False)
    assert result["status"] == "accepted"
    assert str(image) in seen["prompt"]
    assert seen["images"] == [str(image)]


def test_run_external_batch_repairs_product_once(monkeypatch, tmp_path):
    calls = []
    common = tmp_path / "common.jsonl"
    batch = tmp_path / "external_batches.jsonl"

    def fake_call(provider, prompt, **kwargs):
        calls.append(prompt)
        item = {
            "claim": "existing archaeology tool should be reused",
            "evidence": ["tools/contexto_repo.py"],
            "files": ["tools/contexto_repo.py"],
            "confidence": "high", "action": "reuse", "reject_reason": "",
        }
        if len(calls) > 1:
            item["product"] = {"existing_path": "tools/contexto_repo.py",
                               "reuse_test": "tests/test_mak_tandas.py",
                               "decision": "reuse"}
        return json.dumps({"items": [item]})

    monkeypatch.setattr(tandas.external_providers, "call", fake_call)
    result = tandas.run_external_batch(
        "tool_archaeology", "repair01", "ollama", out_dir=str(tmp_path),
        common_path=str(common), batch_path=str(batch), use_ollama=False)

    assert result["status"] == "accepted"
    assert len(calls) == 2
    assert "Repara SOLO" in calls[1]
    assert result["repair_raw_path"]


def test_product_repair_preserves_work_identity(monkeypatch, tmp_path):
    common = tmp_path / "common.jsonl"
    batch = tmp_path / "batch.jsonl"
    calls = []

    def fake_call(provider, prompt, **kwargs):
        calls.append(prompt)
        item = {
            "claim": "existing archaeology tool should be reused",
            "evidence": ["tools/contexto_repo.py"],
            "files": ["tools/contexto_repo.py"],
            "confidence": "high", "action": "reuse", "reject_reason": "",
        }
        if len(calls) > 1:
            item["product"] = {
                "existing_path": "tools/contexto_repo.py",
                "reuse_test": "tests/test_mak_tandas.py",
                "decision": "reuse",
            }
        return json.dumps({"items": [item]})

    monkeypatch.setattr(tandas.external_providers, "call", fake_call)
    result = tandas.run_external_batch(
        "tool_archaeology", "identity-repair", "ollama",
        out_dir=str(tmp_path), common_path=str(common),
        batch_path=str(batch), use_ollama=False)
    assert result["status"] == "accepted"
    rows = [json.loads(line) for line in common.read_text(encoding="utf-8").splitlines()]
    assert rows[-1]["work"]["work_id"] == "tool_archaeology:identity-repair"
    assert rows[-1]["work"]["identity"]["source_id"] == (
        "tool_archaeology:identity-repair")


def test_run_external_batch_rejects_items_over_budget(monkeypatch, tmp_path):
    batch = tmp_path / "budget.jsonl"

    def oversized_call(*_args, **_kwargs):
        item = {
            "claim": "bounded claim",
            "evidence": ["tools/contexto_repo.py"],
            "files": ["tools/contexto_repo.py"],
            "confidence": "high",
            "action": "reuse",
            "reject_reason": "",
            "product": {
                "existing_path": "tools/contexto_repo.py",
                "reuse_test": "tests/test_mak_tandas.py",
                "decision": "reuse",
            },
        }
        return json.dumps({"items": [item, item]})

    monkeypatch.setattr(tandas.external_providers, "call", oversized_call)
    result = tandas.run_external_batch(
        "tool_archaeology", "budget01", "watsonx", out_dir=str(tmp_path),
        batch_path=str(batch), use_ollama=False, max_items=1)

    assert result["status"] == "revise"
    assert result["errors"] == ["items_over_budget:2>1"]
    row = json.loads(batch.read_text(encoding="utf-8"))
    assert row["status"] == "revise"


def test_run_external_batch_records_provider_error_and_returns(monkeypatch, tmp_path):
    batch = tmp_path / "external_batches.jsonl"

    def failing_call(*_args, **_kwargs):
        raise RuntimeError("boto3_unavailable")

    monkeypatch.setattr(tandas.external_providers, "call", failing_call)
    result = tandas.run_external_batch(
        "mak_quality", "r002", "aws", out_dir=str(tmp_path),
        batch_path=str(batch), use_ollama=False)

    assert result["ok"] is False
    assert result["status"] == "provider_error"
    assert result["errors"] == ["boto3_unavailable"]
    row = json.loads(batch.read_text(encoding="utf-8"))
    assert row["provider"] == "aws"
    assert row["status"] == "provider_error"
    assert row["failure_class"] == "unavailable"


def test_run_external_batch_classifies_timeout_without_promoting(monkeypatch, tmp_path):
    batch = tmp_path / "external_batches.jsonl"

    def timing_out_call(*_args, **_kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr(tandas.external_providers, "call", timing_out_call)
    result = tandas.run_external_batch(
        "svg_pipeline", "timeout01", "ollama", out_dir=str(tmp_path),
        batch_path=str(batch), use_ollama=False)

    assert result["status"] == "provider_error"
    assert result["failure_class"] == "timeout"
    row = json.loads(batch.read_text(encoding="utf-8"))
    assert row["failure_class"] == "timeout"


def test_run_external_batch_sanitizes_lone_surrogates(monkeypatch, tmp_path):
    batch = tmp_path / "external_batches.jsonl"

    def malformed_call(*_args, **_kwargs):
        return '{"items": [{"claim": "bad ' + chr(0xDC81) + '",'

    monkeypatch.setattr(tandas.external_providers, "call", malformed_call)
    result = tandas.run_external_batch(
        "tool_archaeology", "surrogate01", "ollama", out_dir=str(tmp_path),
        batch_path=str(batch), use_ollama=False)

    assert result["status"] == "invalid"
    raw = (tmp_path / "tool_archaeology-surrogate01-ollama.raw.txt").read_text(
        encoding="utf-8")
    assert "�" in raw


def test_run_external_batch_sanitizes_escaped_surrogates_after_json_load(
        monkeypatch, tmp_path):
    common = tmp_path / "common.jsonl"
    batch = tmp_path / "external_batches.jsonl"

    def escaped_call(*_args, **_kwargs):
        return json.dumps({"items": [{
            "claim": "bad " + chr(0xDC81),
            "evidence": ["tests/test_mak_tandas.py"],
            "files": ["tests/test_mak_tandas.py"],
            "confidence": "high", "action": "reuse", "reject_reason": "",
            "product": {"existing_path": "tests/test_mak_tandas.py",
                         "reuse_test": "tests/test_mak_tandas.py",
                         "decision": "reuse"},
        }]})

    monkeypatch.setattr(tandas.external_providers, "call", escaped_call)
    result = tandas.run_external_batch(
        "tool_archaeology", "surrogate02", "ollama", out_dir=str(tmp_path),
        common_path=str(common), batch_path=str(batch), use_ollama=False)

    assert result["status"] == "accepted"
    assert "�" in common.read_text(encoding="utf-8")


def test_cli_run_reports_provider_error_without_traceback():
    env = {
        key: value for key, value in providers.os.environ.items()
        if not key.startswith(("WATSONX", "IBM_", "AWS_"))
    }
    env["PYTHONPATH"] = providers.os.getcwd()
    result = subprocess.run(
        [sys.executable, "-m", "cultura.mak_plataforma.tandas", "run",
         "rd_evidence", "r001", "--provider", "watsonx", "--model", "nope",
         "--common-ledger", "NUL", "--no-ollama"],
        capture_output=True, text=True, timeout=20, cwd=str(providers.os.path.dirname(__file__) or "."),
        env=env)
    assert result.returncode == 2
    data = json.loads(result.stdout)
    assert data["status"] == "provider_error"
    assert "Traceback" not in result.stderr
