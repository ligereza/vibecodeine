#!/usr/bin/env python3
"""Pruebas unitarias para research_lib.py usando mocks (sin consumo de APIs)."""

import json
import unittest
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError

import research_lib


class TestResearchLib(unittest.TestCase):
    def setUp(self):
        # Establecemos un entorno controlado para las keys
        self.env_patcher = patch.dict('os.environ', {
            "GROQ_API_KEY": "fake-groq",
            "CEREBRAS_API_KEY": "fake-cerebras",
            "AZURE_API_KEY": "fake-azure",
            "OLLAMA_BASE_URL": "http://127.0.0.1:11434",
            "TAVILY_API_KEY": "fake-tavily"
        })
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    @patch('research_lib.urllib.request.urlopen')
    def test_tavily_search(self, mock_urlopen):
        # Configuramos la respuesta falsa del buscador
        fake_response = MagicMock()
        fake_response.read.return_value = json.dumps({
            "results": [{"title": "Test", "url": "http://test.com", "content": "Fake content"}],
            "answer": "Fake answer"
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = fake_response

        # Ejecutamos
        res = research_lib.tavily_search("query de prueba")
        
        # Validamos
        self.assertEqual(res["answer"], "Fake answer")
        self.assertEqual(len(res["results"]), 1)
        self.assertEqual(res["results"][0]["url"], "http://test.com")
        self.assertTrue(mock_urlopen.called)

    @patch('research_lib.urllib.request.urlopen')
    def test_fetch_url_strips_tags(self, mock_urlopen):
        fake_html = b"<html><head><title>Test</title></head><body><h1>Hola</h1><p>Mundo &amp; cia;</p><script>alert(1)</script></body></html>"
        fake_response = MagicMock()
        fake_response.read.return_value = fake_html
        mock_urlopen.return_value.__enter__.return_value = fake_response

        res = research_lib.fetch_url("http://fake.com")
        
        # tags y script deben desaparecer
        self.assertNotIn("<html>", res)
        self.assertNotIn("alert(1)", res)
        self.assertIn("Hola Mundo", res.replace("  ", " "))

    @patch('research_lib.urllib.request.urlopen')
    def test_llm_fallback(self, mock_urlopen):
        # Queremos que Groq falle con HTTP 500 y Cerebras funcione.
        # urllib lanza HTTPError.
        def urlopen_side_effect(req, timeout=None):
            if "api.groq.com" in req.full_url:
                raise HTTPError(req.full_url, 500, "Internal Server Error", {}, None)
            
            # Para Cerebras devolvemos un JSON de exito
            fake_response = MagicMock()
            fake_response.read.return_value = json.dumps({
                "choices": [{"message": {"content": "Respuesta desde cerebras"}}]
            }).encode('utf-8')
            
            # Simulamos el __enter__ del context manager
            ctx = MagicMock()
            ctx.__enter__.return_value = fake_response
            return ctx

        mock_urlopen.side_effect = urlopen_side_effect

        llm = research_lib.LLM(order="groq,cerebras")
        text, provider = llm.call("System", "User")
        
        # Comprobamos que Cerebras tomo el relevo
        self.assertEqual(text, "Respuesta desde cerebras")
        self.assertEqual(provider, "cerebras")
        # Y que el error de Groq quedo registrado en stats/errors
        self.assertEqual(len(llm.errors), 1)
        self.assertIn("groq: HTTP 500", llm.errors[0])
        self.assertEqual(llm.stats.get("cerebras"), 1)


if __name__ == '__main__':
    unittest.main()
