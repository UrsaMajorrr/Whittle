"""
Command Line Interface for OpenFOAM Copilot
"""
import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from typing import Optional

from openfoam_copilot.core.dict_parser import OpenFOAMDict

app = typer.Typer(
    name="openfoam-copilot",
    help="AI-powered assistant for OpenFOAM meshing and workflows",
    add_completion=False,
)
console = Console()

@app.command()
def check(
    dict_path: Path = typer.Argument(
        ...,
        help="Path to OpenFOAM dictionary file",
        exists=True,
    ),
    dict_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="Type of dictionary (e.g., blockMeshDict, snappyHexMeshDict)",
    ),
):
    """Check and validate an OpenFOAM dictionary file"""
    try:
        # If dict_type not provided, try to infer from filename
        if dict_type is None:
            dict_type = dict_path.stem
            
        parser = OpenFOAMDict(dict_type)
        content = parser.parse_file(dict_path)
        
        is_valid, messages = parser.validate()
        
        if is_valid:
            console.print(Panel("✅ Dictionary is valid", title="Validation Result", style="green"))
        else:
            console.print(Panel("❌ Dictionary has issues", title="Validation Result", style="red"))
            
        if messages:
            console.print("\nValidation Messages:")
            for msg in messages:
                console.print(f"• {msg}")
                
        suggestions = parser.suggest_improvements()
        if suggestions:
            console.print("\n[bold]Suggestions for improvement:[/bold]")
            for suggestion in suggestions:
                console.print(f"• {suggestion}")
                
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

@app.command()
def mesh(
    case_dir: Path = typer.Argument(
        ...,
        help="Path to OpenFOAM case directory",
        exists=True,
    ),
):
    """Interactive mesh generation assistant"""
    console.print("[yellow]Interactive mesh generation assistant - Coming soon![/yellow]")
    # TODO: Implement interactive mesh generation workflow

def main():
    app() 