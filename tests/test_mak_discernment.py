import json
import subprocess
import sys

from cultura.mak_plataforma import discernment
from cultura.mak_plataforma import tandas


def test_review_prompt_covers_all_batch_areas():
    for area in tandas.AREAS:
        prompt = discernment.build_review_prompt(area, {"items": []})
        assert "Ollama" in prompt
        assert discernment.AREA_DOMAINS[area] in prompt
        assert discernment.SCHEMA_VERSION in prompt


def test_adobe_rescue_is_separate_from_svg_and_blender():
    brief = tandas.build_brief(
        "adobe_rescue", "adobe01", providers=["watsonx", "ollama"])
    assert brief["area"] == "adobe_rescue"
    assert "Illustrator/Adobe bridge" in brief["purpose"]
    assert "Blender" in brief["prompt"]
    assert brief["local_review"]["provider"] == "ollama"
    assert '"domain": "adobe"' in brief["local_review"]["prompt"]


def test_validate_review_accepts_local_judgment():
    ok, errors = discernment.validate_review({
        "schema": discernment.SCHEMA_VERSION,
        "verdict": "revise",
        "domain": "rd",
        "reason": "missing official source",
        "risks": ["secondary source only"],
        "missing_evidence": ["official page"],
        "next_action": "find BCN or ministry source",
    }, area="rd_evidence")
    assert ok is True
    assert errors == []


def test_validate_review_rejects_wrong_area_domain():
    ok, errors = discernment.validate_review({
        "schema": discernment.SCHEMA_VERSION,
        "verdict": "accept",
        "domain": "iskvw",
        "reason": "looks good",
        "risks": [],
        "missing_evidence": [],
        "next_action": "curate",
    }, area="rd_evidence")
    assert ok is False
    assert "bad_domain" in errors


def test_normalize_review_domain_accepts_area_alias_only():
    review = {"domain": "adobe_rescue", "verdict": "accept"}
    normalized = discernment.normalize_review_domain(review, "adobe_rescue")
    assert normalized["domain"] == "adobe"


def test_normalize_review_domain_does_not_cross_domains():
    review = {"domain": "iskvw", "verdict": "accept"}
    normalized = discernment.normalize_review_domain(review, "adobe_rescue")
    assert normalized["domain"] == "iskvw"


def test_cli_review_prompt_reads_json_from_stdin():
    result = subprocess.run(
        [sys.executable, "-m", "cultura.mak_plataforma.tandas",
         "review-prompt", "svg_pipeline"],
        input=json.dumps({"items": [{"claim": "x"}]}),
        capture_output=True, text=True, timeout=20)
    assert result.returncode == 0
    assert "DOMINIO: svg" in result.stdout
    assert "accept|revise|reject" in result.stdout


def test_deterministic_review_revises_missing_evidence():
    review = discernment.deterministic_review(
        "rd_evidence", {"items": [{
            "claim": "A claim without a source",
            "evidence": [],
            "files": [],
            "confidence": "medium",
            "action": "verify_source",
            "reject_reason": "",
        }]})
    assert review["verdict"] == "revise"


def test_deterministic_curation_judge_rejects_model_promotion():
    review = discernment.deterministic_review(
        "iskvw_curation", {"items": [{
            "claim": "la pieza puede entrar al archivo",
            "evidence": ["iskvw/datos/campo.json"],
            "files": ["iskvw/datos/campo.json"],
            "confidence": "high",
            "action": "curate",
            "product": {
                "artwork_reading": "lectura concreta",
                "selection": "serie propia",
                "public_status": "publicada",
            },
        }]})
    assert review["verdict"] == "reject"
    assert any("human signature" in risk for risk in review["risks"])


def test_deterministic_curation_accepts_local_review_status():
    review = discernment.deterministic_review(
        "iskvw_curation", {"items": [{
            "claim": "la pieza requiere lectura del artista",
            "evidence": ["iskvw/datos/campo.json"],
            "files": ["iskvw/datos/campo.json"],
            "confidence": "medium",
            "action": "curate",
            "product": {
                "artwork_reading": "lectura concreta",
                "selection": "serie propia",
                "public_status": "revision_local",
            },
        }]})
    assert review["verdict"] == "accept"


