"""Versión y changelog de flujo."""
__version__ = "0.23.0"
VERSION = __version__
__version_info__ = (0, 23, 0)
def get_version(): return __version__
def get_changelog():
    return {
        "0.23.0": {"titulo": "Airdrop Status Command", "fecha": "2026-06-18", "highlights": ["Añadido flujo airdrop status", "Sincronización de versión global"]},
        "0.20.0": {"titulo": "Zero-Friction Airdrop System", "fecha": "2026-06-18", "highlights": ["Sistema de Airdrop automatizado", "Auto-checkpoint + Push"]}
    }
