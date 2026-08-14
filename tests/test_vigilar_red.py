"""Tests for the local, address-independent MAK egress guard."""
import importlib.util
import json
from ipaddress import ip_network
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "cultura" / "mak_plataforma" / "vigilar_red.py"
SPEC = importlib.util.spec_from_file_location("vigilar_red_tested", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_local_network_detection_uses_linux_interface_output(monkeypatch):
    class Result:
        stdout = "2: eth0    inet 10.23.4.8/24 brd 10.23.4.255 scope global eth0\n"

    monkeypatch.setattr(MODULE.subprocess, "run", lambda *args, **kwargs: Result())
    networks, addresses = MODULE._local_networks()
    assert networks == [ip_network("10.23.4.0/24")]
    assert addresses == {"10.23.4.8"}


def test_revisar_excludes_local_address_and_uses_detected_network(tmp_path, monkeypatch):
    state = tmp_path / "vigilar.json"
    monkeypatch.setattr(MODULE, "ESTADO", str(state))
    monkeypatch.setattr(MODULE, "_conexiones", lambda: [
        "10.23.4.8", "10.23.4.9", "203.0.113.4",
    ])
    monkeypatch.setattr(MODULE, "_local_networks", lambda: (
        [ip_network("10.23.4.0/24")], {"10.23.4.8"}))

    snapshot = MODULE.revisar()
    assert snapshot["hosts_lan_distintos"] == 1
    assert snapshot["muestra"] == ["10.23.4.9"]
    assert json.loads(state.read_text(encoding="utf-8"))["redes_locales"] == [
        "10.23.4.0/24"
    ]


def test_guard_has_no_fixed_windows_or_gateway_addresses():
    source = PATH.read_text(encoding="utf-8")
    assert "192.168." not in source
    assert "GATEWAY" not in source
    assert "Windows" not in source
