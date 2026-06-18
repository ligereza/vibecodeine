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

@app.command("flyer-import")
def flyer_import(email: Path = typer.Argument(..., help="ruta a correo.txt")):
    from .intake.email_parser import parse_email_file
    result = parse_email_file(email)
    if 'error' in result:
        console.print(f"[red]Error: {result['error']}[/]")
        return
    console.print(f"[green]Links: {result['link_count']}[/] Tipo: {result['project_type']}")
    for w in result.get('warnings', []):
        console.print(f"[yellow]{w}[/]")

@app.command()
def export(project: Path = typer.Argument(..., help="ruta al proyecto"), output: Path = typer.Option(None, "--output", "-o")):
    from .export.zipper import export_flyer
    try:
        zip_path = export_flyer(project, output)
        console.print(f"[green]ZIP: {zip_path}[/]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        raise typer.Exit(1)

def main():
    app()

if __name__ == "__main__":
    app()
