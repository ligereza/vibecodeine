"""Tests for projects/cultura/corpus_olvido/corpus_olvido.py.

Builds a THROWAWAY git repo in tmp_path with 3 commits to a fake
context/LAST_HANDOFF.md, distinct headers, and runs the extractor against
it. Never touches the real repo history.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "projects" / "cultura" / "corpus_olvido" / "corpus_olvido.py"

sys.path.insert(0, str(SCRIPT.parent))
import corpus_olvido  # noqa: E402


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    env_args = ["git", *args]
    return subprocess.run(
        env_args,
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=True,
    )


def _init_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")


def _commit_handoff(repo: Path, texto: str, mensaje: str, fecha: str) -> str:
    (repo / "context").mkdir(exist_ok=True)
    (repo / "context" / "LAST_HANDOFF.md").write_text(texto, encoding="utf-8")
    _git(repo, "add", "context/LAST_HANDOFF.md")
    env = {
        "GIT_AUTHOR_DATE": fecha,
        "GIT_COMMITTER_DATE": fecha,
    }
    subprocess.run(
        ["git", "commit", "-q", "-m", mensaje],
        cwd=str(repo),
        env={**_base_env(), **env},
        check=True,
    )
    sha = _git(repo, "rev-parse", "--short", "HEAD").stdout.strip()
    return sha


def _base_env():
    import os

    return dict(os.environ)


@pytest.fixture
def repo_falso(tmp_path):
    repo = tmp_path / "repo_falso"
    _init_repo(repo)

    header_1 = "# Estado sesion 1\n\ndone: nada\ndoing: arrancando\n"
    header_2 = "# Estado sesion 2\n\ndone: paso 1\ndoing: paso 2\n"
    header_3 = "# Estado sesion 3\n\ndone: todo\ndoing: nada mas\n"

    contenido_1 = header_1 + "\n## Detalle\n\nblah blah\n"
    contenido_2 = header_2 + "\n## Detalle\n\nblah blah 2\n"
    contenido_3 = header_3 + "\n## Detalle\n\nblah blah 3\n"

    sha1 = _commit_handoff(repo, contenido_1, "sesion 1", "2026-01-01T10:00:00")
    sha2 = _commit_handoff(repo, contenido_2, "sesion 2", "2026-01-02T10:00:00")
    sha3 = _commit_handoff(repo, contenido_3, "sesion 3", "2026-01-03T10:00:00")

    return {
        "repo": repo,
        "shas": [sha1, sha2, sha3],
        "headers": [header_1.strip(), header_2.strip(), header_3.strip()],
    }


def test_orden_oldest_first(repo_falso):
    capas = corpus_olvido.construir_capas(repo_falso["repo"])
    assert len(capas) == 3
    fechas = [c.fecha_iso for c in capas]
    assert fechas == sorted(fechas)
    assert capas[0].sha_corto == repo_falso["shas"][0]
    assert capas[-1].sha_corto == repo_falso["shas"][2]


def test_fragmentos_literales(repo_falso):
    capas = corpus_olvido.construir_capas(repo_falso["repo"])
    for capa, header_esperado in zip(capas, repo_falso["headers"]):
        assert capa.header == header_esperado


def test_sha_y_fecha_presentes(repo_falso):
    capas = corpus_olvido.construir_capas(repo_falso["repo"])
    for capa in capas:
        assert capa.sha_corto
        assert capa.fecha_iso
        assert "T" in capa.fecha_iso  # ISO 8601


def test_determinismo(repo_falso):
    capas_1 = corpus_olvido.construir_capas(repo_falso["repo"])
    capas_2 = corpus_olvido.construir_capas(repo_falso["repo"])
    render_1 = corpus_olvido.render_corpus(capas_1)
    render_2 = corpus_olvido.render_corpus(capas_2)
    assert render_1 == render_2


def test_commit_sin_archivo_se_salta(tmp_path):
    repo = tmp_path / "repo_sin_archivo_a_veces"
    _init_repo(repo)

    # commit 1: archivo presente
    header_1 = "# Sesion A\n\ndone: x\n"
    sha1 = _commit_handoff(repo, header_1 + "\n## Detalle\n\ny\n", "c1", "2026-02-01T10:00:00")

    # commit 2: se borra el archivo (deberia saltarse en el corpus)
    (repo / "context" / "LAST_HANDOFF.md").unlink()
    _git(repo, "add", "-A")
    subprocess.run(
        ["git", "commit", "-q", "-m", "c2 borra"],
        cwd=str(repo),
        env={**_base_env(), "GIT_AUTHOR_DATE": "2026-02-02T10:00:00", "GIT_COMMITTER_DATE": "2026-02-02T10:00:00"},
        check=True,
    )

    # commit 3: se re-crea el archivo
    header_3 = "# Sesion C\n\ndone: z\n"
    sha3 = _commit_handoff(repo, header_3 + "\n## Detalle\n\nw\n", "c3", "2026-02-03T10:00:00")

    capas = corpus_olvido.construir_capas(repo)
    shas = [c.sha_corto for c in capas]
    assert sha1 in shas
    assert sha3 in shas
    assert len(capas) == 2


def test_render_incluye_sha_y_fecha_por_fragmento(repo_falso):
    capas = corpus_olvido.construir_capas(repo_falso["repo"])
    texto = corpus_olvido.render_corpus(capas)
    for capa in capas:
        assert capa.sha_corto in texto
        assert capa.fecha_iso in texto


def test_cli_end_to_end(repo_falso, tmp_path):
    salida = tmp_path / "corpus_out.md"
    rc = corpus_olvido.main(
        [
            "--repo",
            str(repo_falso["repo"]),
            "--salida",
            str(salida),
        ]
    )
    assert rc == 0
    assert salida.exists()
    texto = salida.read_text(encoding="utf-8")
    assert "Capas: 3" in texto