def test_opportunity_review_requires_evidence_and_safe_action():
    review = discernment.deterministic_review(
        "opportunity_radar", {"items": [{
            "claim": "possible artist residency",
            "evidence": [],
            "files": [],
            "confidence": "medium",
            "action": "draft_report",
            "reject_reason": "",
        }]})
    assert review["verdict"] == "revise"
    assert review["missing_evidence"]


def test_deterministic_review_rejects_redacted_or_secret_material():
    review = discernment.deterministic_review(
        "mak_quality", {"items": [{
            "claim": "[redacted] config proves the queue works",
            "evidence": ["~/n8n-local/research.env"],
            "files": ["~/n8n-local/research.env"],
            "confidence": "high",
            "action": "archive",
            "reject_reason": "",
        }]})
    assert review["verdict"] == "reject"
    assert any("secret" in risk or "redacted" in risk for risk in review["risks"])


def test_deterministic_review_revises_action_without_files():
    review = discernment.deterministic_review(
        "adobe_rescue", {"items": [{
            "claim": "adobe bridge exists",
            "evidence": ["README says so"],
            "files": [],
            "confidence": "high",
            "action": "rescue",
            "reject_reason": "",
        }]})
    assert review["verdict"] == "revise"
    assert any("files for" in item for item in review["missing_evidence"])


def test_deterministic_review_revises_weak_negative_claims():
    review = discernment.deterministic_review(
        "tool_archaeology", {"items": [{
            "claim": "no existe herramienta para mapear arquitectura",
            "evidence": [],
            "files": [],
            "confidence": "medium",
            "action": "test",
            "reject_reason": "",
        }]})
    assert review["verdict"] == "revise"
    assert any("negative claim" in item for item in review["missing_evidence"])


def test_review_payload_uses_valid_injected_local_judge():
    def fake_reviewer(_prompt):
        return json.dumps({
            "schema": discernment.SCHEMA_VERSION,
            "verdict": "accept",
            "domain": "repo",
            "reason": "tool path and evidence are present",
            "risks": [],
            "missing_evidence": [],
            "next_action": "append accepted items to ledger",
        })

    review, meta = discernment.review_payload(
        "tool_archaeology", {"items": []}, reviewer=fake_reviewer)
    assert review["verdict"] == "accept"
    assert meta == {"reviewer": "ollama", "fallback": False}


def test_review_payload_falls_back_when_local_judge_breaks():
    def broken(_prompt):
        raise RuntimeError("ollama down")

    review, meta = discernment.review_payload(
        "svg_pipeline", {"items": []}, reviewer=broken)
    assert review["verdict"] == "reject"
    assert meta["reviewer"] == "deterministic"
    assert meta["fallback"] is True


def test_invalid_ollama_acceptance_downgrades_to_revise():
    def wrong_domain(_prompt):
        return json.dumps({
            "schema": discernment.SCHEMA_VERSION,
            "verdict": "accept",
            "domain": "svg",
            "reason": "looks fine",
            "risks": [],
            "missing_evidence": [],
            "next_action": "append",
        })

    review, meta = discernment.review_payload(
        "adobe_rescue", {"items": [{
            "claim": "adobe bridge exists",
            "evidence": ["tools/adobe_panel/README.md"],
            "files": ["tools/adobe_panel/README.md"],
            "confidence": "high",
            "action": "rescue",
            "reject_reason": "",
        }]}, reviewer=wrong_domain)
    assert review["verdict"] == "revise"
    assert "valid local review" in review["missing_evidence"]
    assert meta["fallback"] is True


