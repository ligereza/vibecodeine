#!/usr/bin/env python3
"""Azure CLI token bridge shared by MAK's Azure adapters.

MAK already has an authenticated ``az`` session.  This module reuses it and
keeps short-lived tokens in memory only; it never writes credentials, asks for
login, or prints token material.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import threading
import time


_LOCK = threading.Lock()
_CACHE: dict[str, tuple[str, float]] = {}


def token_for(resource: str) -> str:
    """Return a cached AAD token for one Azure resource audience."""
    audience = str(resource or "").strip().rstrip("/")
    if not audience:
        raise RuntimeError("azure_resource_required")
    now = time.monotonic()
    with _LOCK:
        cached = _CACHE.get(audience)
        if cached and cached[1] > now:
            return cached[0]
        az = os.environ.get("AZ_CLI") or shutil.which("az")
        if not az:
            raise RuntimeError("azure_cli_unavailable")
        completed = subprocess.run(
            [az, "account", "get-access-token", "--resource", audience,
             "--query", "accessToken", "-o", "tsv"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        token = (completed.stdout or "").strip()
        if completed.returncode != 0 or not token:
            raise RuntimeError("azure_cli_token_unavailable")
        _CACHE[audience] = (token, now + 300)
        return token
