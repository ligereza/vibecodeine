"""
Integration test: cue engine -> packet builders -> real UDP -> virtual node.

The xiotech M2 acceptance item ("nodo Art-Net virtual + servidor OSC dummy")
without hardware: two localhost UDP listeners play Art-Net node and OSC server,
the engine runs a 3-cue show, and we assert the actual bytes on the wire.
Standalone like the other tests:  py xio/new-plugins/showcontrol/test_integration.py
"""

import os
import socket
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import protocols as P            # noqa: E402
from cueengine import CueEngine  # noqa: E402


def make_listener():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("127.0.0.1", 0))
    s.settimeout(2.0)
    return s, s.getsockname()[1]


def send_events(events, artnet_addr, osc_addr, seq_state):
    """Mirror of the plugin's _emit_events, Flask-free."""
    out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        for ev in events:
            if ev[0] == "osc":
                out.sendto(P.build_osc_message(ev[1], ev[2]), osc_addr)
            elif ev[0] == "dmx":
                u = ev[1]
                seq_state[u] = seq_state.get(u, 0) % 255 + 1
                out.sendto(P.build_artnet_dmx(u, ev[2], sequence=seq_state[u]),
                           artnet_addr)
    finally:
        out.close()


def parse_artnet(pkt):
    assert pkt[:8] == b"Art-Net\x00"
    (op,) = struct.unpack("<H", pkt[8:10])
    assert op == 0x5000
    seq = pkt[12]
    universe = pkt[14] | (pkt[15] << 8)
    (length,) = struct.unpack(">H", pkt[16:18])
    return seq, universe, pkt[18:18 + length]


def test_show_over_the_wire():
    node, node_port = make_listener()      # virtual Art-Net node
    oscsrv, osc_port = make_listener()     # dummy OSC server
    artnet_addr = ("127.0.0.1", node_port)
    osc_addr = ("127.0.0.1", osc_port)

    e = CueEngine()
    e.load([
        {"label": "open", "fade": 2.0, "levels": {"0": {"1": 200, "2": 100}},
         "osc": [{"address": "/scene/open", "args": [1, 0.5]}]},
        {"label": "cross", "fade": 2.0, "levels": {"0": {"2": 255}}},
    ])
    seq_state = {}

    # GO cue 1: first tick carries the OSC trigger + the k=0 DMX frame
    e.go(0.0)
    send_events(e.tick(0.0), artnet_addr, osc_addr, seq_state)
    osc_pkt = oscsrv.recv(2048)
    assert osc_pkt.startswith(P._osc_string("/scene/open") + P._osc_string(",if"))
    seq, uni, dmx = parse_artnet(node.recv(2048))
    assert (seq, uni) == (1, 0) and dmx[:2] == b"\x00\x00", (seq, uni, dmx[:2])

    # halfway through the 2 s fade: ch1=100, ch2=50, sequence advanced
    send_events(e.tick(1.0), artnet_addr, osc_addr, seq_state)
    seq, uni, dmx = parse_artnet(node.recv(2048))
    assert (seq, uni) == (2, 0) and dmx[:2] == b"\x64\x32", (seq, dmx[:2])

    # fade complete: the full look
    send_events(e.tick(2.0), artnet_addr, osc_addr, seq_state)
    seq, _, dmx = parse_artnet(node.recv(2048))
    assert dmx[:2] == b"\xc8\x64", dmx[:2]

    # GO cue 2, land it: ch1 drops to 0 (tracking off), ch2 rises to 255
    e.go(10.0)
    send_events(e.tick(12.0), artnet_addr, osc_addr, seq_state)
    _, _, dmx = parse_artnet(node.recv(2048))
    assert dmx[:2] == b"\x00\xff", dmx[:2]

    # RELEASE to black
    e.release(20.0, fade=1.0)
    send_events(e.tick(21.0), artnet_addr, osc_addr, seq_state)
    _, _, dmx = parse_artnet(node.recv(2048))
    assert dmx[:2] == b"\x00\x00", dmx[:2]
    assert e.active is False

    node.close(); oscsrv.close()
    print("OK show over the wire (OSC + Art-Net virtual node)")


def test_sequence_wraps_at_255():
    seq_state = {0: 254}
    node, port = make_listener()
    send_events([("dmx", 0, [1])], ("127.0.0.1", port), None, seq_state)
    send_events([("dmx", 0, [1])], ("127.0.0.1", port), None, seq_state)
    s1, _, _ = parse_artnet(node.recv(2048))
    s2, _, _ = parse_artnet(node.recv(2048))
    assert (s1, s2) == (255, 1), (s1, s2)   # wraps 255 -> 1, never 0
    node.close()
    print("OK sequence wraps 255 -> 1")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
    print("\nALL %d PASSED" % len(fns))
