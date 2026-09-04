#!/usr/bin/env python3
"""Every GET route of the MAK hub answers; none of them raises.

`cultura/mak_plataforma/hub.py` dispatches from a 458-line `do_GET` if-chain.
Adding a route is one more `if p ==` branch, and `tools/hub_route_inventory.py`
measured 31 GET routes that no test in the suite so much as mentions. An
unhandled exception in any of them reaches `BaseHTTPRequestHandler`, which
answers 500 with a traceback in the server log and nothing useful to the
caller.

This module asserts the one contract every route shares regardless of what it
does: it produces a response, and it does so without raising. A route that is
degraded -- no database, no optional dependency, a missing file -- satisfies
this by answering 404 or 503; that is a fine answer and a crash is not.

The route list comes from the inventory tool rather than a hardcoded copy, so a
route added to the hub tomorrow is covered here without editing this file.
Proxy prefixes are excluded because reaching them means opening a socket to a
service that is not running in a test.
"""
from __future__ import annotations

import io
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_plataforma"))

from tools.hub_route_inventory import inventory  # noqa: E402

import hub  # noqa: E402


class FakeHandler:
    """Capture what a dispatcher answers without opening a socket."""

    def __init__(self, path: str, command: str = "GET") -> None:
        self.path = path
        self.rfile = io.BytesIO(b"")
        self.headers = {}
        self.command = command
        self.calls: list[tuple] = []
        self.redirect: dict | None = None

    def _json(self, obj, code=200):
        self.calls.append(("json", obj, code))

    def _send(self, body_text, ctype="text/html; charset=utf-8", code=200):
        self.calls.append(("send", body_text, code))

    def _send_bytes(self, data, ctype="application/octet-stream", code=200):
        self.calls.append(("bytes", data, code))

    def send_response(self, code):
        self.redirect = {"code": code}

    def send_header(self, key, value):
        assert self.redirect is not None, "send_header before send_response"
        self.redirect.setdefault("headers", {})[key] = value

    def end_headers(self):
        pass

    @property
    def answered(self) -> bool:
        return bool(self.calls) or self.redirect is not None


def _proxy_prefixes() -> tuple[str, ...]:
    return tuple("/" + prefix for prefix in getattr(hub, "SERVICE_PROXY_PREFIXES", ()))


def _get_routes() -> list[str]:
    """Exact GET paths from the inventory, minus the ones that need a network."""
    rows = inventory()["methods"].get("GET", [])
    prefixes = _proxy_prefixes()
    paths = sorted(
        {
            str(row["path"])
            for row in rows
            if row["match"] == "exact"
            and not any(str(row["path"]).startswith(prefix) for prefix in prefixes)
        }
    )
    # A measured zero is an error, not a clean bill: if the inventory stops
    # finding routes this test would pass forever while covering nothing.
    assert len(paths) > 40, f"the route inventory found only {len(paths)} GET routes"
    return paths


GET_ROUTES = _get_routes()


@pytest.mark.parametrize("path", GET_ROUTES)
def test_get_route_answers_without_raising(path: str) -> None:
    handler = FakeHandler(path)

    try:
        hub.H.do_GET(handler)
    except Exception as error:  # noqa: BLE001 - the point is that none escape
        pytest.fail(f"GET {path} raised {type(error).__name__}: {error}")

    assert handler.answered, f"GET {path} returned without answering anything"


@pytest.mark.parametrize("path", GET_ROUTES)
def test_get_route_never_answers_500(path: str) -> None:
    handler = FakeHandler(path)
    hub.H.do_GET(handler)

    codes = [call[-1] for call in handler.calls]
    if handler.redirect is not None:
        codes.append(handler.redirect["code"])

    assert all(code < 500 or code == 503 for code in codes), (
        f"GET {path} answered {codes}: a degraded dependency is 503, "
        "a server fault is a defect"
    )
