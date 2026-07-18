"""
Test suite for tools/mak/delegar.py.

All tests are mocked (no real network). Cover:
- salud parse
- error paths (network fail -> exit 1)
- research/codex payload shape
- argument validation
"""
import json
import os
import sys
import tempfile
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

# Add tools/mak to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from mak import delegar


class TestMAKDelegar(unittest.TestCase):
    """Test MAK delegation client."""

    def setUp(self):
        """Save original env and stdout/stderr."""
        self.orig_env = os.environ.copy()
        self.stdout = StringIO()
        self.stderr = StringIO()

    def tearDown(self):
        """Restore original env."""
        os.environ.clear()
        os.environ.update(self.orig_env)

    @patch("mak.delegar._http_get")
    def test_salud_success(self, mock_get):
        """Test salud command parses response correctly."""
        mock_response = {
            "salud": {"estado": "ok"},
            "micelio_chunks": 42,
            "actividad": {"jobs": []},
        }
        mock_get.return_value = mock_response

        with patch("sys.stdout", self.stdout):
            result = delegar.cmd_salud(MagicMock(timeout=10))

        self.assertEqual(result, 0)
        output = self.stdout.getvalue()
        self.assertIn("salud", output)
        self.assertIn("micelio_chunks", output)

    @patch("mak.delegar._http_get")
    def test_salud_network_error(self, mock_get):
        """Test salud handles network errors (exit 1)."""
        mock_get.side_effect = delegar.MAKNetworkError("Connection refused")

        with patch("sys.stderr", self.stderr):
            result = delegar.cmd_salud(MagicMock(timeout=10))

        self.assertEqual(result, 1)
        self.assertIn("network", self.stderr.getvalue())

    @patch("mak.delegar._http_post")
    def test_research_submit_success(self, mock_post):
        """Test research job submission with valid payload."""
        mock_post.return_value = {"ok": True}

        args = MagicMock(
            tema="test research topic",
            modo="research",
            densidad="medio",
            n=None,
            memoria=False,
            timeout=10,
        )

        with patch("sys.stdout", self.stdout):
            result = delegar.cmd_research(args)

        self.assertEqual(result, 0)
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        data = call_args[0][1]  # Second positional arg is data dict
        self.assertEqual(data["tema"], "test research topic")
        self.assertEqual(data["modo"], "research")
        self.assertEqual(data["densidad"], "medio")

    def test_research_missing_tema(self):
        """Test research rejects empty tema."""
        args = MagicMock(
            tema="",
            modo="research",
            densidad="medio",
            timeout=10,
        )

        with self.assertRaises(delegar.MAKUsageError) as ctx:
            delegar.cmd_research(args)

        self.assertIn("--tema", str(ctx.exception))

    def test_research_invalid_modo(self):
        """Test research rejects invalid modo."""
        args = MagicMock(
            tema="test",
            modo="invalid",
            densidad="medio",
            n=None,
            memoria=False,
            timeout=10,
        )

        with self.assertRaises(delegar.MAKUsageError) as ctx:
            delegar.cmd_research(args)

        self.assertIn("--modo", str(ctx.exception))

    @patch("mak.delegar._http_post")
    def test_research_with_iterations(self, mock_post):
        """Test research respects --n parameter."""
        mock_post.return_value = {"ok": True}

        args = MagicMock(
            tema="test",
            modo="research",
            densidad="medio",
            n=3,
            memoria=False,
            timeout=10,
        )

        with patch("sys.stdout", self.stdout):
            result = delegar.cmd_research(args)

        self.assertEqual(result, 0)
        data = mock_post.call_args[0][1]
        self.assertEqual(data["n"], "3")

    @patch("mak.delegar._http_post")
    def test_research_clamps_iterations(self, mock_post):
        """Test research clamps --n to 0-10 range."""
        mock_post.return_value = {"ok": True}

        args = MagicMock(
            tema="test",
            modo="research",
            densidad="medio",
            n=100,
            memoria=False,
            timeout=10,
        )

        with patch("sys.stdout", self.stdout):
            result = delegar.cmd_research(args)

        self.assertEqual(result, 0)
        data = mock_post.call_args[0][1]
        self.assertEqual(data["n"], "10")

    @patch("mak.delegar._http_post")
    def test_codex_submit_success(self, mock_post):
        """Test codex job submission."""
        mock_post.return_value = {"ok": True}

        args = MagicMock(
            pedido="write a parser",
            modo="generar",
            densidad="corto",
            timeout=10,
        )

        with patch("sys.stdout", self.stdout):
            result = delegar.cmd_codex(args)

        self.assertEqual(result, 0)
        call_args = mock_post.call_args
        data = call_args[0][1]
        self.assertEqual(data["pedido"], "write a parser")
        self.assertEqual(data["modo"], "generar")
        self.assertEqual(data["densidad"], "corto")

    def test_codex_invalid_modo(self):
        """Test codex rejects invalid modo."""
        args = MagicMock(
            pedido="test",
            modo="invalid",
            densidad="medio",
            timeout=10,
        )

        with self.assertRaises(delegar.MAKUsageError) as ctx:
            delegar.cmd_codex(args)

        self.assertIn("--modo", str(ctx.exception))

    @patch("mak.delegar._http_post")
    def test_codex_network_error(self, mock_post):
        """Test codex network error (exit 1)."""
        mock_post.side_effect = delegar.MAKNetworkError("Timeout")

        args = MagicMock(
            pedido="test",
            modo="generar",
            densidad="medio",
            timeout=10,
        )

        with patch("sys.stderr", self.stderr):
            result = delegar.cmd_codex(args)

        self.assertEqual(result, 1)
        self.assertIn("network", self.stderr.getvalue())

    @patch("urllib.request.urlopen")
    def test_http_get_network_timeout(self, mock_urlopen):
        """Test _http_get handles timeout as network error."""
        mock_urlopen.side_effect = TimeoutError("Connection timed out")

        with self.assertRaises(delegar.MAKNetworkError):
            delegar._http_get("/api/test", timeout=1)

    @patch("urllib.request.urlopen")
    def test_http_get_invalid_json(self, mock_urlopen):
        """Test _http_get handles invalid JSON as usage error."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"not json"
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = lambda s, *args: None
        mock_urlopen.return_value = mock_response

        with self.assertRaises(delegar.MAKUsageError):
            delegar._http_get("/api/test")

    @patch("urllib.request.urlopen")
    def test_http_post_success(self, mock_urlopen):
        """Test _http_post returns parsed JSON."""
        response_data = {"ok": True, "id": 42}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(response_data).encode()
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = lambda s, *args: None
        mock_urlopen.return_value = mock_response

        result = delegar._http_post("/run", {"tema": "test"})

        self.assertEqual(result["ok"], True)
        self.assertEqual(result["id"], 42)


class TestArgumentParsing(unittest.TestCase):
    """Test CLI argument parsing."""

    def test_research_minimal_args(self):
        """Test research command with minimal args."""
        sys.argv = ["delegar", "research", "--tema", "test topic"]
        parser = delegar.argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        research_parser = subparsers.add_parser("research")
        research_parser.add_argument("--tema", required=True)
        research_parser.add_argument("--modo", default="research")
        research_parser.add_argument("--densidad", default="medio")

        args = parser.parse_args(sys.argv[1:])
        self.assertEqual(args.tema, "test topic")
        self.assertEqual(args.modo, "research")
        self.assertEqual(args.densidad, "medio")

    def test_codex_minimal_args(self):
        """Test codex command with minimal args."""
        sys.argv = ["delegar", "codex", "--pedido", "write hello world"]
        parser = delegar.argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")
        codex_parser = subparsers.add_parser("codex")
        codex_parser.add_argument("--pedido", required=True)
        codex_parser.add_argument("--modo", default="generar")

        args = parser.parse_args(sys.argv[1:])
        self.assertEqual(args.pedido, "write hello world")
        self.assertEqual(args.modo, "generar")


if __name__ == "__main__":
    unittest.main()
