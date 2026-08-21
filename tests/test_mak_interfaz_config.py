#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Movido desde cultura/mak_research/ el 2026-07-30.

Vivia junto al modulo que prueba, o sea FUERA de tests/, y `flujo verify` corre
`pytest tests/`: llevaba trece dias sin ejecutarse una sola vez. El guardian de
un incidente documentado que nunca corre no protege de nada.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cultura" / "mak_research"))

import pytest

# `interfaz` importa fcntl: Linux-only. En CI ubuntu corre; en el Windows
# del usuario se salta, igual que el resto de los tests de MAK.
pytest.importorskip("fcntl", reason="interfaz.py importa fcntl (Linux-only)")

import os
import tempfile
import unittest

import interfaz


class TestInterfazConfig(unittest.TestCase):
    def test_guardar_config_updates_env_file_and_os_environ(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "research.env")
            with open(path, "w", encoding="utf-8") as f:
                f.write("GROQ_MODEL=old\n")
            old_env_file = interfaz.ENV_FILE
            interfaz.ENV_FILE = path  # aislado: NUNCA tocar el research.env real
            try:
                interfaz._guardar_config({
                    "GROQ_MODEL": ["nuevo-modelo"],
                    "CEREBRAS_MODEL": ["cerebras-x"],
                    "GEMINI_MODEL": ["gemini-x"],
                    "OLLAMA_MODEL": ["ollama-llama"],
                    "PROVIDERS_ORDER": ["groq,gemini,ollama"],
                })
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                self.assertIn("GROQ_MODEL=nuevo-modelo", content)
                self.assertIn("CEREBRAS_MODEL=cerebras-x", content)
                self.assertIn("GEMINI_MODEL=gemini-x", content)
                self.assertEqual(os.environ["GROQ_MODEL"], "nuevo-modelo")
                self.assertEqual(os.environ["PROVIDERS_ORDER"], "groq,gemini,ollama")
            finally:
                interfaz.ENV_FILE = old_env_file


if __name__ == "__main__":
    unittest.main()
