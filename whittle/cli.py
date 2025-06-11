"""
Command Line Interface for Whittle
"""
import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from typing import Optional
import os

from whittle.core.dict_parser import OpenFOAMDict
from whittle.mesh.ai_assistant import AIAssistant
from whittle.config import load_config, get_openai_key

app = typer.Typer(
    name="whittle",
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
        dir_okay=True,
        file_okay=False,
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        "-k",
        help="OpenAI API key. Can also be set via OPENAI_API_KEY environment variable or .env file.",
        envvar="OPENAI_API_KEY",
    ),
):
    """Interactive AI-powered mesh generation assistant"""
    try:
        # Load config from .env files
        load_config()
        
        # Try to get API key from various sources
        api_key = api_key or get_openai_key()
        
        if not api_key:
            console.print("[red]Error: OpenAI API key not found.[/red]")
            console.print("Please provide it using one of these methods:")
            console.print("1. --api-key command line option")
            console.print("2. OPENAI_API_KEY environment variable")
            console.print("3. .env file in current directory")
            console.print("4. .env file in home directory")
            raise typer.Exit(1)
            
        os.environ["OPENAI_API_KEY"] = api_key
        
        assistant = AIAssistant(case_dir, console)
        assistant.run()
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

def main():
    app() 