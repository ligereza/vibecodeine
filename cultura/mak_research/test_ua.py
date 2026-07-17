import json
import unittest
from unittest.mock import MagicMock, patch

import research_lib


def _resp(payload):
    m = MagicMock()
    m.__enter__.return_value.read.return_value = json.dumps(payload).encode()
    m.__exit__.return_value = False
    return m


class TestUARegression(unittest.TestCase):
    """Cloudflare 403 codigo 1010 bloquea el UA default de urllib.
    Sin el UA custom, groq/cerebras mueren en silencio (2026-07-15)."""

    def test_api_requests_llevan_ua_custom(self):
        vistos = []

        def fake_urlopen(req, timeout=None):
            vistos.append(req)
            return _resp({"choices": [{"message": {"content": "ok"}}],
                          "results": [], "answer": None, "response": "ok"})

        with patch.dict("os.environ", {"GROQ_API_KEY": "x",
                                       "TAVILY_API_KEY": "x"}), \
             patch("urllib.request.urlopen", side_effect=fake_urlopen):
            research_lib.LLM("groq").call(None, "hola", 10)
            research_lib.tavily_search("hola")
        self.assertGreaterEqual(len(vistos), 2)
        for req in vistos:
            self.assertEqual(req.get_header("User-agent"),
                             "flujo-mak-research/1.0")


if __name__ == "__main__":
    unittest.main()
