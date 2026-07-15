"""
showcontrol -- OSC + Art-Net + sACN (E1.31) network show control from the phone.

Turns the on-device xio server into a network show-control node: it emits OSC
messages (Resolume/QLab/consoles), Art-Net DMX and sACN/E1.31 DMX over the hotspot
LAN. Pure stdlib (socket + struct): no pip on Termux, and no shell is ever invoked
-- zero command-injection surface. Packet builders live in protocols.py and are
unit-tested off-device (test_protocols.py).

v1 is SEND-only (the core need to drive lights/VJ from the phone). Receiving OSC to
trigger xio actions is a deliberate v2 (needs a guarded background listener).
Physical DMX512 out (USB-DMX dongle) is out of scope on non-root Android -- drive a
network Art-Net/sACN node instead.

v1.1 adds the CUE ENGINE (cueengine.py): a cue list with timed crossfades and
GO / STOP / RELEASE transport -- the `orq` grow point of cultura/xio-concept.html.
The 30 Hz tick thread only runs while a show is live (battery discipline) and
stops itself once RELEASE lands at black.
"""

import socket
import threading
import time

from plugins.base import PluginBase

from .cueengine import CueEngine, CueError
from .fabric import Fabric, FabricError
from .panel import PANEL_HTML
from .protocols import (
    ARTNET_PORT,
    SACN_PORT,
    build_artnet_dmx,
    build_magic_packet,
    build_osc_message,
    build_sacn_dmx,
    sacn_multicast_ip,
    valid_host,
)

TICK_HZ = 30.0


