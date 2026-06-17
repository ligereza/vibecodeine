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


@app.command()
def export(
    project: Path = typer.Argument(..., help="ruta al proyecto flyer"),
    output: Path = typer.Option(None, "--output", "-o", help="carpeta destino")
):
    """Exportar proyecto flyer a ZIP listo para Photoshop/Illustrator"""
    from .export.zipper import export_flyer
    try:
        zip_path = export_flyer(project, output)
        console.print(f"[green]ZIP creado:[/] {zip_path}")
        size_mb = zip_path.stat().st_size / 1024 / 1024
        console.print(f"Tamaño: {size_mb:.2f} MB")
        console.print("[dim]Incluye: compose.jsx (PS) + compose_ai.jsx (AI)[/]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        raise typer.Exit(1)


@app.command("open")
def open_cmd(
    project: Path = typer.Argument(..., help="ruta al proyecto flyer"),
    ps: bool = typer.Option(False, "--ps", help="abrir script de Photoshop"),
    ai: bool = typer.Option(False, "--ai", help="abrir script de Illustrator")
):
    """Abrir los scripts JSX directamente en Photoshop o Illustrator"""
    import subprocess
    import platform
    from pathlib import Path as Pth

    proj = Pth(project)
    working = proj / "working"
    ai_folder = proj / "ai"

    system = platform.system()

    if ps:
        jsx = working / "compose.jsx"
        if jsx.exists():
            if system == "Darwin":
                subprocess.run(["open", str(jsx)])
            elif system == "Windows":
                subprocess.run(["start", "", str(jsx)], shell=True)
            else:
                console.print(f"Abre manualmente: {jsx}")
            console.print("[green]Abriendo compose.jsx en Photoshop...[/]")
        else:
            console.print("[yellow]No existe working/compose.jsx. Ejecuta primero 'flujo export'[/]")

    elif ai:
        jsx = ai_folder / "compose_ai.jsx"
        if jsx.exists():
            if system == "Darwin":
                subprocess.run(["open", str(jsx)])
            elif system == "Windows":
                subprocess.run(["start", "", str(jsx)], shell=True)
            else:
                console.print(f"Abre manualmente: {jsx}")
            console.print("[green]Abriendo compose_ai.jsx en Illustrator...[/]")
        else:
            console.print("[yellow]No existe ai/compose_ai.jsx. Ejecuta primero 'flujo export'[/]")

    else:
        console.print("[cyan]Uso:[/]")
        console.print("  flujo open <proyecto> --ps     → Photoshop")
        console.print("  flujo open <proyecto> --ai     → Illustrator")


def main():
    app()


if __name__ == "__main__":
    app()
