"""
Privacy Auditor – Auditoría de privacidad sin root para Android
Usa appops para permisos granulares y dumpsys para detectar acceso a sensores.
"""

from plugins.base import PluginBase
import time, json
from datetime import datetime


class PrivacyAuditorPlugin(PluginBase):
    plugin_id = "privacy_auditor"
    name = "Privacy Auditor"
    version = "1.0.0"
    description = "Auditoría de privacidad: appops, permisos, alertas"
    author = "Arena Agent"
    icon = "system"
    category = "system"
    permissions = ["apps", "system"]

    # Permisos sensibles monitorizados
    SENSITIVE_OPS = [
        "camera",                    # Android 10+
        "record_audio",              # Micrófono
        "coarse_location",           # Ubicación aproximada
        "fine_location",             # Ubicación precisa
        "read_contacts",             # Contactos
        "read_call_log",             # Historial de llamadas
        "read_sms",                  # SMS
        "receive_sms",               # Recibir SMS
        "send_sms",                  # Enviar SMS
        "read_phone_state",          # Estado del teléfono
        "read_external_storage",     # Almacenamiento
        "write_external_storage",
        "android:get_usage_stats",   # Estadísticas de uso
    ]

    # Modos de appops
    MODES = {
        "allow": 0,       # Permitido
        "ignore": 1,      # Ignorado (simula permitido pero no hace nada)
        "deny": 2,        # Denegado (app puede crashear)
        "default": 3,     # Comportamiento por defecto
    }

    def __init__(self, context):
        super().__init__(context)
        self._last_scan = None
        self._alerts = []

    def on_load(self):
        self.register_route("/audit", self._api_audit, methods=["GET"])
        self.register_route("/audit/<package>", self._api_audit_package, methods=["GET"])
        self.register_route("/revoke", self._api_revoke, methods=["POST"])
        self.register_route("/grant", self._api_grant, methods=["POST"])
        self.register_route("/reset", self._api_reset, methods=["POST"])
        self.register_route("/alerts", self._api_alerts, methods=["GET"])
        self.register_route("/scan", self._api_scan, methods=["POST"])
        self.register_route("/report", self._api_report, methods=["GET"])
        # Background scan cada 5 minutos
        self.context.schedule("privacy_scan", self._background_scan, interval_seconds=300)
        self.logger.info("Privacy Auditor loaded")

    def _run_appops(self, *args):
        try:
            return self.controller._shell("appops", *args)
        except Exception as e:
            self.logger.error(f"appops error: {e}")
            return ""

    def _get_package_perms(self, package):
        """Get permission status via appops for a package."""
        out = self._run_appops("get", package)
        perms = {}
        current_op = None
        for line in out.splitlines():
            line = line.strip()
            for op in self.SENSITIVE_OPS:
                if op in line:
                    current_op = op
                    mode = "unknown"
                    if "allow" in line.lower():
                        mode = "allow"
                    elif "ignore" in line.lower():
                        mode = "ignore"
                    elif "deny" in line.lower():
                        mode = "deny"
                    perms[op] = {"mode": mode, "raw": line}
                    break
        return perms

    def _set_op(self, package, op, mode):
        """Set appops permission."""
        mode_num = self.MODES.get(mode, mode)
        try:
            self._run_appops("set", package, op, str(mode_num))
            return True
        except Exception as e:
            self.logger.error(f"Error setting {op} for {package}: {e}")
            return False

    def _get_installed_packages(self):
        """Get list of user-installed packages (non-system)."""
        try:
            out = self.controller._shell("pm", "list", "packages", "-3")
            return [line.replace("package:", "").strip() for line in out.splitlines() if line.strip()]
        except Exception:
            return []

    def _background_scan(self):
        """Background scan to detect permission usage changes."""
        try:
            packages = self._get_installed_packages()
            suspicious = []
            for pkg in packages[:50]:  # Limitar para no demorar
                perms = self._get_package_perms(pkg)
                for op, info in perms.items():
                    if op in ["camera", "record_audio", "fine_location"] and info["mode"] == "allow":
                        # App con permisos sensibles - checkear si está en background
                        suspicious.append({
                            "package": pkg,
                            "permission": op,
                            "timestamp": datetime.now().isoformat()
                        })
            
            if suspicious:
                self._alerts.append({
                    "type": "sensitive_permission",
                    "message": f"{len(suspicious)} apps con permisos sensibles activos",
                    "details": suspicious[:5],
                    "timestamp": datetime.now().isoformat()
                })
                if len(self._alerts) > 100:
                    self._alerts = self._alerts[-100:]
            
            self._last_scan = datetime.now().isoformat()
        except Exception as e:
            self.logger.error(f"Background scan error: {e}")

    # ── API Endpoints ────────────────────────────────────────────────

    def _api_audit(self):
        """GET /api/plugins/privacy_auditor/audit
        Full audit of all user-installed apps.
        """
        from flask import jsonify
        packages = self._get_installed_packages()
        results = []
        for pkg in packages[:100]:  # Limit for performance
            perms = self._get_package_perms(pkg)
            has_sensitive = any(op in perms for op in ["camera", "record_audio", "fine_location", "read_sms"])
            results.append({
                "package": pkg,
                "permissions": perms,
                "has_sensitive": has_sensitive,
                "sensitive_count": sum(1 for op in perms if op in ["camera", "record_audio", "fine_location", "read_sms", "send_sms"])
            })
        # Sort by sensitivity
        results.sort(key=lambda x: -x["sensitive_count"])
        return jsonify({
            "apps": results,
            "total": len(packages),
            "audited": len(results),
            "last_scan": self._last_scan
        })

    def _api_audit_package(self, package):
        """GET /api/plugins/privacy_auditor/audit/<package>"""
        from flask import jsonify
        perms = self._get_package_perms(package)
        return jsonify({
            "package": package,
            "permissions": perms,
            "sensitive_ops": self.SENSITIVE_OPS
        })

    def _api_revoke(self):
        """POST /api/plugins/privacy_auditor/revoke"""
        from flask import request, jsonify
        data = request.get_json(force=True)
        package = data.get("package", "")
        permission = data.get("permission", "")
        if not package or not permission:
            return jsonify({"error": "package and permission required"}), 400
        success = self._set_op(package, permission, "ignore")
        self._alerts.append({
            "type": "permission_revoked",
            "message": f"Revocado {permission} de {package}",
            "timestamp": datetime.now().isoformat()
        })
        return jsonify({"ok": success, "package": package, "permission": permission, "mode": "ignore"})

    def _api_grant(self):
        """POST /api/plugins/privacy_auditor/grant"""
        from flask import request, jsonify
        data = request.get_json(force=True)
        package = data.get("package", "")
        permission = data.get("permission", "")
        if not package or not permission:
            return jsonify({"error": "package and permission required"}), 400
        success = self._set_op(package, permission, "allow")
        return jsonify({"ok": success, "package": package, "permission": permission, "mode": "allow"})

    def _api_reset(self):
        """POST /api/plugins/privacy_auditor/reset"""
        from flask import request, jsonify
        data = request.get_json(force=True)
        package = data.get("package", "")
        permission = data.get("permission", "")
        if not package or not permission:
            return jsonify({"error": "package and permission required"}), 400
        success = self._set_op(package, permission, "default")
        return jsonify({"ok": success, "package": package, "permission": permission, "mode": "default"})

    def _api_alerts(self):
        """GET /api/plugins/privacy_auditor/alerts"""
        from flask import jsonify
        return jsonify(self._alerts[-50:])

    def _api_scan(self):
        """POST /api/plugins/privacy_auditor/scan - trigger manual scan"""
        from flask import jsonify
        self._background_scan()
        return jsonify({"ok": True, "last_scan": self._last_scan, "alerts": len(self._alerts)})

    def _api_report(self):
        """GET /api/plugins/privacy_auditor/report - risk summary"""
        from flask import jsonify
        packages = self._get_installed_packages()
        high_risk = []
        medium_risk = []
        for pkg in packages[:100]:
            perms = self._get_package_perms(pkg)
            sensitive = [op for op in perms if op in ["camera", "record_audio", "fine_location", "read_sms", "send_sms"]]
            if len(sensitive) >= 3:
                high_risk.append({"package": pkg, "count": len(sensitive), "perms": sensitive})
            elif len(sensitive) >= 1:
                medium_risk.append({"package": pkg, "count": len(sensitive), "perms": sensitive})
        return jsonify({
            "high_risk": high_risk[:20],
            "medium_risk": medium_risk[:20],
            "total_scanned": len(packages),
            "last_scan": self._last_scan
        })


plugin_class = PrivacyAuditorPlugin
