"""Versión y changelog de flujo."""
__version__ = "0.27.0"
VERSION = __version__
__version_info__ = (0, 27, 0)
def get_version(): return __version__
def get_changelog():
    return {
        "0.27.0": {"titulo": "Catálogo oficial de formatos ONG (v2.0)", "fecha": "2026-06-18", "highlights": ["INDEX_FORMATOS v2.0: 12 formatos reales con area/medio/herramienta/parametrico", "Eventos (correo) y Suplementos (whatsapp); regla Illustrator=impresión, Photoshop=digital, Blender=carteleras", "flujo render formats con filtros -a/-m/--herramienta", "Pendones/banderas paramétricos; carteleras con campos a inferir", "docs/CATALOGO_FORMATOS.md + docs/BLENDER_FLYERS.md + 13 tests nuevos"]},
        "0.26.0": {"titulo": "Render rescale + bloque modificacion", "fecha": "2026-06-18", "highlights": ["flujo render rescale (proporción/DPI)", "bloque modificacion en intake JSON"]},
        "0.25.0": {"titulo": "README maestro + Intake JSON spec", "fecha": "2026-06-18", "highlights": ["README guía para agentes", "intake JSON + schema + ejemplos"]},
        "0.24.1": {"titulo": "Fix Airdrop rutas Windows", "fecha": "2026-06-18", "highlights": ["scan_airdrop() usa rel.as_posix()"]},
        "0.24.0": {"titulo": "Fix Airdrop CLI", "fecha": "2026-06-18", "highlights": ["Reparados los comandos flujo airdrop", "Versión centralizada", "Tests de regresión"]},
        "0.20.0": {"titulo": "Zero-Friction Airdrop System", "fecha": "2026-06-18", "highlights": ["Sistema de Airdrop automatizado", "Auto-checkpoint + Push"]}
    }
