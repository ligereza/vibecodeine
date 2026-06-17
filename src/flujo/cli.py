import sys
from pathlib import Path
import typer
from rich.console import Console

app = typer.Typer(add_completion=False, help="flujo — Dimensiones del Orden")
console = Console()

@app.command()
def health():
    from .paths import repo_root
    root = repo_root()
    console.print(f"[cyan]flujo[/] @ {root}")

@app.command()
def export(
    project: Path = typer.Argument(..., help="ruta al proyecto flyer"),
    output: Path = typer.Option(None, "--output", "-o", help="carpeta destino")
):
    from .export.zipper import export_flyer
    try:
        zip_path = export_flyer(project, output)
        console.print(f"[green]ZIP creado:[/] {zip_path}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        raise typer.Exit(1)

@app.command("open")
def open_cmd(
    project: Path = typer.Argument(..., help="ruta al proyecto flyer"),
    ps: bool = typer.Option(False, "--ps"),
    ai: bool = typer.Option(False, "--ai")
):
    import subprocess
    import platform
    from pathlib import Path as Pth

    proj = Pth(project)
    system = platform.system()

    if ps:
        jsx = proj / "working" / "compose.jsx"
        if jsx.exists():
            if system == "Darwin":
                subprocess.run(["open", str(jsx)])
            elif system == "Windows":
                subprocess.run(["start", "", str(jsx)], shell=True)
            console.print("[green]Abriendo en Photoshop...[/]")
        else:
            console.print("[yellow]Ejecuta primero 'flujo export'[/]")

    elif ai:
        jsx = proj / "ai" / "compose_ai.jsx"
        if jsx.exists():
            if system == "Darwin":
                subprocess.run(["open", str(jsx)])
            elif system == "Windows":
                subprocess.run(["start", "", str(jsx)], shell=True)
            console.print("[green]Abriendo en Illustrator...[/]")
        else:
            console.print("[yellow]Ejecuta primero 'flujo export'[/]")

def main():
    app()

if __name__ == "__main__":
    app()
