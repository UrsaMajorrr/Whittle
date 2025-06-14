"""
Command Line Interface for Whittle
"""
import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from typing import Optional
import os

from whittle.src.ai_assistant import AIAssistant
from whittle.config import load_config, get_openai_key

app = typer.Typer(
    name="whittle",
    help="AI-powered assistant for CFD meshing and workflows",
    add_completion=False,
)
console = Console()

def show_available_solvers():
    """Show available solver plugins"""
    solvers = AIAssistant.available_solvers()
    if not solvers:
        console.print("[yellow]No solver plugins found![/yellow]")
        return
    
    console.print("\nAvailable solvers:")
    for solver in solvers:
        console.print(f"- {solver}")
    console.print()

@app.callback(invoke_without_command=True)
def main(
    case_dir: Path = typer.Argument(
        ...,
        help="Path to case directory",
        exists=True,
        dir_okay=True,
        file_okay=False,
    ),
    solver: str = typer.Option(
        "openfoam",
        "--solver",
        "-s",
        help="CFD solver to use (use --list-solvers to see available options)",
    ),
    list_solvers: bool = typer.Option(
        False,
        "--list-solvers",
        "-l",
        help="List available solver plugins",
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
        if list_solvers:
            show_available_solvers()
            raise typer.Exit()
            
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
            
        # Set environment variable for other parts of the code
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Validate solver choice
        available_solvers = AIAssistant.available_solvers()
        if solver.lower() not in available_solvers:
            console.print(f"[red]Error: Unknown solver '{solver}'[/red]")
            show_available_solvers()
            raise typer.Exit(1)
        
        # Create and run the assistant with the API key
        assistant = AIAssistant(
            case_dir=case_dir,
            api_key=api_key,
            solver_name=solver.lower(),
            console=console
        )
        assistant.run()
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app() 