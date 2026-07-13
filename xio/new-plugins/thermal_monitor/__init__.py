"""
Thermal Monitor Pro – Monitoreo de temperatura por zonas.
"""

from plugins.base import PluginBase
import json
from datetime import datetime


class ThermalMonitorPlugin(PluginBase):
    plugin_id = "thermal_monitor"
    name = "Thermal Monitor Pro"
    version = "1.0.0"
    description = "Monitoreo termico por zonas"
    author = "Arena Agent"
    icon = "battery"
    category = "battery"
    permissions = ["system", "battery"]

    def __init__(self, context):
        super().__init__(context)
        self._history = []
        self._alerts = []
        self._max_history = 2880

    def on_load(self):
        self._load_history()
        self.register_route("/temperatures", self._api_temperatures, methods=["GET"])
        self.register_route("/history", self._api_history, methods=["GET"])
        self.register_route("/alerts", self._api_alerts, methods=["GET"])
        self.register_route("/zones", self._api_zones, methods=["GET"])
        self.register_route("/config", self._api_get_config, methods=["GET"])
        self.register_route("/config", self._api_set_config, methods=["POST"])
        self.context.schedule("thermal_poll", self._poll_temperatures, interval_seconds=30)
        self.logger.info("Thermal Monitor Pro loaded")

    def _load_history(self):
        f = self.data_dir / "thermal_history.json"
        if f.exists():
            try:
                self._history = json.loads(f.read_text())
            except:
                self._history = []

    def _save_history(self):
        f = self.data_dir / "thermal_history.json"
        f.write_text(json.dumps(self._history[-self._max_history:], indent=2))

    def _read_thermal_zones(self):
        zones = {}
        try:
            out = self.controller._shell("ls", "/sys/class/thermal/")
            for zone in out.split():
                if zone.startswith("thermal_zone"):
                    num = zone.replace("thermal_zone", "")
                    temp_raw = self.controller._shell("cat", f"/sys/class/thermal/{zone}/temp")
                    ztype = self.controller._shell("cat", f"/sys/class/thermal/{zone}/type")
                    if temp_raw and temp_raw.lstrip('-').isdigit():
                        temp_c = int(temp_raw) / 1000.0
                        zones[ztype or f"zone{num}"] = round(temp_c, 1)
        except Exception as e:
            self.logger.error(f"Error reading thermal zones: {e}")
        try:
            bat = self.controller.battery_status()
            if "temperature" in bat:
                zones["battery"] = bat["temperature"]
        except:
            pass
        return zones

    def _check_throttling(self):
        try:
            out = self.controller._shell("cat", "/sys/class/thermal/thermal_zone0/throttle_state")
            return int(out.strip()) if out and out.strip().isdigit() else 0
        except:
            return None

    def _poll_temperatures(self):
        try:
            temps = self._read_thermal_zones()
            throttle = self._check_throttling()
            entry = {"timestamp": datetime.now().isoformat(), "temperatures": temps, "throttle_state": throttle}
            self._history.append(entry)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]
            self._save_history()
            threshold = self.get_config("alert_threshold", 40.0)
            for zone, temp in temps.items():
                if temp > threshold:
                    if not self._alerts or self._alerts[-1].get("zone") != zone:
                        self._alerts.append({"zone": zone, "temperature": temp, "threshold": threshold, "timestamp": entry["timestamp"]})
                        self._alerts = self._alerts[-50:]
        except Exception as e:
            self.logger.error(f"Thermal poll error: {e}")

    def _api_temperatures(self):
        from flask import jsonify
        return jsonify({"temperatures": self._read_thermal_zones(), "throttle_state": self._check_throttling(), "timestamp": datetime.now().isoformat()})

    def _api_history(self):
        from flask import request, jsonify
        minutes = int(request.args.get("minutes", 30))
        idx = max(0, len(self._history) - (minutes * 2))
        return jsonify(self._history[idx:])

    def _api_alerts(self):
        from flask import jsonify
        return jsonify(self._alerts[-20:])

    def _api_zones(self):
        from flask import jsonify
        try:
            out = self.controller._shell("ls", "/sys/class/thermal/")
            zones = []
            for z in out.split():
                if z.startswith("thermal_zone"):
                    zt = self.controller._shell("cat", f"/sys/class/thermal/{z}/type")
                    zones.append({"name": z, "type": zt})
            return jsonify(zones)
        except Exception as e:
            return jsonify({"error": str(e)})

    def _api_get_config(self):
        from flask import jsonify
        return jsonify({"alert_threshold": self.get_config("alert_threshold", 40.0)})

    def _api_set_config(self):
        from flask import request, jsonify
        data = request.get_json(force=True)
        if "alert_threshold" in data:
            self.set_config("alert_threshold", float(data["alert_threshold"]))
        return jsonify({"ok": True})


plugin_class = ThermalMonitorPlugin
