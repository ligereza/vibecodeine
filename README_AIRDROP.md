# AIRDROP - flujo instaloader-only

Fecha: 2026-06-16

Este airdrop elimina yt-dlp completamente del repo, dejando solo instaloader para descargas de Instagram.

## Archivos incluidos

1. `requirements.txt`
   - ELIMINADO: `yt-dlp>=2024.5.0`
   - Quedan: matplotlib, pyyaml, gradio, instaloader
   - Instalación ligera: ~50 MB, no 400 MB

2. `scripts/ig_download.py`
   - Eliminado fallback `download_with_ytdlp()`
   - Solo instaloader
   - API 100% compatible: `download_post(url, output_dir)` devuelve el mismo dict
   - MEJORAS:
     - Guarda TODAS las imágenes del carrusel: `input_ig.jpg`, `input_ig_2.jpg`, `input_ig_3.jpg`...
     - Guarda caption en `ig_caption.txt`
     - media_type detecta `carousel` correctamente
     - Mensajes de error más claros: `login_requerido_o_privado`, `post_no_encontrado`
     - Devuelve owner y date en el resultado

## Aplicar

```bash
bash scripts/apply_airdrop.sh --dry-run
bash scripts/apply_airdrop.sh --apply
```

Luego instalar dependencias limpias:
```bash
python -m pip uninstall -y yt-dlp
python -m pip install -r requirements.txt
```

## Test rápido

```bash
python scripts/ig_download.py "https://www.instagram.com/p/XXXX/" ./tmp_test
```

## Compatibilidad

- `scripts/flyer_from_email.py` funciona igual, sin cambios
- manifest.json mantiene el mismo formato
- tests smoke pasan

--
flujo - Dimensiones del Orden
