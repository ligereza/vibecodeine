"""Tests for tools/vj_set/osc_sender.py.

No __init__.py under tools/, so the module is loaded directly by file path
via importlib (same pattern as tests/test_vj_git_performance.py).
"""

from __future__ import annotations

import importlib.util
import json
import socket
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "vj_set" / "osc_sender.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("vj_osc_sender", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


osc = _load_module()


# ---------------------------------------------------------------------------
# encode_osc: golden bytes computed by hand (address padded to 4-byte
# boundary with AT LEAST one null byte, typetag string padded the same way,
# int32/float32 big-endian).
# ---------------------------------------------------------------------------


def test_encode_osc_int_arg_matches_hand_computed_bytes() -> None:
    address = "/composition/layers/1/clips/2/connect"
    # len(address) == 37 -> padded to 40 (3 nulls, since 37 % 4 == 1 -> pad 3
    # ... but OSC always pads at least 1, and 37 -> next multiple of 4 is 40)
    expected_address = address.encode("utf-8") + b"\x00" * 3
    assert len(expected_address) == 40
    # typetag ",i" is 2 bytes -> padded to 4 (2 nulls)
    expected_typetag = b",i" + b"\x00" * 2
    expected_args = struct.pack(">i", 1)
    expected = expected_address + expected_typetag + expected_args

    assert osc.encode_osc(address, 1) == expected
    assert expected == (
        b"/composition/layers/1/clips/2/connect\x00\x00\x00"
        b",i\x00\x00"
        b"\x00\x00\x00\x01"
    )


def test_encode_osc_short_address_pads_full_4_bytes() -> None:
    # "/a" is 2 bytes -> len % 4 == 2 -> pad 2 to reach 4.
    packet = osc.encode_osc("/a", 1)
    assert packet.startswith(b"/a\x00\x00")
    assert packet[4:8] == b",i\x00\x00"


def test_encode_osc_address_already_multiple_of_4_still_pads() -> None:
    # "/abcd" without trailing arg concerns: length 5 -> pad to 8 (not 0-pad
    # since OSC requires at least one null terminator).
    address = "/abcd"
    packet = osc.encode_osc(address, 0)
    # address field must be a multiple of 4 AND null-terminated
    addr_field = packet[:8]
    assert addr_field == b"/abcd\x00\x00\x00"
    assert len(addr_field) % 4 == 0


def test_encode_osc_float_arg() -> None:
    address = "/foo"
    packet = osc.encode_osc(address, 1.5)
    # "/foo" is already 4 bytes -> still padded with 4 more nulls (min 1 null rule)
    expected_address = b"/foo\x00\x00\x00\x00"
    expected_typetag = b",f\x00\x00"
    expected_args = struct.pack(">f", 1.5)
    assert packet == expected_address + expected_typetag + expected_args


def test_encode_osc_string_arg() -> None:
    address = "/foo"
    packet = osc.encode_osc(address, "hi")
    expected_address = b"/foo\x00\x00\x00\x00"
    expected_typetag = b",s\x00\x00"
    expected_str = b"hi\x00\x00"
    assert packet == expected_address + expected_typetag + expected_str


def test_encode_osc_multiple_args() -> None:
    packet = osc.encode_osc("/x", 1, 2.5, "z")
    assert packet.startswith(b"/x\x00\x00")
    # typetag ",ifs" -> 4 bytes, already multiple of 4 -> pad 4 more
    assert b",ifs\x00\x00\x00\x00" in packet


def test_encode_osc_rejects_address_without_leading_slash() -> None:
    with pytest.raises(ValueError):
        osc.encode_osc("no-slash", 1)


def test_encode_osc_rejects_unsupported_type() -> None:
    with pytest.raises(TypeError):
        osc.encode_osc("/x", {"nope": 1})


# ---------------------------------------------------------------------------
# UDP round-trip: real socket, real datagrams.
# ---------------------------------------------------------------------------


SAMPLE_SCORE = {
    "port": 7000,
    "fps": 30,
    "duration_s": 1.0,
    "messages": [
        {"t": 0.0, "address": "/composition/layers/1/clips/1/connect", "args": [1], "type": "merge"},
        {"t": 0.0, "address": "/composition/layers/2/clips/1/connect", "args": [1], "type": "feat"},
        {"t": 0.0, "address": "/composition/layers/3/clips/1/connect", "args": [1], "type": "fix"},
    ],
}


