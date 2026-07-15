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
"""

import socket

from plugins.base import PluginBase

from .protocols import (
    ARTNET_PORT,
    SACN_PORT,
    build_artnet_dmx,
    build_osc_message,
    build_sacn_dmx,
    sacn_multicast_ip,
    valid_host,
)


class ShowControlPlugin(PluginBase):
    """OSC / Art-Net / sACN sender exposed over the xio HTTP API."""

    plugin_id = "showcontrol"
    name = "Show Control"
    version = "1.0.0"
    description = "Send OSC, Art-Net and sACN/E1.31 DMX from the phone over the LAN"
    author = "Cauce"
    icon = "network"
    category = "network"
    permissions = ["network"]

    def on_load(self):
        self._sent = {"osc": 0, "artnet": 0, "sacn": 0}
        self._last_error = None
        self.register_route("/status", self._api_status, methods=["GET"])
        self.register_route("/osc", self._api_osc, methods=["POST"])
        self.register_route("/artnet", self._api_artnet, methods=["POST"])
        self.register_route("/sacn", self._api_sacn, methods=["POST"])
        self.logger.info("%s loaded (OSC/Art-Net/sACN sender)" % self.name)

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
            "protocols": ["osc", "artnet", "sacn"],
            "sent": self._sent,
            "last_error": self._last_error,
            "artnet_port": ARTNET_PORT,
            "sacn_port": SACN_PORT,
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


# The plugin loader (xio/new-plugins/__init__.py) requires this export.
plugin_class = ShowControlPlugin
