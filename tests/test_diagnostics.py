import json
import subprocess
import sys
from pathlib import Path

from flujo.diagnostics import (
    build_diagnostic_report,
    redact_text,
    render_markdown,
    render_route_markdown,
    route_idea,
)


ROOT = Path(__file__).resolve().parents[1]


def test_route_idea_selects_cultura_with_research_support():
    route = route_idea(
        "quiero hacer scraping de manuales de cultivo de plantas para una obra 3D",
        root=ROOT,
    )
    assert route["primary_domain"] == "cultura"
    assert "research" in route["support_domains"]
    assert route["contract"].endswith("cultura.md")
    assert "WIN raw archive" in route["do_not_read"]


def test_route_idea_explicit_area_wins():
    route = route_idea("mi sitio web esta caido", area="portfolio", root=ROOT)
    assert route["primary_domain"] == "portfolio"
    assert route["suggested_branch"].startswith("portfolio/")


def test_redact_text_hides_secrets_email_and_home():
    text = "token=abc123 password=secret user@example.com /home/mak/flujo"
    safe = redact_text(text)
    assert "abc123" not in safe
    assert "secret" not in safe
    assert "user@example.com" not in safe
    assert "/home/mak" not in safe


def test_report_is_bounded_and_markdown_copyable(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='fixture'\n", encoding="utf-8")
    report = build_diagnostic_report(
        root=tmp_path,
        area="research",
        idea="scraping de manuales",
        operation="source_search",
        error="Authorization: Bearer topsecret user@example.com",
        command="python scraper.py --token=secret",
        expected="un corpus",
        observed="HTTP 401",
    )
    text = render_markdown(report)
    assert report["schema"] == "mak-diagnostic-v1"
    assert report["area"] == "research"
    assert "topsecret" not in text
    assert "user@example.com" not in text
    assert "WIN raw archive" in text
    assert "source_search" in text
    assert render_route_markdown(report["route"]).startswith("# MAK context route")


def test_json_route_script_works_without_package_install():
    proc = subprocess.run(
        [sys.executable, "tools/route_idea.py", "mi portafolio web esta caido", "--format", "json"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["primary_domain"] == "portfolio"
