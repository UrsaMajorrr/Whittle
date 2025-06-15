"""
AI-powered CFD case setup and mesh generation assistant
"""
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from whittle.src.interfaces.prompt_interface import IPromptManager
from whittle.src.managers.solver_factory import SolverFactory, SolverManagers
from whittle.src.managers.plugin_registry import PluginRegistry
from whittle.src.managers.mesh_executor import MeshExecutor

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
        prompt_manager: Optional[IPromptManager] = None,
    ):
        self.console = console or Console()
        self.solver_name = solver_name
        self.api_key = api_key

        # Get all required managers from the factory
        managers: SolverManagers = SolverFactory.create_managers(
            solver_name=self.solver_name,
            api_key=self.api_key,
            console=self.console,
            prompt_manager=prompt_manager
        )
        self.mesh_executor = MeshExecutor(
            case_dir=self.case_dir,
            console=self.console
        )
        
        # Store managers
        self.prompt_manager = managers.prompt_manager
        self.case_dir = managers.case_dir
        self.conversation_manager = managers.conversation_manager
    
    @classmethod
    def available_solvers(cls) -> list[str]:
        """Get list of available solver names"""
        return PluginRegistry.available_solvers()
    
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
        response = self.conversation_manager.get_response(
            self.prompt_manager.get_initial_prompt()
        )
        self.console.print(Markdown(response))
        
        # Continue conversation until user is done
        while True:
            user_input = input("\nYour response ('done' to finish, 'run' to run the case): ")
            
            if user_input.lower() == 'done':
                break
            elif user_input.lower() == 'run':
                self.console.print("\n[green]✓[/green] Running the case...")
                self.mesh_executor.run_mesh()
                break
            
            # Get AI response for user input
            response = self.conversation_manager.get_response(user_input)
            self.console.print(Markdown(response))
        
        self.console.print("\n[green]✓[/green] Session complete!")
        self.console.print("\nNext steps:")
        self.console.print("1. Create the case directory structure")
        self.console.print("2. Copy the suggested configurations into the appropriate files")
        self.console.print("3. Run the mesh generation commands")
        self.console.print("4. Check the mesh quality") 