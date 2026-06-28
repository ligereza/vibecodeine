from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Union


SvgInput = Union[str, Path, Iterable[Union[str, Path]]]


def prepare_svg_for_illustrator(
    svg_inputs: SvgInput,
    output_dir: str | Path | None = None,
    project_name: str = "flujo_svg",
) -> Path:
    """Crear un paquete listo para abrir en Illustrator desde uno o varios SVG.

    El paquete incluye una carpeta ``svg/`` con los archivos copiados, un script
    JSX para Illustrator y un README con instrucciones simples.
    """

    if isinstance(svg_inputs, (str, Path)):
        candidates = [Path(svg_inputs)]
    else:
        candidates = [Path(item) for item in svg_inputs]

    resolved_files: list[Path] = []
    for item in candidates:
        if item.is_dir():
            resolved_files.extend(sorted([p for p in item.rglob("*.svg") if p.is_file()]))
        elif item.suffix.lower() == ".svg" and item.exists():
            resolved_files.append(item)
        else:
            raise FileNotFoundError(f"SVG no encontrado o no válido: {item}")

    if not resolved_files:
        raise FileNotFoundError("No se encontraron archivos SVG para preparar")

    unique_files: list[Path] = []
    seen: set[Path] = set()
    for path in resolved_files:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique_files.append(resolved)

    base_output = Path(output_dir) if output_dir else Path("exports") / f"{project_name}_illustrator"
    package_dir = base_output / project_name
    package_dir.mkdir(parents=True, exist_ok=True)

    svg_dir = package_dir / "svg"
    svg_dir.mkdir(parents=True, exist_ok=True)

    copied_files: list[str] = []
    for source in unique_files:
        destination = svg_dir / source.name
        destination.write_bytes(source.read_bytes())
        copied_files.append(destination.relative_to(package_dir).as_posix())

    manifest = {
        "project": project_name,
        "svg_files": copied_files,
        "created_with": "flujo.export.illustrator.prepare_svg_for_illustrator",
    }
    (package_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    (package_dir / "import_svg.jsx").write_text(_build_illustrator_jsx(copied_files), encoding="utf-8")
    (package_dir / "README.md").write_text(_build_readme(project_name, copied_files), encoding="utf-8")

    return package_dir


def _build_illustrator_jsx(svg_files: list[str]) -> str:
    entries = [f'  new File(baseFolder + "/svg/{path.split("/")[-1]}")' for path in svg_files]
    entries_block = ",\n".join(entries)
    return f"""// import_svg.jsx — preparado por flujo
#target illustrator

function main() {{
    var baseFolder = Folder.current;
    var svgFiles = [
{entries_block}
    ];

    if (!svgFiles.length) {{
        alert("No se encontraron SVGs para importar");
        return;
    }}

    var doc = app.documents.add(DocumentColorSpace.RGB, 1400, 900);
    doc.artboards[0].name = "SVG import";

    var x = 80;
    var y = 120;
    for (var i = 0; i < svgFiles.length; i++) {{
        if (!svgFiles[i].exists) continue;

        var placed = doc.placedItems.add();
        placed.file = svgFiles[i];
        placed.name = svgFiles[i].name.replace(/\\.svg$/i, "");
        placed.position = [x, y];

        var scale = 0.8;
        placed.resize(scale * 100, scale * 100);
        x += 280;
        if ((i + 1) % 3 === 0) {{
            x = 80;
            y -= 240;
        }}
    }}

    alert("SVGs importados. Ajusta tamaño/posición en Illustrator si hace falta.");
}}

main();
"""


def _build_readme(project_name: str, svg_files: list[str]) -> str:
    svg_list = "\n".join(f"- {path}" for path in svg_files)
    return f"""# {project_name}

Paquete preparado para abrir en Illustrator desde SVGs.

## Archivos
{svg_list}

## Pasos
1. Abre `import_svg.jsx` con Illustrator.
2. Asegúrate de que la carpeta `svg/` esté junto al script.
3. Revisa el documento resultante y ajusta escala/posición si hace falta.

## Nota
Este paquete conserva el SVG como vector editable y facilita la revisión en Illustrator.
"""