class ShowControlPlugin(PluginBase):
    """OSC / Art-Net / sACN sender exposed over the xio HTTP API."""

    plugin_id = "showcontrol"
    name = "Show Control"
    version = "1.2.0"
    description = "Send OSC, Art-Net and sACN/E1.31 DMX from the phone over the LAN"
    author = "Cauce"
    icon = "network"
    category = "network"
    permissions = ["network"]

    def on_load(self):
        self._sent = {"osc": 0, "artnet": 0, "sacn": 0}
        self._last_error = None
        self._engine = CueEngine()
        self._cue_output = None
        self._seq = {}                      # {universe: last sequence 1..255}
        self._cue_stop = threading.Event()
        self._cue_thread = None
        self._cue_thread_lock = threading.Lock()
        self.register_route("/status", self._api_status, methods=["GET"])
        self.register_route("/osc", self._api_osc, methods=["POST"])
        self.register_route("/artnet", self._api_artnet, methods=["POST"])
        self.register_route("/sacn", self._api_sacn, methods=["POST"])
        self.register_route("/cues", self._api_cues, methods=["GET", "POST"])
        self.register_route("/cue/go", self._api_cue_go, methods=["POST"])
        self.register_route("/cue/stop", self._api_cue_stop, methods=["POST"])
        self.register_route("/cue/release", self._api_cue_release, methods=["POST"])
        self.register_route("/cue/state", self._api_cue_state, methods=["GET"])
        self.register_route("/panel", self._api_panel, methods=["GET"])
        self.register_route("/wol", self._api_wol, methods=["POST"])
        self._fabric = Fabric()
        self._fabric_output = None
        self._fabric_stop = threading.Event()
        self._fabric_thread = None
        self._fabric_thread_lock = threading.Lock()
        self.register_route("/fabric", self._api_fabric, methods=["GET", "POST"])
        self.register_route("/fabric/set", self._api_fabric_set, methods=["POST"])
        self.register_route("/fabric/state", self._api_fabric_state, methods=["GET"])
        # Re-arm a persisted show (list only -- never auto-runs anything).
        saved = self.get_config("cuelist")
        if saved:
            try:
                self._engine.load(saved)
                self._cue_output = self._valid_output(self.get_config("cue_output") or {})
            except (CueError, ValueError) as e:
                self.logger.warning("showcontrol: persisted cue list ignored: %s" % e)
        self.logger.info("%s loaded (OSC/Art-Net/sACN + cue engine)" % self.name)

    def on_unload(self):
        self._cue_stop.set()
        self._fabric_stop.set()

    # ── sender ────────────────────────────────────────────────────────────
    def _send_udp(self, packet, host, port, multicast=False):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            if multicast:
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 8)
            sock.sendto(packet, (host, port))
        finally:
            sock.close()

    # ── API ───────────────────────────────────────────────────────────────
    def _api_status(self):
        from flask import jsonify
        return jsonify({
            "name": self.name,
            "version": self.version,
            "protocols": ["osc", "artnet", "sacn", "cues"],
            "sent": self._sent,
            "last_error": self._last_error,
            "artnet_port": ARTNET_PORT,
            "sacn_port": SACN_PORT,
            "cue": self._engine.status(),
        })

    def _api_osc(self):
        from flask import request, jsonify
        d = request.get_json(force=True, silent=True) or {}
        host, port = d.get("host"), d.get("port", 9000)
        address, args = d.get("address", ""), d.get("args", [])
        if not valid_host(host):
            return jsonify({"ok": False, "error": "invalid host (need IPv4)"}), 400
        if not isinstance(port, int) or not (1 <= port <= 65535):
            return jsonify({"ok": False, "error": "invalid port"}), 400
        if not isinstance(args, list):
            return jsonify({"ok": False, "error": "args must be a list"}), 400
        try:
            pkt = build_osc_message(address, args)
        except ValueError as e:
            return jsonify({"ok": False, "error": str(e)}), 400
        try:
            self._send_udp(pkt, host, port)
        except OSError as e:
            self._last_error = "osc: %s" % e
            return jsonify({"ok": False, "error": str(e)}), 502
        self._sent["osc"] += 1
        return jsonify({"ok": True, "sent_bytes": len(pkt), "to": "%s:%d" % (host, port)})

    def _api_artnet(self):
        from flask import request, jsonify
        d = request.get_json(force=True, silent=True) or {}
        host, port = d.get("host"), d.get("port", ARTNET_PORT)
        universe = d.get("universe", 0)
        data = d.get("data", d.get("channels"))
        if not valid_host(host):
            return jsonify({"ok": False, "error": "invalid host (need IPv4)"}), 400
        if not isinstance(port, int) or not (1 <= port <= 65535):
            return jsonify({"ok": False, "error": "invalid port"}), 400
        if data is None:
            return jsonify({"ok": False, "error": "missing 'data' (list) or 'channels' (object)"}), 400
        try:
            pkt = build_artnet_dmx(int(universe), data)
        except (ValueError, TypeError) as e:
            return jsonify({"ok": False, "error": str(e)}), 400
        try:
            self._send_udp(pkt, host, port)
        except OSError as e:
            self._last_error = "artnet: %s" % e
            return jsonify({"ok": False, "error": str(e)}), 502
        self._sent["artnet"] += 1
        return jsonify({"ok": True, "sent_bytes": len(pkt), "universe": int(universe),
                        "to": "%s:%d" % (host, port)})

    def _api_sacn(self):
        from flask import request, jsonify
        d = request.get_json(force=True, silent=True) or {}
        universe = d.get("universe")
        data = d.get("data", d.get("channels"))
        host = d.get("host")            # optional: unicast; default is multicast
        priority, source = d.get("priority", 100), d.get("source", "xio")
        if universe is None or data is None:
            return jsonify({"ok": False, "error": "missing 'universe' or 'data'"}), 400
        if host is not None and not valid_host(host):
            return jsonify({"ok": False, "error": "invalid host (need IPv4)"}), 400
        try:
            pkt = build_sacn_dmx(int(universe), data, source_name=str(source), priority=int(priority))
        except (ValueError, TypeError) as e:
            return jsonify({"ok": False, "error": str(e)}), 400
        target = host or sacn_multicast_ip(int(universe))
        try:
            self._send_udp(pkt, target, SACN_PORT, multicast=(host is None))
        except OSError as e:
            self._last_error = "sacn: %s" % e
            return jsonify({"ok": False, "error": str(e)}), 502
        self._sent["sacn"] += 1
        return jsonify({"ok": True, "sent_bytes": len(pkt), "universe": int(universe),
                        "to": "%s:%d" % (target, SACN_PORT),
                        "mode": "unicast" if host else "multicast"})

    # ── cue engine: output config ─────────────────────────────────────────
    def _valid_output(self, d):
        """Validate {protocol, host, port, osc_host, osc_port}; raise ValueError."""
        if not isinstance(d, dict):
            raise ValueError("output must be an object")
        proto = d.get("protocol", "artnet")
        if proto not in ("artnet", "sacn"):
            raise ValueError("output.protocol must be 'artnet' or 'sacn'")
        host = d.get("host")
        if proto == "artnet" and not valid_host(host):
            raise ValueError("output.host (IPv4) is required for artnet")
        if proto == "sacn" and host is not None and not valid_host(host):
            raise ValueError("output.host must be IPv4 (omit for sACN multicast)")
        port = d.get("port", ARTNET_PORT if proto == "artnet" else SACN_PORT)
        if not isinstance(port, int) or not (1 <= port <= 65535):
            raise ValueError("output.port invalid")
        osc_host, osc_port = d.get("osc_host"), d.get("osc_port", 9000)
        if osc_host is not None and not valid_host(osc_host):
            raise ValueError("output.osc_host must be IPv4")
        if not isinstance(osc_port, int) or not (1 <= osc_port <= 65535):
            raise ValueError("output.osc_port invalid")
        return {"protocol": proto, "host": host, "port": port,
                "osc_host": osc_host, "osc_port": osc_port}

    # ── cue engine: emitter + tick thread ─────────────────────────────────
    def _next_seq(self, universe):
        s = self._seq.get(universe, 0) + 1
        if s > 255:
            s = 1
        self._seq[universe] = s
        return s

    def _emit_events(self, events):
        out = self._cue_output
        for ev in events:
            try:
                if ev[0] == "osc":
                    if not out or not out.get("osc_host"):
                        continue                        # no OSC target configured
                    pkt = build_osc_message(ev[1], ev[2])
                    self._send_udp(pkt, out["osc_host"], out["osc_port"])
                    self._sent["osc"] += 1
                elif ev[0] == "dmx":
                    if not out:
                        continue
                    universe, levels = ev[1], ev[2]
                    seq = self._next_seq(universe)
                    if out["protocol"] == "artnet":
                        pkt = build_artnet_dmx(universe, levels, sequence=seq)
                        self._send_udp(pkt, out["host"], out["port"])
                        self._sent["artnet"] += 1
                    else:
                        pkt = build_sacn_dmx(universe, levels, sequence=seq)
                        target = out["host"] or sacn_multicast_ip(universe)
                        self._send_udp(pkt, target, out["port"],
                                       multicast=(out["host"] is None))
                        self._sent["sacn"] += 1
            except (ValueError, OSError) as e:
                self._last_error = "cue emit: %s" % e

    def _cue_loop(self):
        while not self._cue_stop.is_set():
            now = time.monotonic()
            try:
                self._emit_events(self._engine.tick(now))
            except Exception as e:                       # never kill the thread
                self._last_error = "cue tick: %s" % e
            if not self._engine.active:
                # show over -> save battery; recheck under the lock so a GO
                # racing this exit can't be left without a tick thread
                with self._cue_thread_lock:
                    if not self._engine.active:
                        self._cue_thread = None
                        return
            self._cue_stop.wait(1.0 / TICK_HZ)
        with self._cue_thread_lock:
            self._cue_thread = None

    def _ensure_cue_thread(self):
        with self._cue_thread_lock:
            if self._cue_thread is not None and self._cue_thread.is_alive():
                return
            self._cue_stop.clear()
            t = threading.Thread(target=self._cue_loop, daemon=True,
                                 name="showcontrol-cue")
            self._cue_thread = t
            t.start()

    # ── cue engine: API ───────────────────────────────────────────────────
    def _api_cues(self):
        from flask import request, jsonify
        if request.method == "GET":
            return jsonify({"ok": True,
                            "cues": [c.to_dict() for c in self._engine.cues],
                            "output": self._cue_output,
                            "state": self._engine.status()})
        d = request.get_json(force=True, silent=True) or {}
        try:
            output = self._valid_output(d.get("output") or {})
            count = self._engine.load(d.get("cues"))
        except (CueError, ValueError) as e:
            return jsonify({"ok": False, "error": str(e)}), 400
        self._cue_output = output
        self.set_config("cuelist", d.get("cues"))
        self.set_config("cue_output", output)
        return jsonify({"ok": True, "loaded": count, "output": output})

    def _api_cue_go(self):
        from flask import request, jsonify
        d = request.get_json(force=True, silent=True) or {}
        index = d.get("index")
        if index is not None and not isinstance(index, int):
            return jsonify({"ok": False, "error": "index must be an integer"}), 400
        if self._cue_output is None:
            return jsonify({"ok": False, "error": "no output configured (POST /cues first)"}), 400
        try:
            label = self._engine.go(time.monotonic(), index)
        except CueError as e:
            return jsonify({"ok": False, "error": str(e)}), 400
        self._ensure_cue_thread()
        return jsonify({"ok": True, "cue": label, "state": self._engine.status()})

    def _api_cue_stop(self):
        from flask import jsonify
        self._engine.stop(time.monotonic())
        return jsonify({"ok": True, "state": self._engine.status()})

    def _api_cue_release(self):
        from flask import request, jsonify
        d = request.get_json(force=True, silent=True) or {}
        try:
            self._engine.release(time.monotonic(), d.get("fade", 2.0))
        except CueError as e:
            return jsonify({"ok": False, "error": str(e)}), 400
        self._ensure_cue_thread()                       # ticks the fade-to-black
        return jsonify({"ok": True, "state": self._engine.status()})

    def _api_cue_state(self):
        from flask import jsonify
        return jsonify({"ok": True, "state": self._engine.status(),
                        "output": self._cue_output, "sent": self._sent})

    # ── signal fabric (the `fabric` node) ─────────────────────────────────
    def _emit_fabric(self, events):
        out = self._fabric_output
        for ev in events:
            try:
                if ev[0] == "osc":                       # route-local host/port
                    _, host, port, address, args = ev
                    self._send_udp(build_osc_message(address, args), host, port)
                    self._sent["osc"] += 1
                elif ev[0] == "dmx":
                    if not out:
                        continue
                    universe, levels = ev[1], ev[2]
                    seq = self._next_seq(universe)
                    if out["protocol"] == "artnet":
                        self._send_udp(build_artnet_dmx(universe, levels, sequence=seq),
                                       out["host"], out["port"])
                        self._sent["artnet"] += 1
                    else:
                        tgt = out["host"] or sacn_multicast_ip(universe)
                        self._send_udp(build_sacn_dmx(universe, levels, sequence=seq),
                                       tgt, out["port"], multicast=(out["host"] is None))
                        self._sent["sacn"] += 1
            except (ValueError, OSError) as e:
                self._last_error = "fabric emit: %s" % e

    def _fabric_loop(self):
        while not self._fabric_stop.is_set():
            now = time.monotonic()
            try:
                self._emit_fabric(self._fabric.keepalive(now))
            except Exception as e:
                self._last_error = "fabric tick: %s" % e
            if not self._fabric.active:
                with self._fabric_thread_lock:
                    if not self._fabric.active:
                        self._fabric_thread = None
                        return
            self._fabric_stop.wait(1.0 / TICK_HZ)
        with self._fabric_thread_lock:
            self._fabric_thread = None

    def _ensure_fabric_thread(self):
        with self._fabric_thread_lock:
            if self._fabric_thread is not None and self._fabric_thread.is_alive():
                return
            self._fabric_stop.clear()
            t = threading.Thread(target=self._fabric_loop, daemon=True,
                                 name="showcontrol-fabric")
            self._fabric_thread = t
            t.start()

    def _api_fabric(self):
        from flask import request, jsonify
        if request.method == "GET":
            return jsonify({"ok": True, "output": self._fabric_output,
                            "state": self._fabric.status()})
        d = request.get_json(force=True, silent=True) or {}
        try:
            output = self._valid_output(d.get("output") or {}) if d.get("output") else None
            info = self._fabric.load(d)
        except (FabricError, ValueError) as e:
            return jsonify({"ok": False, "error": str(e)}), 400
        # DMX routes need an output target; OSC-only fabrics don't
        if info["universes"] and output is None:
            return jsonify({"ok": False, "error": "DMX routes need an 'output' {protocol,host}"}), 400
        self._fabric_output = output
        self._ensure_fabric_thread()
        return jsonify({"ok": True, "loaded": info, "output": output})

    def _api_fabric_set(self):
        from flask import request, jsonify
        d = request.get_json(force=True, silent=True) or {}
        name, value = d.get("signal"), d.get("value")
        try:
            self._emit_fabric(self._fabric.set(name, value))
        except FabricError as e:
            return jsonify({"ok": False, "error": str(e)}), 400
        self._ensure_fabric_thread()
        return jsonify({"ok": True, "signal": name, "value": self._fabric.signals.get(name)})

    def _api_fabric_state(self):
        from flask import jsonify
        return jsonify({"ok": True, "state": self._fabric.status(),
                        "output": self._fabric_output, "sent": self._sent})

    # ── panel + wake-on-lan (xiotech M2) ──────────────────────────────────
    def _api_panel(self):
        from flask import Response
        return Response(PANEL_HTML, mimetype="text/html")

    def _api_wol(self):
        """Send a WoL magic packet; optionally verify a TCP service comes up
        (xiotech M2: 'verificacion de puerto de servicio, no solo ping')."""
        from flask import request, jsonify
        d = request.get_json(force=True, silent=True) or {}
        broadcast = d.get("broadcast", "255.255.255.255")
        verify_host, verify_port = d.get("verify_host"), d.get("verify_port")
        timeout = d.get("timeout", 20)
        try:
            pkt = build_magic_packet(d.get("mac"))
        except ValueError as e:
            return jsonify({"ok": False, "error": str(e)}), 400
        if not valid_host(broadcast):
            return jsonify({"ok": False, "error": "invalid broadcast address"}), 400
        if verify_port is not None:
            if not isinstance(verify_port, int) or not (1 <= verify_port <= 65535):
                return jsonify({"ok": False, "error": "invalid verify_port"}), 400
            if not valid_host(verify_host):
                return jsonify({"ok": False, "error": "verify_port needs a valid verify_host"}), 400
        if not isinstance(timeout, (int, float)) or not (1 <= timeout <= 120):
            return jsonify({"ok": False, "error": "timeout out of range 1..120 s"}), 400
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            for _ in range(3):                       # WoL is fire-and-forget; repeat
                sock.sendto(pkt, (broadcast, 9))
        except OSError as e:
            self._last_error = "wol: %s" % e
            return jsonify({"ok": False, "error": str(e)}), 502
        finally:
            sock.close()
        if verify_port is None:
            return jsonify({"ok": True, "sent": 3, "verified": None})
        deadline = time.monotonic() + float(timeout)
        up = False
        while time.monotonic() < deadline and not up:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2.0)
            try:
                up = s.connect_ex((verify_host, verify_port)) == 0
            finally:
                s.close()
            if not up:
                time.sleep(1.0)
        return jsonify({"ok": True, "sent": 3, "verified": up,
                        "service": "%s:%d" % (verify_host, verify_port)})


# The plugin loader (xio/new-plugins/__init__.py) requires this export.
plugin_class = ShowControlPlugin
