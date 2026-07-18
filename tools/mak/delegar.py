#!/usr/bin/env python3
"""
delegar.py - MAK delegation client (flujo -> MAK LAN peer).

Bridges flujo (Windows) to MAK (Linux 192.168.50.2) for delegating mechanical work:
  - research: investigation jobs to :8890
  - codex: code generation/review/testing to :8891
  - salud: health status of :8900 hub

API Contracts extracted from:
  - cultura/mak_research/interfaz.py (research endpoints)
  - cultura/mak_codex/interfaz_codex.py (codex endpoints)
  - cultura/mak_plataforma/hub.py (health endpoint)

Token handling: env MAK_CODEX_TOKEN or file via --token-file.
All requests have timeouts (default 10s). No hardcoding, no token leaks in output.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


MAK_HOST = "192.168.50.2"
RESEARCH_PORT = 8890
CODEX_PORT = 8891
HUB_PORT = 8900
DEFAULT_TIMEOUT = 10

# Research modes (from interfaz.py MODO_DIR)
RESEARCH_MODES = {
    "research": "single analysis",
    "panel": "committee discussion",
    "cadena": "chained providers",
    "refutar": "adversarial",
    "corpus": "archive correlation",
    "grafo": "custom graph",
    "memoria": "semantic memory",
}

# Codex modes (from interfaz_codex.py line 331)
CODEX_MODES = {
    "generar": "generate code",
    "revisar": "review code",
    "testear": "test code",
    "debug": "debug code",
}


class MAKClientError(Exception):
    """Base exception for MAK client errors."""
    pass


class MAKNetworkError(MAKClientError):
    """Network error (exit code 1)."""
    pass


class MAKUsageError(MAKClientError):
    """Usage/API error (exit code 2)."""
    pass


def _get_token():
    """
    Fetch token from env MAK_CODEX_TOKEN or file via CLI arg.
    Never print token value.
    Returns: (token, source) or (None, "not_found")
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--token-file", type=str, default=None)
    args, _ = parser.parse_known_args()

    if args.token_file:
        try:
            with open(args.token_file, "r") as f:
                token = _extract_token(f.read())
            if token:
                return token, f"file:{args.token_file}"
        except (OSError, IOError) as e:
            raise MAKUsageError(f"Could not read token file: {e}")

    token = _extract_token(os.environ.get("MAK_CODEX_TOKEN", ""))
    if token:
        return token, "env:MAK_CODEX_TOKEN"

    return None, "not_found"


def _extract_token(raw):
    """
    Extract the token value from raw file/env content.

    The MAK box stores ~/codex/.token as an env-file line
    (CODEX_TOKEN="value"), which the server parses by regex --
    see cultura/mak_plataforma/hub.py:480. Accept that shape as well
    as a bare token, stripping any KEY= prefix and surrounding quotes.
    """
    if not raw:
        return ""
    text = raw.strip()
    m = re.search(r'(?:CODEX_TOKEN|INTERFAZ_TOKEN|TOKEN)\s*=\s*["\']?([^"\'\s]+)',
                  text)
    if m:
        return m.group(1)
    return text.strip('"\'')


