from __future__ import annotations
import zipfile
from pathlib import Path
from datetime import datetime

def export_flyer(project_dir: Path, output_dir: Path | None = None) -> Path:
    """Exporta flyer a ZIP incluyendo scripts JSX de integración directa"""
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
        add_dir(z, project_dir / "input", "input")
        add_dir(z, project_dir / "analysis", "analysis")
        add_dir(z, project_dir / "working", "working")
        add_dir(z, project_dir / "ai", "ai")

        for name in ["manifest.json", "README.md"]:
            p = project_dir / name
            if p.exists():
                z.write(p, name)

        working_dir = project_dir / "working"
        ai_dir = project_dir / "ai"
        working_dir.mkdir(exist_ok=True)
        ai_dir.mkdir(exist_ok=True)

        templates = Path(__file__).parent.parent / "templates"

        compose_ps = working_dir / "compose.jsx"
        if not compose_ps.exists():
            compose_ps.write_text(_get_compose_jsx(), encoding="utf-8")

        compose_ai = ai_dir / "compose_ai.jsx"
        if not compose_ai.exists():
            compose_ai.write_text(_get_compose_ai_jsx(), encoding="utf-8")

        email = _generar_email_draft(project_dir)
        z.writestr("exports/respuesta_jefe.txt", email)

        info = f"""FLUJO v0.15 — Export con integración directa
Proyecto: {project_dir.name}
Fecha: {ts}

Contenido:
- input/
- analysis/
- working/compose.jsx (Photoshop)
- ai/compose_ai.jsx (Illustrator)
"""
        z.writestr("LEEME.txt", info)

    return zip_path


def _get_compose_jsx() -> str:
    return """// compose.jsx — Flujo v0.15
#target photoshop
function main() {
    var base = Folder.current;
    var img = new File(base + "/input/input_ig.jpg");
    if (!img.exists) { alert("Falta input"); return; }

    var doc = app.documents.add(1080, 1920, 72, base.name, NewDocumentMode.RGB);
    var idPlc = charIDToTypeID("Plc ");
    var d = new ActionDescriptor();
    d.putPath(charIDToTypeID("null"), img);
    executeAction(idPlc, d, DialogModes.NO);

    var layer = doc.activeLayer;
    layer.name = "Imagen IG";
    var scale = (1920 / layer.bounds[3].value) * 100;
    layer.resize(scale, scale, AnchorPosition.MIDDLECENTER);
    executeAction(stringIDToTypeID("newPlacedLayer"), undefined, DialogModes.NO);

    var palette = [[255,0,127],[0,255,200],[25,25,25],[255,255,255],[140,90,220]];
    var names = ["Principal","Acento","Fondo","Texto","Secundario"];

    for (var i = 0; i < palette.length; i++) {
        var cLayer = doc.artLayers.add();
        cLayer.name = "Color " + names[i];
        var solid = new SolidColor();
        solid.rgb.red = palette[i][0];
        solid.rgb.green = palette[i][1];
        solid.rgb.blue = palette[i][2];
        var fd = new ActionDescriptor();
        var rd = new ActionDescriptor();
        rd.putDouble(charIDToTypeID("Rd  "), palette[i][0]);
        rd.putDouble(charIDToTypeID("Grn "), palette[i][1]);
        rd.putDouble(charIDToTypeID("Bl  "), palette[i][2]);
        var cd = new ActionDescriptor();
        cd.putObject(charIDToTypeID("Clr "), charIDToTypeID("RGBC"), rd);
        fd.putObject(charIDToTypeID("Clr "), charIDToTypeID("SolidColor"), cd);
        executeAction(charIDToTypeID("Fl  "), fd, DialogModes.NO);
    }

    var txt = doc.artLayers.add();
    txt.kind = LayerKind.TEXT;
    txt.name = "Caption";
    txt.textItem.contents = "Pega el caption aquí...";
    txt.textItem.size = 28;
    txt.textItem.font = "Arial-Bold";
    txt.textItem.color = new SolidColor();
    txt.textItem.color.rgb.red = 255;
    txt.textItem.color.rgb.green = 255;
    txt.textItem.color.rgb.blue = 255;
    txt.textItem.position = [80, 1700];

    alert("Listo para Photoshop");
}
main();
"""


def _get_compose_ai_jsx() -> str:
    return """// compose_ai.jsx — Flujo v0.15
#target illustrator
function main() {
    var base = Folder.current;
    var img = new File(base + "/input/input_ig.jpg");
    if (!img.exists) { alert("Falta input"); return; }

    var doc = app.documents.add(DocumentColorSpace.RGB, 1080, 1920);
    doc.artboards[0].name = base.name;

    var placed = doc.placedItems.add();
    placed.file = img;
    placed.name = "Imagen IG";

    var scale = (1920 / placed.height) * 100;
    placed.resize(scale, scale);
    placed.position = [(1080 - placed.width) / 2, 1920 - placed.height];

    var palette = [[255,0,127],[0,255,200],[25,25,25],[255,255,255],[140,90,220]];
    var names = ["Principal","Acento","Fondo","Texto","Secundario"];

    for (var i = 0; i < palette.length; i++) {
        var c = new RGBColor();
        c.red = palette[i][0]; c.green = palette[i][1]; c.blue = palette[i][2];
        var sw = doc.swatches.add();
        sw.name = names[i];
        sw.color = c;
    }

    alert("Listo para Illustrator");
}
main();
"""


def _generar_email_draft(project_dir: Path) -> str:
    import json
    try:
        data = json.loads((project_dir / "manifest.json").read_text(encoding="utf-8"))
        ig = data.get("instagram", {})
        return f"""Asunto: Flyer listo — {project_dir.name}

Hola,

Post: @{ig.get('owner','?')} / {ig.get('shortcode','')}

Archivos listos:
- Imagen original
- Paleta (.aco + .ase)
- Scripts directos para Photoshop e Illustrator

¿Ajustes?

Saludos
"""
    except:
        return "Error generando email draft"
