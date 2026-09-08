"""Direct-call tests for `flujo.web.hub.HubRequestHandler` private endpoint
methods -- the pattern already used by tests/test_hub_comandos.py and
tests/test_rd_informe.py: instantiate via `__new__` (skips
BaseHTTPRequestHandler.__init__, so no socket opens) and call the method the
route dispatches to directly.

This file does not touch tests/test_hub_*.py or tests/test_mak_hub_*.py
(another agent's files); it adds new coverage for endpoints those files do
not exercise yet: agent roles/delegation, automatizaciones (gh absent), show
kit, portafolio, MAK box status, svg state rules, safe-command allowlisting,
research job listing, and the datadrop listing.

Several of these assert the repo's "absence is named, not read as health"
doctrine: `_get_automatizaciones` without `gh`, `_get_mak` without
FLUJO_MAK_URL, `_get_portafolio` without its manifest, `_get_research_jobs`
without a registry -- none of them may report success or fabricate data.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from flujo.web.hub import HubRequestHandler


def _handler(root: Path) -> HubRequestHandler:
    h = HubRequestHandler.__new__(HubRequestHandler)
    h.root = root
    return h


# --------------------------------------------------------------- agent roles / delegate

def test_agents_roles_are_well_formed():
    h = _handler(Path("."))
    roles = h._get_agents_roles()["roles"]
    assert len(roles) >= 4
    for r in roles:
        for field in ("id", "name", "short", "focus", "prompt_template"):
            assert field in r and r[field]
        assert "{task}" in r["prompt_template"]


def test_delegate_fills_the_template_with_the_task():
    h = _handler(Path("."))
    out = h._handle_delegate({"role_id": "pipeline", "task": "arreglar el CLI"})
    assert out["role"]["id"] == "pipeline"
    assert "arreglar el CLI" in out["prompt"]
    assert out["task"] == "arreglar el CLI"


def test_delegate_falls_back_to_the_first_role_for_an_unknown_id():
    h = _handler(Path("."))
    out = h._handle_delegate({"role_id": "no-existe", "task": "x"})
    assert out["role"]["id"] == h._get_agents_roles()["roles"][0]["id"]


def test_delegate_supplies_a_default_task_when_none_is_given():
    h = _handler(Path("."))
    out = h._handle_delegate({"role_id": "pipeline"})
    assert out["task"]


# --------------------------------------------------------------- automatizaciones (gh doctrine)

def test_gh_queue_without_gh_says_so_instead_of_looking_empty(monkeypatch, tmp_path: Path):
    """An empty `cola: []` reads as 'nothing pending'. Without `gh` on PATH
    the endpoint must say it could not check, not claim there is nothing."""
    monkeypatch.setattr("shutil.which", lambda name: None)
    h = _handler(tmp_path)
    out = h._get_automatizaciones()
    assert out["disponible"] is False
    assert out["cola"] == []
    assert "gh" in out["motivo"]


def test_gh_queue_reports_gh_failure_reason(monkeypatch, tmp_path: Path):
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/gh")

    class _Fail:
        returncode = 1
        stdout = ""
        stderr = "error: not authenticated\n"

    monkeypatch.setattr("subprocess.run", lambda *a, **k: _Fail())
    h = _handler(tmp_path)
    out = h._get_automatizaciones()
    assert out["disponible"] is False
    assert "not authenticated" in out["motivo"]


# --------------------------------------------------------------- show kit / portafolio

def test_show_kit_on_an_empty_repo_reports_zero_without_crashing(tmp_path: Path):
    h = _handler(tmp_path)
    out = h._get_show_kit()
    assert out["setlist"] == []
    assert out["cues"] == []
    assert out["resumen"]["temas"] == 0


def test_portafolio_missing_manifest_names_the_missing_file(tmp_path: Path):
    h = _handler(tmp_path)
    out = h._get_portafolio()
    assert out["proyectos"] == []
    assert "proyectos.json" in out["error"]


def test_portafolio_reads_the_real_manifest(tmp_path: Path):
    manifest = tmp_path / "tools" / "portfolio"
    manifest.mkdir(parents=True)
    (manifest / "proyectos.json").write_text(json.dumps({
        "titulo": "iskvw", "proyectos": [
            {"id": "p1", "nombre": "Uno", "linea": "laser", "estado": "publicado"},
        ],
    }), encoding="utf-8")
    h = _handler(tmp_path)
    out = h._get_portafolio()
    assert out["titulo"] == "iskvw"
    assert out["proyectos"][0]["id"] == "p1"
    assert out["prototipo_generado"] is False


# --------------------------------------------------------------- MAK box status

def test_mak_status_without_url_configured_says_so(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("FLUJO_MAK_URL", raising=False)
    monkeypatch.setenv("FLUJO_MAK_COMMON_LEDGER", str(tmp_path / "common.jsonl"))
    monkeypatch.setenv("FLUJO_MAK_BATCH_LEDGER", str(tmp_path / "batch.jsonl"))
    h = _handler(tmp_path)
    out = h._get_mak()
    assert out["disponible"] is False
    assert out["configurado"] is False
    assert "FLUJO_MAK_URL" in out["error"]


def test_mak_status_with_unreachable_url_reports_the_error(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("FLUJO_MAK_URL", "http://127.0.0.1:1")  # nobody listens here
    monkeypatch.setenv("FLUJO_MAK_COMMON_LEDGER", str(tmp_path / "common.jsonl"))
    monkeypatch.setenv("FLUJO_MAK_BATCH_LEDGER", str(tmp_path / "batch.jsonl"))
    h = _handler(tmp_path)
    out = h._get_mak()
    assert out["disponible"] is False
    assert out["configurado"] is True
    assert out["error"]


def test_mak_tandas_on_missing_ledgers_reports_zero_rows(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("FLUJO_MAK_COMMON_LEDGER", str(tmp_path / "no_existe_common.jsonl"))
    monkeypatch.setenv("FLUJO_MAK_BATCH_LEDGER", str(tmp_path / "no_existe_batch.jsonl"))
    h = _handler(tmp_path)
    out = h._get_mak_tandas()
    assert out["common_rows"] == 0
    assert out["batch_rows"] == 0
    assert out["pending_human"] == 0


def test_mak_tandas_counts_pending_human_and_rejections(monkeypatch, tmp_path: Path):
    common = tmp_path / "common.jsonl"
    rows = [
        {"domain": "cultura", "source": "groq:model", "type": "evidence"},
        {"domain": "cultura", "source": "groq:model", "type": "reject", "reject_reason": "no aplica"},
        {"domain": "cultura", "source": "groq:model", "type": "decision",
         "metadata": {"queue_status": "pending_human", "next_action": "revisar a mano"}},
    ]
    common.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    monkeypatch.setenv("FLUJO_MAK_COMMON_LEDGER", str(common))
    monkeypatch.setenv("FLUJO_MAK_BATCH_LEDGER", str(tmp_path / "batch.jsonl"))
    h = _handler(tmp_path)
    out = h._get_mak_tandas()
    assert out["common_rows"] == 3
    assert out["accepted"] == 1
    assert out["rejected_or_revise"] == 1
    assert out["pending_human"] == 1
    assert out["by_provider"] == {"groq": 3}


# --------------------------------------------------------------- svg state rules

def test_svg_state_defaults_to_the_fallback_without_a_rules_file(monkeypatch, tmp_path: Path):
    monkeypatch.setattr("flujo.web.hub.repo_root", lambda: tmp_path)
    h = _handler(tmp_path)
    assert h._estado_svg("svg/cualquiera/pieza.svg") == "borrador"


def test_svg_state_the_last_matching_rule_wins(monkeypatch, tmp_path: Path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "svg_estados.json").write_text(json.dumps({
        "por_defecto": "borrador",
        "reglas": [
            {"ruta": "svg/suplementos_rd/", "estado": "en_revision"},
            {"ruta": "svg/suplementos_rd/09_contraportadas_dark/", "estado": "aprobado"},
        ],
    }), encoding="utf-8")
    monkeypatch.setattr("flujo.web.hub.repo_root", lambda: tmp_path)
    h = _handler(tmp_path)
    assert h._estado_svg("svg/suplementos_rd/otro.svg") == "en_revision"
    assert h._estado_svg("svg/suplementos_rd/09_contraportadas_dark/x.svg") == "aprobado"


def test_list_svg_works_on_a_repo_without_svg_dir(tmp_path: Path):
    h = _handler(tmp_path)
    out = h._list_svg_works()
    assert out == {"groups": {}, "count": 0, "root": "svg", "error": "no svg dir"}


def test_list_svg_works_groups_and_classifies_files(monkeypatch, tmp_path: Path):
    grupo = tmp_path / "svg" / "suplementos_rd"
    grupo.mkdir(parents=True)
    (grupo / "editable_impulso.svg").write_text("<svg/>", encoding="utf-8")
    monkeypatch.setattr("flujo.web.hub.repo_root", lambda: tmp_path)
    h = _handler(tmp_path)
    out = h._list_svg_works()
    assert out["count"] == 1
    assert "suplementos_rd" in out["groups"]
    assert out["groups"]["suplementos_rd"][0]["kind"] == "editable"


# --------------------------------------------------------------- real_parse_pedido / simple_parse

def test_real_parse_pedido_on_empty_text_is_an_error():
    h = _handler(Path("."))
    out = h._real_parse_pedido("   ")
    assert out["tipo"] == "desconocido"
    assert "error" in out


def test_real_parse_pedido_matches_known_formats():
    h = _handler(Path("."))
    out = h._real_parse_pedido("necesito un flyer para el evento de creamfields")
    assert out["tipo"] == "flyer"
    assert out["formato"] == "evt_flyer_fisico_10x14"
    assert out["match"] is True
    assert out["area"] == "eventos"


def test_simple_parse_is_a_pure_fallback():
    h = _handler(Path("."))
    assert h._simple_parse("necesito una etiqueta")["tipo"] == "etiqueta"
    assert h._simple_parse("algo sin match")["tipo"] == "desconocido"


# --------------------------------------------------------------- jobs listing

def test_list_jobs_api_on_an_empty_workspace(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("flujo.paths.repo_root", lambda: tmp_path)
    monkeypatch.setattr("flujo.jobs.job.repo_root", lambda: tmp_path)
    (tmp_path / "jobs").mkdir()
    h = _handler(tmp_path)
    out = h._list_jobs_api()
    assert out["count"] == 0
    assert out["jobs"] == []
    assert out["connected"] is True


# --------------------------------------------------------------- safe command allowlist (security)

@pytest.mark.parametrize("arg", ["--json", "--limit", "-v", "positional", "job123"])
def test_arg_es_seguro_accepts_plain_arguments(arg):
    assert HubRequestHandler._arg_es_seguro(arg) is True


@pytest.mark.parametrize("arg", [
    "", "--rm", "-x",              # flag not in the allowlist
    "/etc/passwd", "~/secret", "..\\..\\x", "../escape",
    "C:\\Windows", "a;rm -rf /", "a|b", "a`b`", "a$b", "a>b", "a<b",
])
def test_arg_es_seguro_rejects_escapes_and_unknown_flags(arg):
    assert HubRequestHandler._arg_es_seguro(arg) is False


def test_is_safe_cmd_accepts_an_allowlisted_prefix_with_safe_args():
    h = _handler(Path("."))
    assert h._is_safe_cmd("flujo job list --limit") is True


def test_is_safe_cmd_rejects_a_prefix_that_only_starts_the_same_way():
    """`startswith` alone would let `flujo version-not-safe` through."""
    h = _handler(Path("."))
    assert h._is_safe_cmd("flujo version-not-safe") is False


def test_is_safe_cmd_rejects_an_unlisted_command():
    h = _handler(Path("."))
    assert h._is_safe_cmd("flujo package") is False
    assert h._is_safe_cmd("") is False


def test_is_safe_cmd_rejects_an_escaping_argument_even_on_a_safe_prefix():
    h = _handler(Path("."))
    assert h._is_safe_cmd("flujo job prepare /home/user/.ssh") is False


def test_is_safe_cmd_rejects_an_overlong_command():
    h = _handler(Path("."))
    assert h._is_safe_cmd("flujo version " + "x" * 400) is False


def test_run_safe_command_refuses_a_non_whitelisted_command(tmp_path: Path):
    h = _handler(tmp_path)
    out = h._run_safe_command("rm -rf /")
    assert "error" in out
    assert "not whitelisted" in out["error"]


def test_run_safe_command_actually_runs_an_allowlisted_command(tmp_path: Path):
    h = _handler(tmp_path)
    out = h._run_safe_command("flujo version")
    assert out["success"] is True
    assert out["returncode"] == 0


# --------------------------------------------------------------- research jobs listing

def _seed_registry(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE domain_adapters (id INTEGER PRIMARY KEY, "
                     "slug TEXT, label TEXT, description TEXT, "
                     "input_examples TEXT, source_policy TEXT, constraint_policy TEXT)")
        conn.execute("CREATE TABLE research_jobs (id INTEGER PRIMARY KEY, "
                     "adapter_id INTEGER, question TEXT, domain TEXT, status TEXT, "
                     "next_process TEXT, created_at TEXT)")
        conn.execute("CREATE TABLE job_steps (id INTEGER PRIMARY KEY, job_id INTEGER, "
                     "step_order INTEGER, process_key TEXT, input_semantics TEXT, "
                     "output_semantics TEXT, status TEXT, provider_policy TEXT)")
        conn.execute("CREATE TABLE job_relations (id INTEGER PRIMARY KEY, job_id INTEGER, "
                     "relation_type TEXT, from_object TEXT, to_object TEXT, rationale TEXT)")
        conn.execute("INSERT INTO domain_adapters VALUES (1,'curatoria','Curatoria','d','e','s','c')")
        conn.execute("INSERT INTO research_jobs VALUES "
                     "(1, 1, 'una pregunta', 'cultura', 'done', 'ninguno', '2026-08-01')")
        conn.execute("INSERT INTO job_steps VALUES (1, 1, 0, 'buscar', 'in', 'out', 'done', 'p')")


def test_get_research_jobs_without_a_registry(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("MAK_RESEARCH_REGISTRY", str(tmp_path / "no_existe.sqlite"))
    h = _handler(tmp_path)
    out = h._get_research_jobs()
    assert out == {"available": False, "jobs": [], "count": 0}


def test_get_research_jobs_lists_seeded_jobs(monkeypatch, tmp_path: Path):
    db = tmp_path / "registry.sqlite"
    _seed_registry(db)
    monkeypatch.setenv("MAK_RESEARCH_REGISTRY", str(db))
    h = _handler(tmp_path)
    out = h._get_research_jobs()
    assert out["available"] is True
    assert out["count"] == 1
    assert out["jobs"][0]["question"] == "una pregunta"
    assert out["jobs"][0]["done_steps"] == 1


def test_get_research_job_rejects_a_non_positive_id():
    h = _handler(Path("."))
    with pytest.raises(ValueError):
        h._get_research_job(0)


def test_get_research_job_returns_the_full_record(monkeypatch, tmp_path: Path):
    db = tmp_path / "registry.sqlite"
    _seed_registry(db)
    monkeypatch.setenv("MAK_RESEARCH_REGISTRY", str(db))
    h = _handler(tmp_path)
    out = h._get_research_job(1)
    assert out["available"] is True
    assert out["job"]["question"] == "una pregunta"
    assert len(out["job"]["steps"]) == 1


def test_get_research_job_raises_for_an_unknown_id(monkeypatch, tmp_path: Path):
    db = tmp_path / "registry.sqlite"
    _seed_registry(db)
    monkeypatch.setenv("MAK_RESEARCH_REGISTRY", str(db))
    h = _handler(tmp_path)
    with pytest.raises(ValueError):
        h._get_research_job(999)


def test_create_research_job_rejects_an_empty_question():
    h = _handler(Path("."))
    out = h._create_research_job({"question": "   "})
    assert out["ok"] is False
    assert "question" in out["error"]


def test_create_research_job_rejects_an_overlong_question():
    h = _handler(Path("."))
    out = h._create_research_job({"question": "x" * 2001})
    assert out["ok"] is False


# --------------------------------------------------------------- datadrops listing

def test_list_datadrops_on_an_empty_workspace(tmp_path: Path, monkeypatch):
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    monkeypatch.setattr("flujo.web.hub.datadrops_dir", lambda: tmp_path)
    h = _handler(tmp_path)
    out = h._list_datadrops()
    assert out["datadrops"] == []
    assert out["count"] == 0
    assert out["pending_incoming"] == 0


def test_list_datadrops_reports_raw_drops_and_pending_incoming(tmp_path: Path, monkeypatch):
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    (incoming / "foto.jpg").write_bytes(b"fake")
    (incoming / "notes.txt").write_bytes(b"not an image")
    drop = tmp_path / "2026-08-01_pieza"
    drop.mkdir()
    monkeypatch.setattr("flujo.web.hub.datadrops_dir", lambda: tmp_path)
    h = _handler(tmp_path)
    out = h._list_datadrops()
    assert out["count"] == 1
    assert out["datadrops"][0]["note"] == "no manifest (raw)"
    assert out["pending_incoming"] == 1


# --------------------------------------------------------------- rd db (privacy allowlist)

def test_get_rd_db_on_an_empty_repo_degrades_without_crashing(tmp_path: Path):
    h = _handler(tmp_path)
    out = h._get_rd_db()
    assert isinstance(out, dict)
    assert out.get("productoras", []) == []


# --------------------------------------------------------------- version / status / dashboard

def test_get_version_returns_the_real_package_version():
    h = _handler(Path("."))
    v = h._get_version()
    from flujo.version import get_version
    assert v == get_version()


def test_get_status_reports_root_and_operational_ledger(tmp_path: Path):
    h = _handler(tmp_path)
    out = h._get_status()
    assert out["status"] == "ok"
    assert out["root"] == str(tmp_path)
    assert "operational" in out


def test_get_dashboard_summary_on_an_empty_workspace(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("flujo.paths.repo_root", lambda: tmp_path)
    monkeypatch.setattr("flujo.dashboard.scoring.repo_root", lambda: tmp_path)
    h = _handler(tmp_path)
    out = h._get_dashboard_summary()
    assert isinstance(out, dict)
