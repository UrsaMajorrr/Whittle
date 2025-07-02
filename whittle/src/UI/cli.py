"""
Command Line Interface for Whittle
"""
import argparse
from rich.console import Console
import os
import sys
from pathlib import Path
from typing import Optional

# Import plugins first to ensure they're registered
from whittle.src.plugins import *
from whittle.src.ai_assistant import AIAssistant
from whittle.config import load_config, get_openai_key, get_anthropic_key
from whittle.src.application.llm_agent_interactor import OpenAILLMAgent, ClaudeLLMAgent

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

def show_available_models():
    """Show available LLM models"""
    console.print("\nAvailable LLM models:")
    console.print("- GPT-4 (requires OPENAI_API_KEY)")
    console.print("- Claude (requires ANTHROPIC_API_KEY)")
    console.print()

def create_llm_agent(model: str, system_prompt: str) -> Optional[OpenAILLMAgent | ClaudeLLMAgent]:
    """Create an LLM agent based on model choice and available API keys"""
    if model.lower() == "gpt-4":
        api_key = get_openai_key()
        if not api_key:
            console.print("[red]Error: OpenAI API key not found.[/red]")
            return None
        return OpenAILLMAgent(system_prompt)
    elif model.lower() == "claude":
        api_key = get_anthropic_key()
        if not api_key:
            console.print("[red]Error: Anthropic API key not found.[/red]")
            return None
        return ClaudeLLMAgent(system_prompt)
    else:
        console.print(f"[red]Error: Unknown model '{model}'[/red]")
        return None

def main():
    """Interactive AI-powered mesh generation assistant"""
    parser = argparse.ArgumentParser(
        description="AI-powered assistant for CFD meshing and workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add arguments
    parser.add_argument(
        "--model", "-m",
        default="gpt-4",
        help="LLM model to use (gpt-4 or claude)"
    )
    
    parser.add_argument(
        "--list-models", "-L",
        action="store_true",
        help="List available LLM models"
    )
    
    parser.add_argument(
        "--list-solvers", "-l",
        action="store_true",
        help="List available solver plugins"
    )
    
    parser.add_argument(
        "--case-dir", "-d",
        default="./case",
        help="Path to case directory"
    )
    
    args = parser.parse_args()
    
    try:
        # Handle --list flags first
        if args.list_models:
            show_available_models()
            return 0
            
        if args.list_solvers:
            show_available_solvers()
            return 0
            
        # Load config from .env files
        load_config()
        
        # Create case directory if it doesn't exist
        case_dir = Path(args.case_dir).resolve()
        case_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up system prompt for MCP
        system_prompt = """You are an AI assistant for CFD (Computational Fluid Dynamics) case setup and mesh generation.
Your role is to help users set up CFD simulations by:

1. Understanding their requirements through natural conversation
2. Inferring which CFD software would be most appropriate (when not explicitly specified)
3. Providing guidance on mesh generation and case setup
4. Suggesting appropriate commands and configurations

When you infer which CFD software would be most appropriate, indicate it with:
INFERRED_SOFTWARE: <software_name>

Keep track of the context of the conversation and use it to provide more relevant responses.
If you need more information, ask clarifying questions.
"""
        
        # Create LLM agent
        agent = create_llm_agent(args.model, system_prompt)
        if not agent:
            return 1
            
        # Update context with case directory
        agent.update_context("case_dir", str(case_dir))
        
        # Main interaction loop
        console.print("[green]Welcome to Whittle! I'm here to help you set up your CFD case.[/green]")
        console.print("[green]Type 'exit' or 'quit' to end the session.[/green]\n")
        
        while True:
            try:
                # Get user input
                user_input = input("> ")
                
                # Check for exit command
                if user_input.lower() in ["exit", "quit"]:
                    break
                    
                # Get AI response
                response = agent.return_response(user_input)
                
                # Print response
                console.print("\n" + response + "\n")
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Session interrupted by user[/yellow]")
                break
            except Exception as e:
                console.print(f"\n[red]Error:[/red] {str(e)}")
                continue
        
        return 0
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 