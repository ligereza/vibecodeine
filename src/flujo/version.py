"""Versión y changelog de flujo."""

__version__ = "0.20.0"
VERSION = __version__
__version_info__ = (0, 20, 0)

def get_version():
    return __version__

def get_changelog():
    return {
        "0.20.0": {
            "titulo": "Zero-Friction Airdrop System",
            "fecha": "2026-06-18",
            "highlights": [
                "Sistema de Airdrop automatizado (Apply -> Checkpoint -> Push)",
                "Eliminación de scripts de Bash manuales para actualizaciones",
                "Integración de auto-checkpoint en la CLI",
                "Sistema de Rollback mejorado con backups temporales"
            ]
        },
        "0.16.0": {
            "titulo": "CLI Completo + Pipeline Unificado",
            "fecha": "2026-06-17",
            "highlights": [
                "CLI unificada con 25+ comandos",
                "Pipeline completo de jobs: correo → brief → proyecto → render",
                "Módulos nuevos: jobs, privacy, render, dashboard",
                "Track M (integración directa PS/AI desde palette.json)",
                "Sistema de airdrop profesional",
                "Privacidad integrada (Ley 21.719)",
                "~30 tests añadidos"
            ]
        },
        "0.15.0": {
            "titulo": "Avance completo (Intake Inteligente + Track M + Airdrop)",
            "fecha": "2026-06-17",
            "highlights": [
                "CLI unificado (flujo)",
                "Intake inteligente de correos",
                "Track M (integración directa PS/AI)",
                "Sistema de airdrop profesional",
                "Limpieza estructural"
            ]
        },
        "0.14.0": {
            "titulo": "Analisis + Index + Export",
            "fecha": "2026-06-16",
            "highlights": [
                "Análisis de colores dominantes",
                "Índice SQLite de flyers",
                "Exportación ZIP con scripts JSX"
            ]
        }
    }
