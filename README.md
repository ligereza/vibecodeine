<pre>
╔════════════════════════════════════════════════════════════╗
║                                                          ║
║          flujo  ·  Dimensiones del Orden                 ║
║                                                          ║
║          arte  +  automatización                        ║
║                                                          ║
╚════════════════════════════════════════════════════════════╝

  Ver tapiz completo: docs/TAPIZ.md
</pre>

# flujo — arte y automatización

Un tapiz donde los proyectos respiran, las IAs ordenan, y nada empieza desde cero.

`flujo` junta arte, código e IAs para proyectos creativos. No reemplaza la mano del diseñador. Guarda contexto, inputs, checkpoints.

## Instalación

```bash
py -m pip install -e .
# o
py -m pip install -r requirements.txt
```

Linux/macOS: usa `python3` en lugar de `py`

Dependencias: `matplotlib / pyyaml / gradio / instaloader / pydantic / typer / rich`

**Sin yt-dlp. Sin venvs de 400 MB.**

## Uso rápido

```bash
# CLI unificado
flujo health
flujo flyer-import inbox/correo.txt
flujo ig-redownload
flujo analyze              # colores + OCR
flujo index --rebuild      # índice SQLite
flujo export projects/flyer_eventos/2026-06-16_ig_XXXX  # ZIP para PS
flujo app

# Compatibilidad legacy
py scripts/flyer_from_email.py "inbox/correo_prueba.txt"
bash scripts/flyer_list.sh
bash scripts/flyer_status_latest.sh
```

## Herramienta activa

`flyer_eventos` — importar desde Instagram, descarga automática con **instaloader únicamente**.

Archivos descargados:
- `input/input_ig.jpg`, `input_ig_2.jpg` …
- `input/input_ig_video.mp4`
- `input/ig_caption.txt`

Análisis automático:
- `analysis/palette.json` + `palette.png`
- `analysis/palette.aco` / `palette.ase` – Photoshop / Illustrator
- `analysis/ocr.txt` (opcional, requiere pytesseract)
- Ver `docs/ANALISIS.md`

## Piezas vectoriales

Para etiquetas / Illustrator / impresión:
```
tools/piezas_vectoriales/SPEC.md
py -m flujo render projects/piezas_vectoriales/etiquetas_ejemplo/config.json
```

## Documentación para IAs

Lee en orden:
```
docs/AGENT_GUIDE.md
docs/DIMENSIONES_DEL_ORDEN.md
context/ESTADO.md
tools/flyer_eventos/SPEC.md
```

Entrada legacy: `PARA_IA.md` → redirige a `docs/AGENT_GUIDE.md`

## Reglas del tapiz

- Paso a paso. Sin cambios gigantes.
- No Photoshop / Blender automático todavía.
- No borrar sin confirmación.
- `py` en Windows / `python3` en Linux/macOS
- Checkpoint después de cada mejora.
- **Solo instaloader. No yt-dlp.**

---

**flujo — Dimensiones del Orden**
*arte + automatización*