def test_ingest_accepts_only_after_local_review(tmp_path):
    common = tmp_path / "common_ledger.jsonl"

    def fake_reviewer(_prompt):
        return json.dumps({
            "schema": discernment.SCHEMA_VERSION,
            "verdict": "accept",
            "domain": "repo",
            "reason": "existing tool is named",
            "risks": [],
            "missing_evidence": [],
            "next_action": "append accepted items to ledger",
        })

    payload = {"items": [{
        "claim": "existing tool should be reused",
        "evidence": ["tools/contexto_repo.py"],
        "files": ["tools/contexto_repo.py"],
        "confidence": "high",
        "action": "reuse",
        "reject_reason": "",
    }]}
    result = tandas.ingest_result(
        payload, "tool_archaeology", common_path=str(common),
        source="watsonx", reviewer=fake_reviewer)
    rows = [json.loads(line) for line in common.read_text(encoding="utf-8").splitlines()]
    assert result["ok"] is True
    assert result["items"] == 1
    assert rows[0]["type"] == "decision"
    assert rows[1]["type"] == "evidence"


def test_ingest_promotes_verified_opportunity_to_pending_review_ledger(tmp_path):
    common = tmp_path / "common_ledger.jsonl"

    def fake_reviewer(_prompt):
        return json.dumps({
            "schema": discernment.SCHEMA_VERSION,
            "verdict": "accept",
            "domain": "opportunities",
            "reason": "official source and bounded next action",
            "risks": [],
            "missing_evidence": [],
            "next_action": "append accepted items to ledger",
        })

    payload = {"items": [{
        "claim": "artist opportunity requires current source check",
        "evidence": ["official source"],
        "files": ["cultura/mak_vigia/fuentes.json"],
        "confidence": "high",
        "action": "verify_source",
        "reject_reason": "",
        "format": "oportunidad",
        "evidence_kind": "official_source",
        "product": {"opportunity": "residency", "eligibility": "artist",
                    "deadline": "unknown", "source": "official",
                    "next_action": "verify", "risk": "unknown"},
    }]}
    result = tandas.ingest_result(
        payload, "opportunity_radar", common_path=str(common),
        source="watsonx", reviewer=fake_reviewer, strict_product=True)
    rows = [json.loads(line) for line in common.read_text(encoding="utf-8").splitlines()]
    assert result["status"] == "accepted"
    assert rows[-1]["domain"] == "opportunities"


def test_ingest_rejects_without_appending_provider_facts(tmp_path):
    common = tmp_path / "common_ledger.jsonl"
    payload = {"items": [{
        "claim": "RD claim with no source",
        "evidence": [],
        "files": [],
        "confidence": "medium",
        "action": "verify_source",
        "reject_reason": "",
    }]}
    result = tandas.ingest_result(
        payload, "rd_evidence", common_path=str(common),
        source="aws", use_ollama=False)
    rows = [json.loads(line) for line in common.read_text(encoding="utf-8").splitlines()]
    assert result["ok"] is False
    assert result["status"] == "revise"
    assert len(rows) == 1
    assert rows[0]["type"] == "reject"


def test_cli_ingest_deterministic_mode(tmp_path):
    common = tmp_path / "common_ledger.jsonl"
    payload = {"items": [{
        "claim": "adobe bridge path exists",
        "evidence": ["docs/CONTRAPORTADAS_SUPLEMENTOS_RD.md"],
        "files": ["docs/CONTRAPORTADAS_SUPLEMENTOS_RD.md"],
        "confidence": "medium",
        "action": "rescue",
        "reject_reason": "",
        "product": {"bridge": "illustrator", "installation_evidence": "docs/CONTRAPORTADAS_SUPLEMENTOS_RD.md", "rescue_action": "reuse"},
    }]}
    result = subprocess.run(
        [sys.executable, "-m", "cultura.mak_plataforma.tandas",
         "ingest", "adobe_rescue", "--provider", "aws",
         "--common-ledger", str(common), "--no-ollama"],
        input=json.dumps(payload), capture_output=True, text=True, timeout=20)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["status"] == "accepted"
