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
                    "AZURE_DEPLOYMENT": ["az-deployment"],
                    "OLLAMA_MODEL": ["ollama-llama"],
                    "PROVIDERS_ORDER": ["groq,cerebras,azure,ollama"],
                })
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                self.assertIn("GROQ_MODEL=nuevo-modelo", content)
                self.assertIn("CEREBRAS_MODEL=cerebras-x", content)
                self.assertEqual(os.environ["GROQ_MODEL"], "nuevo-modelo")
                self.assertEqual(os.environ["PROVIDERS_ORDER"], "groq,cerebras,azure,ollama")
            finally:
                interfaz.ENV_FILE = old_env_file


if __name__ == "__main__":
    unittest.main()