def test_udp_round_trip_sends_exact_datagrams() -> None:
    listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listener.bind(("127.0.0.1", 0))
    listener.settimeout(5.0)
    port = listener.getsockname()[1]

    try:
        sent, remaining = osc.run(
            SAMPLE_SCORE, host="127.0.0.1", port_override=port,
            dry_run=False, speed=1_000_000.0, desde=0.0,
        )
        assert sent == 3
        assert remaining == 0

        received = []
        for _ in range(3):
            data, _addr = listener.recvfrom(4096)
            received.append(data)
    finally:
        listener.close()

    expected = [
        osc.encode_osc(m["address"], *m["args"]) for m in SAMPLE_SCORE["messages"]
    ]
    assert received == expected


def test_udp_round_trip_respects_score_port_when_no_override() -> None:
    listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listener.bind(("127.0.0.1", 0))
    listener.settimeout(5.0)
    port = listener.getsockname()[1]

    score = {**SAMPLE_SCORE, "port": port, "messages": SAMPLE_SCORE["messages"][:1]}

    try:
        sent, remaining = osc.run(
            score, host="127.0.0.1", port_override=None,
            dry_run=False, speed=1_000_000.0, desde=0.0,
        )
        assert sent == 1
        data, _addr = listener.recvfrom(4096)
    finally:
        listener.close()

    assert data == osc.encode_osc(
        score["messages"][0]["address"], *score["messages"][0]["args"]
    )


# ---------------------------------------------------------------------------
# --dry-run: no socket ever created.
# ---------------------------------------------------------------------------


def test_dry_run_never_opens_a_socket(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    def _boom(*_a, **_kw):
        raise AssertionError("socket.socket() must not be called in --dry-run")

    monkeypatch.setattr(socket, "socket", _boom)

    sent, remaining = osc.run(
        SAMPLE_SCORE, host="127.0.0.1", port_override=7000,
        dry_run=True, speed=1_000_000.0, desde=0.0,
    )
    assert sent == 3
    assert remaining == 0

    out = capsys.readouterr().out
    lines = [line for line in out.splitlines() if line.strip()]
    assert len(lines) == 3
    for line, msg in zip(lines, SAMPLE_SCORE["messages"]):
        assert line.startswith(f"t={msg['t']:.3f} {msg['address']}")


# ---------------------------------------------------------------------------
# --desde filtering.
# ---------------------------------------------------------------------------


TIMED_SCORE = {
    "port": 7000,
    "fps": 30,
    "duration_s": 10.0,
    "messages": [
        {"t": 0.0, "address": "/composition/layers/1/clips/1/connect", "args": [1], "type": "a"},
        {"t": 3.0, "address": "/composition/layers/2/clips/1/connect", "args": [1], "type": "b"},
        {"t": 6.0, "address": "/composition/layers/3/clips/1/connect", "args": [1], "type": "c"},
    ],
}


def test_desde_filters_cues_before_the_cutoff(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    def _boom(*_a, **_kw):
        raise AssertionError("socket.socket() must not be called in --dry-run")

    monkeypatch.setattr(socket, "socket", _boom)

    sent, remaining = osc.run(
        TIMED_SCORE, host="127.0.0.1", port_override=None,
        dry_run=True, speed=1_000_000.0, desde=4.0,
    )
    assert sent == 1  # only the t=6.0 cue survives desde=4.0
    assert remaining == 0

    out = capsys.readouterr().out
    lines = [line for line in out.splitlines() if line.strip()]
    assert len(lines) == 1
    assert "layers/3/clips/1" in lines[0]


def test_desde_zero_keeps_everything(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.setattr(socket, "socket", lambda *a, **kw: (_ for _ in ()).throw(
        AssertionError("no socket in dry-run")
    ))
    sent, _remaining = osc.run(
        TIMED_SCORE, host="127.0.0.1", port_override=None,
        dry_run=True, speed=1_000_000.0, desde=0.0,
    )
    assert sent == 3


# ---------------------------------------------------------------------------
# load_score
# ---------------------------------------------------------------------------


def test_load_score_reads_real_git_performance_output(tmp_path: Path) -> None:
    score_path = tmp_path / "osc_score.json"
    score_path.write_text(json.dumps(SAMPLE_SCORE), encoding="utf-8")
    loaded = osc.load_score(score_path)
    assert loaded == SAMPLE_SCORE


def test_load_score_rejects_file_without_messages_key(tmp_path: Path) -> None:
    bad_path = tmp_path / "bad.json"
    bad_path.write_text(json.dumps({"port": 7000}), encoding="utf-8")
    with pytest.raises(ValueError):
        osc.load_score(bad_path)
