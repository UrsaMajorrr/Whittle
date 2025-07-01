"""
AI-powered CFD case setup and mesh generation assistant
"""
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from pathlib import Path

# Import from actual modules that exist in the project
from whittle.src.application.llm_agent_interactor import OpenAILLMAgent, ClaudeLLMAgent
from whittle.src.application.cfd_interactor import FOAM, SU2
from whittle.src.infra.registry import SoftwareRegistry, ModelRegistry

class AIAssistant:
    """
    AI-powered assistant for CFD case setup and mesh generation.
    Supports multiple CFD solvers through a plugin architecture.
    """
    def __init__(
        self,
        api_key: str,
        solver_name: str = "openfoam",
        console: Optional[Console] = None,
        case_dir: Optional[Path] = None,
    ):
        self.console = console or Console()
        self.solver_name = solver_name
        self.api_key = api_key
        self.case_dir = case_dir or Path.cwd()
        
        # Initialize the registries
        self.software_registry = SoftwareRegistry()
        self.model_registry = ModelRegistry(
            system_prompt="You are a helpful assistant that can help with CFD simulations."
        )
        
        # Initialize LLM agent using the registry
        self.llm_agent = self.model_registry.get_model("gpt")  # Default to GPT
        
        # Initialize CFD software
        if solver_name.lower() == "openfoam":
            self.cfd_software = FOAM(case_dir=self.case_dir)
        elif solver_name.lower() == "su2":
            self.cfd_software = SU2(case_dir=self.case_dir)
        else:
            raise ValueError(f"Unsupported solver: {solver_name}")
    
    @classmethod
    def available_solvers(cls) -> list[str]:
        """Get list of available solver names"""
        return ["openfoam", "su2"]
    
    def available_models(self) -> list[str]:
        """Get list of available LLM models"""
        return self.model_registry.get_models()
    
    def set_model(self, model_name: str) -> None:
        """Change the LLM model"""
        self.llm_agent = self.model_registry.get_model(model_name)
    
    def run(self) -> None:
        """Main entry point for the AI mesh generation assistant"""
        solver_name = self.solver_name.title()
        self.console.print(Panel(
            f"[bold blue]Welcome to Whittle AI Mesh Assistant![/bold blue]\n\n"
            f"I'll help you set up your {solver_name} case using AI-powered recommendations.\n\n"
            f"I'll provide configuration suggestions that you can copy and paste into your files.",
            title="Whittle"
        ))
        
        # Get initial response
        initial_prompt = f"Help me set up a {solver_name} case. What do you need to know?"
        response = self.llm_agent.return_response(initial_prompt)
        self.console.print(Markdown(response))
        
        # Continue conversation until user is done
        while True:
            user_input = input("\nYour response ('done' to finish, 'run' to run the case): ")
            
            if user_input.lower() == 'done':
                break
            elif user_input.lower() == 'run':
                self.console.print("\n[green]✓[/green] Running the case...")
                # This would integrate with the CFD software
                if isinstance(self.cfd_software, FOAM):
                    result = self.cfd_software.block_mesh()
                    self.console.print(f"Mesh generation result: {result}")
                else:
                    self.console.print(f"Running {solver_name} case...")
                    # For SU2, you might want to run different commands
                    available_commands = self.cfd_software.get_available_commands()
                    self.console.print(f"Available commands: {available_commands}")
                break
            
            # Get AI response for user input
            response = self.llm_agent.return_response(user_input)
            self.console.print(Markdown(response))
        
        self.console.print("\n[green]✓[/green] Session complete!") 