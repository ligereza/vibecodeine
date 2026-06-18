"""Versión y changelog de flujo."""
__version__ = "0.30.2"
VERSION = __version__
__version_info__ = (0, 30, 2)
def get_version(): return __version__
def get_changelog():
    return {
        "0.30.2": {"titulo": "IG: usuario en URL + descarga + paleta en el editor", "fecha": "2026-06-18", "highlights": ["Detecta instagram.com/<usuario>/p/CODE/ (formato real)", "Pestaña INSTAGRAM: descargar post (instaloader) + extraer paleta de colores", "Botón 'Aplicar paleta a la pieza' conecta IG con el editor", "Muestra la imagen descargada y avisos privado/video"]},
        "0.30.1": {"titulo": "Fixes editor: IG sin esquema, preview responsive, orientación", "fecha": "2026-06-18", "highlights": ["IG sin https://", "preview responsive", "formatos verticales correctos"]},
        "0.30.0": {"titulo": "Auto-fit de texto + avisos IG + acuse de recibo", "fecha": "2026-06-18", "highlights": ["Auto-fit de texto (respeta 'locked')", "pestañas INSTAGRAM y ACUSE DE RECIBO"]},
        "0.29.0": {"titulo": "Auto-checkpoint en Python puro (fix Windows/bash)", "fecha": "2026-06-18", "highlights": ["run_auto_checkpoint sin bash"]},
        "0.28.0": {"titulo": "Editor visual Gradio (src/flujo/web)", "fecha": "2026-06-18", "highlights": ["Editor: catálogo → datos/proporción → preview SVG → exportar"]},
        "0.27.0": {"titulo": "Catálogo oficial de formatos ONG (v2.0)", "fecha": "2026-06-18", "highlights": ["12 formatos con area/medio/herramienta"]},
        "0.26.0": {"titulo": "Render rescale + bloque modificacion", "fecha": "2026-06-18", "highlights": ["flujo render rescale (proporción/DPI)"]},
        "0.25.0": {"titulo": "README maestro + Intake JSON spec", "fecha": "2026-06-18", "highlights": ["intake JSON + schema"]},
        "0.24.0": {"titulo": "Fix Airdrop CLI", "fecha": "2026-06-18", "highlights": ["Reparados comandos airdrop"]},
        "0.20.0": {"titulo": "Zero-Friction Airdrop System", "fecha": "2026-06-18", "highlights": ["Airdrop automatizado + push"]}
    }
