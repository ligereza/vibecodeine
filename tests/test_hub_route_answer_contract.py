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


# Query values are caller input. A route that assumes they parse is a 500
# waiting for a typo -- the same assumption that made a non-numeric
# Content-Length crash seven POST routes.
HOSTILE_QUERIES = {
    "no numerico": "limit=abc&width=abc&height=abc&seed=abc&id=abc&offset=abc&n=abc",
    "vacio": "limit=&width=&height=&seed=&id=&offset=&n=",
    "negativo": "limit=-5&width=-5&height=-5&offset=-5&n=-5",
    "enorme": "limit=99999999999999999999&width=99999999999999999999&offset=99999999999999999999",
}


def _query_reading_routes() -> list[str]:
    """The exact GET routes whose own branch reads the query string.

    Only 21 of 76 do. Driving the other 55 with a hostile query pays each
    route's full cost -- one of them takes 2.75 s -- to prove something its
    branch cannot get wrong, because it never looks at the query. The list
    comes from the inventory, so a route that starts reading one is covered
    without editing this file.
    """
    rows = inventory()["methods"].get("GET", [])
    prefixes = _proxy_prefixes()
    paths = sorted(
        {
            str(row["path"])
            for row in rows
            if row["match"] == "exact"
            and row["reads_query"]
            and not any(str(row["path"]).startswith(prefix) for prefix in prefixes)
        }
    )
    assert paths, "no route reads the query: the inventory stopped detecting them"
    return paths


QUERY_ROUTES = _query_reading_routes()


def test_the_query_filter_narrows_without_emptying() -> None:
    """The filter has to cut, and has to keep the routes that matter.

    A detector that silently matched nothing would turn this contract into 0
    cases and still report green; one that matched everything would give back
    the cost it was written to remove.
    """
    assert set(QUERY_ROUTES) <= set(GET_ROUTES)
    assert len(QUERY_ROUTES) < len(GET_ROUTES), "the filter removed nothing"
    assert len(QUERY_ROUTES) >= 15, f"only {len(QUERY_ROUTES)} routes read a query"
    # Routes whose whole behaviour depends on a query parameter.
    for known in ("/api/portfolio/copilot/map", "/api/research/job", "/pieza"):
        assert known in QUERY_ROUTES, f"{known} reads a query and was filtered out"


def test_routes_that_ignore_the_query_are_still_covered() -> None:
    """Dropping them here loses nothing: they are driven by the other three."""
    ignoring = set(GET_ROUTES) - set(QUERY_ROUTES)
    assert ignoring, "every route reads the query, which contradicts the inventory"
    # Those three contracts parametrise over GET_ROUTES, not QUERY_ROUTES.
    assert ignoring <= set(GET_ROUTES)


@pytest.mark.parametrize("label,query", sorted(HOSTILE_QUERIES.items()))
@pytest.mark.parametrize("path", QUERY_ROUTES)
def test_get_route_survives_a_hostile_query(path: str, label: str, query: str) -> None:
    handler = FakeHandler(f"{path}?{query}")

    try:
        hub.H.do_GET(handler)
    except Exception as error:  # noqa: BLE001 - that would be the defect
        pytest.fail(f"GET {path}?{query} ({label}) raised {type(error).__name__}: {error}")

    assert handler.answered, f"GET {path}?{query} ({label}) answered nothing"


@pytest.mark.parametrize("path", GET_ROUTES)
def test_get_route_status_agrees_with_its_own_body(path: str) -> None:
    """A route that says it failed must not answer 200.

    hub.py already records this as a measured defect: a body reading
    `{"available": false}` under a 200 is honest to a human and invisible to a
    machine, because a probe, a watchdog or a proxy reads the status code.
    `_status_for` was written for it and two routes were fixed; three more --
    `/api/portfolio/copilot/scene`, `/api/portfolio/copilot/suggestions` and
    `/api/portfolio/production` -- still answered 200 while their bodies said
    `ok: false`, two of them with the same `item_no_encontrado` that their
    sibling routes `vision` and `manifest` answer 404 for.
    """
    handler = FakeHandler(path)
    hub.H.do_GET(handler)

    if not handler.calls:
        return
    kind, payload, code = handler.calls[-1]
    if kind != "json" or not isinstance(payload, dict):
        return

    declares_failure = payload.get("available") is False or payload.get("ok") is False
    if declares_failure and code == 200:
        pytest.fail(
            f"GET {path} answered 200 with a body that says it failed "
            f"({ {k: payload[k] for k in list(payload)[:3]} }). "
            "Name the error in hub._ERROR_STATUS so the code agrees with the body."
        )


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
