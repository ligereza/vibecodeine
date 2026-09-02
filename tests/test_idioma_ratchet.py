# -*- coding: utf-8 -*-
"""Ratchet: the language rule finally gets a measurement that does not rot.

Rule (2026-07-31). Concrete cause: the repository language policy said code and comments are
written in English, but the tree was measured 2026-07-30 at hundreds of Python
files carrying Spanish comments -- and NOTHING re-measured it, so the number
was already stale the day after. That gap is operational, not cosmetic: an
agent reads the rule, searches in English, finds nothing, and concludes the
thing does not exist -- then rebuilds it or reports it missing.

What this ratchet does:

- `tools/idioma.py` classifies the COMMENTS AND DOCSTRINGS of every tracked
  Python file (never identifiers, never product strings) as es/en/mixed/none
  with a transparent offline heuristic (documented in that module's docstring).
- The change ratchet also checks newly declared identifiers in changed and
  untracked Python files against HEAD. Existing declarations remain compatible.
- `tests/fixtures/idioma_baseline.txt` pins the measured set of files carrying
  Spanish (verdict es or mixed) at the moment the ratchet was born:
  426 files (388 es + 38 mixed), against 96 English, on 2026-07-31.
- This test fails ONLY when a file outside that set starts carrying Spanish
  comments -- a new file, or an English file that gained Spanish. It NEVER
  fails when the count goes down: cleaning is always welcome, and a cleaned
  file may keep its (now unused) baseline entry until someone regenerates.

How to lower the pin after cleaning files (do it, the ratchet only tightens
by hand):

    python3 tools/idioma.py --baseline > tests/fixtures/idioma_baseline.txt

What this ratchet deliberately does NOT do: demand renames. File names that a
cron line or a systemd unit already invokes are load-bearing; the rule (see
docs/GLOSSARY.md) is that NEW comments are English, not that the machine that
works gets broken. Excluded zones follow tests/test_higiene_docs.py: archives
(DEAD_ZONE) are history and vendorized third-party code (FOREIGN_ZONE) is not
ours to accuse. The measurement reads `git ls-files`, never the disk, so an
uncommitted scratch file cannot distort it -- which also means a NEW offender
is invisible until `git add`; add first, then run this.

Retirement: when the tree measures zero files carrying Spanish comments and
the baseline is empty, this becomes a plain "no Spanish comments" check.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "tools"))

import idioma  # noqa: E402

BASELINE = Path(__file__).resolve().parent / "fixtures" / "idioma_baseline.txt"


def _baseline_set() -> set[str]:
    lines = BASELINE.read_text(encoding="utf-8").splitlines()
    return {ln.strip() for ln in lines if ln.strip() and not ln.startswith("#")}


def _measured():
    try:
        return idioma.measure(_REPO)
    except RuntimeError as exc:  # not a usable git checkout
        pytest.skip(str(exc))


def test_no_new_file_carries_spanish_comments():
    """The ratchet itself: Spanish-carrying files may only leave the set."""
    baseline = _baseline_set()
    assert baseline, "empty baseline: regenerate with tools/idioma.py --baseline"
    measured = set(_measured()["spanish_files"])
    new_offenders = sorted(measured - baseline)
    assert not new_offenders, (
        "New file(s) carrying Spanish comments or docstrings. The rule "
        "(docs/GLOSSARY.md): NEW code is written in English -- "
        "comments and docstrings included -- because a Spanish term inside an "
        "English system becomes unsearchable. Product strings a human reads "
        "stay in correct Spanish with diacritics; this ratchet never counts "
        "them, only comments/docstrings (see tools/idioma.py for the exact "
        "heuristic). Fix: rewrite the flagged comments in English. If you "
        "instead CLEANED files, lower the pin with:\n"
        "  python3 tools/idioma.py --baseline > tests/fixtures/idioma_baseline.txt\n"
        "New offenders:\n  " + "\n  ".join(new_offenders)
    )
    assert not idioma.new_spanish_comment_files(_REPO)
    assert not idioma.new_spanish_identifiers(_REPO)


def test_change_ratchet_detects_new_declared_spanish_identifier(monkeypatch):
    source = "def calcular_ruta():\n    return 1\n"
    monkeypatch.setattr(idioma, "changed_python_files",
                        lambda _root: ["probe.py"])
    monkeypatch.setattr(idioma, "_read_text", lambda _path: source)
    monkeypatch.setattr(idioma, "_source_at_head", lambda *_args: None)
    assert idioma.new_spanish_identifiers(_REPO) == [
        ("probe.py", "calcular_ruta")]


def test_change_ratchet_allows_legacy_names_and_product_strings(monkeypatch):
    source = (
        'MESSAGE = "Genera la cotizacion para el cliente"\n'
        "def registrar():\n    return MESSAGE\n"
    )
    monkeypatch.setattr(idioma, "changed_python_files",
                        lambda _root: ["legacy.py"])
    monkeypatch.setattr(idioma, "_read_text", lambda _path: source)
    monkeypatch.setattr(idioma, "_source_at_head", lambda *_args: source)
    assert idioma.new_spanish_identifiers(_REPO) == []


def test_shrinking_is_not_punished():
    """The measured set never has to fill the baseline: only growth fails."""
    baseline = _baseline_set()
    measured = set(_measured()["spanish_files"])
    # Cleaned files (in baseline, no longer offending) are legal by design.
    # This asserts the relation the ratchet depends on, nothing more.
    assert measured - baseline == measured.difference(baseline)
    assert len(measured & baseline) <= len(baseline)


# ---------------------------------------------------------------------------
# The instrument itself: pin the heuristic's behaviour on known text, so a
# future edit to the stopword lists cannot silently flip the verdicts the
# ratchet stands on.


def test_classifier_on_known_spanish():
    es, en = idioma.score_text("Genera el informe y lo escribe en la carpeta "
                               "de salida, sin tocar la versión publicada.")
    assert idioma.classify(es, en) == "es", (es, en)


def test_classifier_on_known_english():
    es, en = idioma.score_text("Builds the report and writes it to the output "
                               "directory without touching the published version.")
    assert idioma.classify(es, en) == "en", (es, en)


def test_classifier_needs_evidence():
    # A lone ambiguous word accuses nobody: "de-duplicate" tokenizes to
    # ("de", "duplicate") and "de" is excluded from the stopword lists.
    es, en = idioma.score_text("de-duplicate entries")
    assert idioma.classify(es, en) == "none", (es, en)
    assert idioma.classify(0, 0) == "none"
    assert idioma.classify(1, 0) == "none"


def test_diacritics_are_strong_evidence():
    es, en = idioma.score_text("Versión")
    assert (es, en) == (2, 0)
    assert idioma.classify(es, en) == "es"


def test_product_strings_are_never_counted():
    source = (
        'MENSAJE = "Genera la cotización para el cliente"\n'
        "# builds the quote payload\n"
        'def f():\n    """Return the quote."""\n    return MENSAJE\n'
    )
    text = idioma.comment_and_docstring_text(source)
    assert "cotización" not in text, "a string literal leaked into the measurement"
    es, en = idioma.score_text(text)
    assert idioma.classify(es, en) == "en", (es, en)


def test_docstrings_are_counted():
    source = '"""Convierte el pedido en una cotización lista para enviar."""\n'
    es, en = idioma.score_text(idioma.comment_and_docstring_text(source))
    assert idioma.classify(es, en) == "es", (es, en)


def test_excluded_zones_match_the_house_convention():
    """DEAD_ZONE/FOREIGN_ZONE mirror tests/test_higiene_docs.py on purpose:
    one convention for which files an instrument may accuse.

    The counterpart is a MAK doc ratchet and stayed in MAK when the branches
    separated (2026-09-02), so from FLUJO there is nothing to mirror against.
    This skipped with an ImportError until then, which read as a broken test
    rather than as an absent counterpart. MAK still enforces the equality; the
    skip records where the authority lives instead of hiding it.
    """
    try:
        from test_higiene_docs import ZONA_AJENA, ZONA_MUERTA
    except ModuleNotFoundError:
        pytest.skip(
            "tests/test_higiene_docs.py belongs to MAK; the mirror is "
            "enforced there, on the branch that owns the doc ratchets")

    assert set(idioma.DEAD_ZONE) == set(ZONA_MUERTA)
    assert set(idioma.FOREIGN_ZONE) == set(ZONA_AJENA)


def test_measurement_reads_git_not_the_disk(tmp_path):
    """An uncommitted file must be invisible (lesson from the vendorized
    README incident: ratchets over `git ls-files` and disk walks disagree
    exactly when it hurts)."""
    files = idioma.tracked_python_files(_REPO)
    assert files, "tracked_python_files returned nothing on a real checkout"
    stray = _REPO / "_idioma_stray_probe.py"
    assert not stray.exists()
    try:
        stray.write_text("# comentario en español para la sonda\n", encoding="utf-8")
        assert "_idioma_stray_probe.py" not in idioma.tracked_python_files(_REPO)
    finally:
        stray.unlink()


def test_glossary_fyi_is_soft_and_deterministic():
    """The FYI section must keep working (it prints, it never fails anyone).
    Determinism check: two runs, same answer."""
    a = idioma.glossary_misses(_REPO)
    b = idioma.glossary_misses(_REPO)
    assert a == b
    for name, spread in a:
        assert spread >= 4
