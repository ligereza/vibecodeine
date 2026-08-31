# -*- coding: utf-8 -*-
"""UN handoff, UN README, UNA carpeta de archivo -- comprobado, no pedido.

Correccion del usuario el 2026-07-27: "que lo explique no asegura nada". Un
documento que explica que no hay que leerlo sigue estando ahi para que alguien
lo lea y lo edite. Una nota es una esperanza; un test es una garantia.

No es teorico: este repo llego a tener SIETE documentos de estado compitiendo,
se consolidaron en uno el 2026-07-26, y al dia siguiente habia otra vez tres
sueltos. Se limpio a mano dos veces.

Dos correcciones mas del mismo dia, que ordenan como se escribe un test asi:

- Antes de proteger algo hay que preguntarse si debe existir. `AGENTS.md` se
  archivo por eso: ningun codigo lo leia y yo lo iba a conservar inventandole un
  consumidor. Lo que no tiene uso medido se retira.
- **Nada de umbrales numericos.** La primera version de este archivo exigia
  "<= 8 lineas", que es el mismo error que un `test -gt 600` que ese dia bloqueo
  una publicacion correcta: un numero codifica el estado de hoy. Se comprueba la
  PROPIEDAD -- que no haya un segundo contrato -- y no un tamano.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _versionados():
    r = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True,
                       encoding="utf-8", errors="replace")
    return r.stdout.split() if r.returncode == 0 else []


def _vivos(nombres):
    """Sin lo archivado: la historia puede tener todos los handoffs que quiera."""
    return [n for n in nombres
            if not n.startswith(("_archive/", "docs/handoffs/archive/"))
            and "/legacy_" not in n]


def test_un_solo_handoff_vivo():
    hs = [n for n in _vivos(_versionados())
          if "handoff" in n.lower() and n.endswith(".md")
          and not n.endswith("README.md")
          and "skills/" not in n]
    assert hs == ["context/LAST_HANDOFF.md"], (
        "debe haber UN solo handoff vivo, context/LAST_HANDOFF.md; lo demas se "
        "archiva en docs/handoffs/archive/. Encontrados: " + ", ".join(hs))


def test_un_solo_readme_en_la_raiz():
    # solo .md: `arte-ascii-readme.svg` es la OBRA que se ve como portada, no
    # un segundo readme -- un falso positivo del primer intento de este test.
    raiz = [n for n in _versionados()
            if "/" not in n and n.lower().endswith(".md") and "readme" in n.lower()]
    assert raiz == ["README.md"], raiz


def test_no_hay_dos_carpetas_de_archivo():
    """Habia `.archive/` y `_archive/`: dos lugares para lo mismo es confusion
    por diseno, y la convencion que declara CLAUDE.md es `_archive/`."""
    assert not (REPO / ".archive").exists(), (
        "hay dos carpetas de archivo. La convencion es _archive/legacy_<fecha>/")


def test_no_vuelve_un_segundo_punto_de_entrada():
    """AGENTS.md es el contrato actual y no debe competir con otro handoff."""
    p = REPO / "AGENTS.md"
    if not p.is_file():
        return
    texto = p.read_text(encoding="utf-8", errors="replace")
    assert "Faro operating contract" in texto
    assert "context/LAST_HANDOFF.md" in texto
    assert "The current director is" in texto