def _http_get(path, host=MAK_HOST, port=HUB_PORT, token=None, timeout=DEFAULT_TIMEOUT):
    """
    Make HTTP GET request. Returns decoded JSON response.

    Args:
        path: URL path (e.g., "/api/salud")
        host: Target host (default MAK_HOST)
        port: Target port (default HUB_PORT)
        token: Optional auth token (query param t=...)
        timeout: Request timeout in seconds

    Returns:
        Parsed JSON dict

    Raises:
        MAKNetworkError: network/timeout issues (exit 1)
        MAKUsageError: API/auth errors (exit 2)

    References:
        - research interfaz.py line 2628-2637 (_check_auth)
        - codex interfaz_codex.py line 272-279 (_auth)
    """
    url = f"http://{host}:{port}{path}"
    if token:
        url += ("&" if "?" in path else "?") + f"t={urllib.parse.quote(token)}"

    try:
        req = urllib.request.Request(
            url,
            method="GET",
            headers={
                "User-Agent": "flujo-mak-delegar/1.0",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read(1000000).decode("utf-8", errors="replace")
            return json.loads(data)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise MAKUsageError("Authentication failed (invalid or missing token)")
        raise MAKNetworkError(f"HTTP {e.code}: {e.reason}")
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        raise MAKNetworkError(f"Network error: {e}")
    except (json.JSONDecodeError, ValueError) as e:
        raise MAKUsageError(f"Invalid JSON response: {e}")


def _http_post(
    path,
    data,
    host=MAK_HOST,
    port=HUB_PORT,
    token=None,
    timeout=DEFAULT_TIMEOUT,
):
    """
    Make HTTP POST request with form data. Returns decoded JSON response.

    Args:
        path: URL path (e.g., "/run")
        data: dict of form parameters
        host: Target host (default MAK_HOST)
        port: Target port (default HUB_PORT)
        token: Optional auth token (query param t=...)
        timeout: Request timeout in seconds

    Returns:
        Parsed JSON dict

    Raises:
        MAKNetworkError: network/timeout issues (exit 1)
        MAKUsageError: API/auth errors (exit 2)

    References:
        - research interfaz.py line 2861-2882 (POST /run)
        - codex interfaz_codex.py line 325-339 (POST /run)
    """
    url = f"http://{host}:{port}{path}"
    if token:
        url += ("&" if "?" in path else "?") + f"t={urllib.parse.quote(token)}"

    body = urllib.parse.urlencode(data).encode("utf-8")
    try:
        req = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "flujo-mak-delegar/1.0",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            resp_data = response.read(1000000).decode("utf-8", errors="replace")
            return json.loads(resp_data)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise MAKUsageError("Authentication failed (invalid or missing token)")
        if e.code == 400:
            raise MAKUsageError(f"Bad request: {e.reason}")
        raise MAKNetworkError(f"HTTP {e.code}: {e.reason}")
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        raise MAKNetworkError(f"Network error: {e}")
    except (json.JSONDecodeError, ValueError) as e:
        raise MAKUsageError(f"Invalid JSON response: {e}")


def cmd_salud(args):
    """
    Query health/status of MAK hub (:8900).

    Reference: cultura/mak_plataforma/hub.py line 836-837
    GET /api/salud returns {"salud": {...}, "micelio_chunks": {...}, ...}
    """
    try:
        result = _http_get("/api/salud", host=MAK_HOST, port=HUB_PORT, timeout=args.timeout)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except MAKNetworkError as e:
        print(f"Error (network): {e}", file=sys.stderr)
        return 1
    except MAKUsageError as e:
        print(f"Error (usage): {e}", file=sys.stderr)
        return 2


def cmd_research(args):
    """
    Submit research job to :8890.

    Reference: cultura/mak_research/interfaz.py line 2861-2882 (POST /run)

    Args:
        --tema TEMA: research topic (max 300 chars)
        --modo MODE: research/panel/cadena/refutar/corpus/grafo/memoria
                     (default: research)
        --densidad DENSITY: corto/medio/largo (default: medio)
        --n N: iterations (0-10)
        --memoria: use semantic memory
        --token-file FILE: path to token file
        --timeout SECONDS: request timeout (default: 10)
    """
    token, token_src = _get_token()
    if not token and os.environ.get("INTERFAZ_TOKEN"):
        token = os.environ.get("INTERFAZ_TOKEN")
        token_src = "env:INTERFAZ_TOKEN (research)"

    if not args.tema:
        raise MAKUsageError("--tema is required")

    if args.modo not in RESEARCH_MODES:
        raise MAKUsageError(f"Invalid --modo. Must be one of: {', '.join(RESEARCH_MODES.keys())}")

    if args.densidad not in ("corto", "medio", "largo"):
        raise MAKUsageError("--densidad must be corto/medio/largo")

    data = {
        "tema": args.tema[:300],
        "modo": args.modo,
        "densidad": args.densidad,
    }

    if args.n is not None:
        try:
            n = int(args.n)
            n = max(0, min(n, 10))
            data["n"] = str(n)
        except (ValueError, TypeError):
            raise MAKUsageError(f"--n must be integer 0-10")

    if args.memoria:
        data["memoria"] = "1"

    try:
        result = _http_post(
            "/run",
            data,
            host=MAK_HOST,
            port=RESEARCH_PORT,
            token=token,
            timeout=args.timeout,
        )
        if result.get("ok"):
            print(f"Research job submitted: {args.tema[:60]}")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
        else:
            raise MAKUsageError(result.get("error", "Unknown error"))
    except MAKNetworkError as e:
        print(f"Error (network): {e}", file=sys.stderr)
        return 1
    except MAKUsageError as e:
        print(f"Error (usage): {e}", file=sys.stderr)
        return 2


def cmd_codex(args):
    """
    Submit codex job to :8891.

    Reference: cultura/mak_codex/interfaz_codex.py line 325-339 (POST /run)

    Args:
        --pedido TEXT: code request (max 2000 chars)
        --modo MODE: generar/revisar/testear/debug (default: generar)
        --densidad DENSITY: corto/medio/largo (default: medio)
        --token-file FILE: path to token file (required or MAK_CODEX_TOKEN)
        --timeout SECONDS: request timeout (default: 10)
    """
    token, token_src = _get_token()
    if not token:
        raise MAKUsageError("Token required: --token-file or env MAK_CODEX_TOKEN")

    if not args.pedido:
        raise MAKUsageError("--pedido is required")

    if args.modo not in CODEX_MODES:
        raise MAKUsageError(f"Invalid --modo. Must be one of: {', '.join(CODEX_MODES.keys())}")

    if args.densidad not in ("corto", "medio", "largo"):
        raise MAKUsageError("--densidad must be corto/medio/largo")

    data = {
        "pedido": args.pedido[:2000],
        "modo": args.modo,
        "densidad": args.densidad,
    }

    try:
        result = _http_post(
            "/run",
            data,
            host=MAK_HOST,
            port=CODEX_PORT,
            token=token,
            timeout=args.timeout,
        )
        if result.get("ok"):
            print(f"Codex job submitted ({args.modo}): {args.pedido[:60]}")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
        else:
            raise MAKUsageError(result.get("error", "Unknown error"))
    except MAKNetworkError as e:
        print(f"Error (network): {e}", file=sys.stderr)
        return 1
    except MAKUsageError as e:
        print(f"Error (usage): {e}", file=sys.stderr)
        return 2


def main():
    """Parse CLI args and dispatch to command handlers."""
    parser = argparse.ArgumentParser(
        prog="delegar",
        description="MAK delegation client - submit work to Linux peer",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Request timeout in seconds (default {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--token-file",
        type=str,
        default=None,
        help="Path to token file (for codex)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # salud
    salud_parser = subparsers.add_parser("salud", help="Check MAK hub health")

    # research
    research_parser = subparsers.add_parser("research", help="Submit research job")
    research_parser.add_argument("--tema", type=str, required=True, help="Research topic")
    research_parser.add_argument(
        "--modo",
        type=str,
        default="research",
        choices=list(RESEARCH_MODES.keys()),
        help="Research mode (default: research)",
    )
    research_parser.add_argument(
        "--densidad",
        type=str,
        default="medio",
        choices=("corto", "medio", "largo"),
        help="Output density (default: medio)",
    )
    research_parser.add_argument(
        "--n",
        type=int,
        default=None,
        help="Iterations (0-10)",
    )
    research_parser.add_argument(
        "--memoria",
        action="store_true",
        help="Use semantic memory",
    )

    # codex
    codex_parser = subparsers.add_parser("codex", help="Submit codex job")
    codex_parser.add_argument("--pedido", type=str, required=True, help="Code request")
    codex_parser.add_argument(
        "--modo",
        type=str,
        default="generar",
        choices=list(CODEX_MODES.keys()),
        help="Codex mode (default: generar)",
    )
    codex_parser.add_argument(
        "--densidad",
        type=str,
        default="medio",
        choices=("corto", "medio", "largo"),
        help="Output density (default: medio)",
    )

    args = parser.parse_args()

    try:
        if args.command == "salud":
            return cmd_salud(args)
        elif args.command == "research":
            return cmd_research(args)
        elif args.command == "codex":
            return cmd_codex(args)
        else:
            parser.print_help()
            return 2
    except MAKUsageError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except MAKNetworkError as e:
        print(f"Error (network): {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
