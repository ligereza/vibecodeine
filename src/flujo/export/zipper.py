from __future__ import annotations
import zipfile
from pathlib import Path
from datetime import datetime

def export_flyer(project_dir: Path, output_dir: Path | None = None) -> Path:
    """Crea un ZIP listo para Photoshop con input + análisis"""
    project_dir = Path(project_dir)
    if not (project_dir / "manifest.json").exists():
        raise FileNotFoundError(f"No es un proyecto flyer válido: {project_dir}")

    if output_dir is None:
        output_dir = project_dir / "exports"
    output_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    zip_path = output_dir / f"{project_dir.name}_entrega_{ts}.zip"

    def add_dir(zipf, src_dir: Path, arc_prefix: str):
        if not src_dir.exists():
            return
        for f in src_dir.rglob("*"):
            if f.is_file() and ".gitkeep" not in f.name:
                arcname = f"{arc_prefix}/{f.relative_to(src_dir)}"
                zipf.write(f, arcname)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        # input
        add_dir(z, project_dir / "input", "input")
        # analysis
        add_dir(z, project_dir / "analysis", "analysis")
        # manifest + readme
        for name in ["manifest.json", "README.md"]:
            p = project_dir / name
            if p.exists():
                z.write(p, name)
        # info txt
        info = f"FLUJO // export\nProyecto: {project_dir.name}\nFecha: {ts}\n\nContenido:\n- input/  : imágenes originales de Instagram\n- analysis/: palette.json, palette.png, palette.aco, palette.ase, ocr.txt\n- manifest.json\n"
        z.writestr("LEEME.txt", info)

    return zip_path
