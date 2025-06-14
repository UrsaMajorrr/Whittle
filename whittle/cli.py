"""
Command Line Interface for Whittle
"""
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from typing import Optional
import os
import sys

# Import plugins first to ensure they're registered
from whittle.src.plugins import *
from whittle.src.ai_assistant import AIAssistant
from whittle.config import load_config, get_openai_key

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

def validate_path(path_str: str) -> Path:
    """Validate that the path exists and is a directory"""
    path = Path(path_str)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"Directory {path} does not exist")
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"{path} is not a directory")
    return path

def main():
    """Interactive AI-powered mesh generation assistant"""
    parser = argparse.ArgumentParser(
        description="AI-powered assistant for CFD meshing and workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add arguments
    parser.add_argument(
        "case_dir",
        type=validate_path,
        nargs="?",  # Make it optional
        help="Path to case directory"
    )
    
    parser.add_argument(
        "--solver", "-s",
        default="openfoam",
        help="CFD solver to use (use --list-solvers to see available options)"
    )
    
    parser.add_argument(
        "--list-solvers", "-l",
        action="store_true",
        help="List available solver plugins"
    )
    
    parser.add_argument(
        "--api-key", "-k",
        help="OpenAI API key. Can also be set via OPENAI_API_KEY environment variable or .env file."
    )
    
    args = parser.parse_args()
    
    try:
        # Handle --list-solvers flag first
        if args.list_solvers:
            show_available_solvers()
            return 0
            
        # Validate case directory is provided for normal operation
        if args.case_dir is None:
            console.print("[red]Error: Case directory is required[/red]")
            console.print("Usage: whittle <CASE_DIR> [OPTIONS]")
            console.print("       whittle --list-solvers")
            return 1
            
        # Load config from .env files
        load_config()
        
        # Try to get API key from various sources
        api_key = args.api_key or get_openai_key()
        
        if not api_key:
            console.print("[red]Error: OpenAI API key not found.[/red]")
            console.print("Please provide it using one of these methods:")
            console.print("1. --api-key command line option")
            console.print("2. OPENAI_API_KEY environment variable")
            console.print("3. .env file in current directory")
            console.print("4. .env file in home directory")
            return 1
            
        # Set environment variable for other parts of the code
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Get solver name and normalize it
        solver_name = args.solver.lower()
        
        # Validate solver choice
        available_solvers = AIAssistant.available_solvers()
        if solver_name not in available_solvers:
            console.print(f"[red]Error: Unknown solver '{args.solver}'[/red]")
            show_available_solvers()
            return 1
        
        # Create and run the assistant with the API key
        assistant = AIAssistant(
            case_dir=args.case_dir,
            api_key=api_key,
            solver_name=solver_name,
            console=console
        )
        assistant.run()
        return 0
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 