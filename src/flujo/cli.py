import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(add_completion=False, help="flujo — Dimensiones del Orden // arte y automatización")
console = Console()

@app.command()
def health():
    """Health check del repo"""
    from .paths import repo_root
    root = repo_root()
    console.print(f"[cyan]flujo[/] @ {root}")
    checks = [
        ("requirements.txt", (root / "requirements.txt").exists()),
        ("tools/flyer_eventos", (root / "tools" / "flyer_eventos").exists()),
        ("projects/flyer_eventos", (root / "projects" / "flyer_eventos").exists()),
    ]
    try:
        import instaloader, yaml, matplotlib, gradio
        checks.append(("instaloader", True))
    except Exception as e:
        checks.append((f"deps: {e}", False))

    for name, ok in checks:
        console.print(f"  {'✓' if ok else '✗'} {name}", style="green" if ok else "red")

@app.command("flyer-import")
def flyer_import(
    email: Path = typer.Argument(..., help="ruta a correo.txt con links IG"),
    force: bool = typer.Option(False, "--force", help="forzar duplicados"),
):
    """Crear proyectos flyer desde un correo con links de Instagram"""
    from .flyer.import_email import import_from_email
    res = import_from_email(email, force=force)
    console.print(f"[green]Creados:[/] {res['created']}  [yellow]Omitidos:[/] {res['skipped']}  [dim]Encontrados: {res['found']}[/]")

@app.command("flyer-list")
def flyer_list():
    """Listar proyectos flyer"""
    from .paths import flyer_base
    base = flyer_base()
    if not base.exists():
        console.print("sin proyectos")
        return
    table = Table("Fecha", "Proyecto", "Estado")
    for p in sorted(base.iterdir(), reverse=True):
        if not p.is_dir(): continue
        mf = p / "manifest.json"
        status = "-"
        if mf.exists():
            import json
            try:
                d = json.loads(mf.read_text(encoding="utf-8"))
                status = d.get("status", "")
            except: pass
        table.add_row(p.name[:10], p.name, status)
    console.print(table)

@app.command("ig-redownload")
def ig_redownload(
    all: bool = typer.Option(False, "--all", help="reintentar también los descargados"),
    project: Path = typer.Option(None, "--project", help="proyecto específico"),
):
    """Reintentar descarga IG en proyectos fallidos"""
    from .paths import flyer_base
    from .manifest import load_json, write_json
    from .ig.download import download_post
    import datetime
    base = flyer_base()
    projects = [Path(project)] if project else sorted([p for p in base.glob("*") if (p / "manifest.json").exists()]) if base.exists() else []
    ok = fail = skip = 0
    for proj in projects:
        data = load_json(proj / "manifest.json") or {}
        ig = data.get("instagram", {}) if isinstance(data.get("instagram"), dict) else {}
        url = ig.get("url", "")
        if not url: continue
        if not all and ig.get("download_status") == "downloaded":
            skip += 1; continue
        console.print(f"→ {proj.name}  {url}")
        res = download_post(url, proj / "input")
        manifest_path = proj / "manifest.json"
        full = load_json(manifest_path) or {}
        full.setdefault("instagram", {}).update({"download_result": res, "download_retry_at": datetime.datetime.now().isoformat(timespec="seconds")})
        if res.get("status") == "downloaded":
            full["instagram"].update({
                "download_status": "downloaded",
                "media_type": res.get("media_type",""),
                "file_count": res.get("file_count",0),
                "owner": res.get("owner",""),
                "date_utc": res.get("date",""),
            })
            ok += 1
            console.print(f"  [green]OK {res.get('media_type')}[/]")
        else:
            fail += 1
            console.print(f"  [red]FAIL {res.get('reason')}[/]")
        write_json(manifest_path, full)
    console.print(f"\nOK={ok} FAIL={fail} SKIP={skip}")

@app.command()
def daily():
    """Generar reporte diario"""
    import subprocess
    from .paths import repo_root
    root = repo_root()
    subprocess.run([sys.executable, str(root / "scripts" / "flujo_daily.py")], check=False)

@app.command()
def app_cmd():
    """Iniciar interfaz Gradio"""
    import subprocess
    from .paths import repo_root
    root = repo_root()
    subprocess.run([sys.executable, str(root / "scripts" / "app.py")])

# alias para que `flujo app` funcione
app.command(name="app")(app_cmd)

@app.command("new-flyer")
def new_flyer(name: str = typer.Argument(..., help="nombre del evento")):
    """Crear proyecto flyer manual"""
    from .flyer.project import create_flyer_project
    p = create_flyer_project(None, name, source_type="manual")
    console.print(f"[green]Creado:[/] {p}")

@app.command()
def analyze(
    project: Path = typer.Argument(None, help="ruta al proyecto flyer (vacío = último)"),
    all: bool = typer.Option(False, "--all", help="analizar todos los proyectos"),
):
    """Analizar flyer: colores dominantes + OCR opcional"""
    from .analyze.run import analyze_project, find_latest_flyer
    from .paths import flyer_base

    targets = []
    if all:
        base = flyer_base()
        targets = sorted([p for p in base.glob("*") if (p / "manifest.json").exists()]) if base.exists() else []
    elif project:
        targets = [project]
    else:
        latest = find_latest_flyer()
        if not latest:
            console.print("[red]No se encontró ningún proyecto flyer[/]")
            raise typer.Exit(1)
        targets = [latest]

    ok = 0
    for proj in targets:
        console.print(f"→ [cyan]{proj.name}[/]")
        res = analyze_project(proj)
        if res.get("status") == "ok":
            colors = [c["hex"] for c in res.get("palette", {}).get("colors", [])]
            console.print("  colores: " + " ".join(f"[on {c}]{c}[/]" for c in colors))
            if res.get("ocr", {}).get("available"):
                console.print(f"  OCR: {res['ocr'].get('chars',0)} chars")
            else:
                console.print("  OCR: [dim]no disponible (pip install pytesseract)[/]")
            ok += 1
        else:
            console.print(f"  [red]FAIL: {res.get('error', res)}[/]")
    console.print(f"\n[green]Analizados OK: {ok}/{len(targets)}[/]")

@app.command()
def index(
    rebuild: bool = typer.Option(False, "--rebuild", help="reconstruir índice desde cero")
):
    """Índice SQLite de flyers"""
    from .index.db import rebuild_index, list_flyers
    from rich.table import Table
    if rebuild:
        res = rebuild_index()
        console.print(f"[green]Index rebuild OK:[/] {res['indexed']} flyers → {res['db']}")
    rows = list_flyers(limit=30)
    if rows:
        table = Table("shortcode", "owner", "status", "media", "proyecto")
        for r in rows:
            table.add_row(
                r.get("shortcode","") or "-",
                r.get("owner","") or "-",
                r.get("status",""),
                r.get("media_type",""),
                Path(r["project_path"]).name
            )
        console.print(table)
    else:
        console.print("Índice vacío. Ejecuta: flujo index --rebuild")

@app.command()
def export(
    project: Path = typer.Argument(..., help="ruta al proyecto flyer"),
    output: Path = typer.Option(None, "--output", "-o", help="carpeta destino")
):
    """Exportar proyecto flyer a ZIP listo para Photoshop"""
    from .export.zipper import export_flyer
    try:
        zip_path = export_flyer(project, output)
        console.print(f"[green]ZIP creado:[/] {zip_path}")
        # tamaño
        size_mb = zip_path.stat().st_size / 1024 / 1024
        console.print(f"Tamaño: {size_mb:.2f} MB")
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        raise typer.Exit(1)

def main():
    app()

if __name__ == "__main__":
    app()
