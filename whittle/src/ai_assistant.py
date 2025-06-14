"""
AI-powered CFD case setup and mesh generation assistant
"""
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from whittle.src.interfaces.prompt_interface import IPromptManager
from whittle.src.managers.solver_factory import SolverFactory, SolverManagers
from whittle.src.managers.plugin_registry import PluginRegistry

class AIAssistant:
    """
    AI-powered assistant for CFD case setup and mesh generation.
    Supports multiple CFD solvers through a plugin architecture.
    """
    def __init__(
        self,
        case_dir: Path,
        api_key: str,
        solver_name: str = "openfoam",
        console: Optional[Console] = None,
        prompt_manager: Optional[IPromptManager] = None,
    ):
        self.console = console or Console()
        self.solver_name = solver_name
        
        # Get all required managers from the factory
        managers: SolverManagers = SolverFactory.create_managers(
            solver_name=solver_name,
            case_dir=case_dir,
            api_key=api_key,
            console=self.console,
            prompt_manager=prompt_manager
        )
        
        # Store managers
        self.prompt_manager = managers.prompt_manager
        self.conversation_manager = managers.conversation_manager
        self.dictionary_manager = managers.dictionary_manager
        self.path_manager = managers.path_manager
        self.mesh_executor = managers.mesh_executor
    
    @classmethod
    def available_solvers(cls) -> list[str]:
        """Get list of available solver names"""
        return PluginRegistry.available_solvers()
    
    def run(self) -> None:
        """Main entry point for the AI mesh generation assistant"""
        solver_name = self.solver_name.title()
        self.console.print(Panel(
            f"[bold blue]Welcome to Whittle AI Mesh Assistant![/bold blue]\n\n"
            f"I'll help you set up your {solver_name} case using AI-powered recommendations.",
            title="Whittle"
        ))
        
        # Create case structure
        self.path_manager.ensure_directories_exist()
        
        # Get initial response
        response = self.conversation_manager.get_response(
            self.prompt_manager.get_initial_prompt()
        )
        self.console.print(Markdown(response))
        self.dictionary_manager.process_ai_response(response)
        
        # Continue conversation until mesh is set up
        while True:
            user_input = input("\nYour response ('done' to finish, 'run' to run the mesh): ")
            
            if user_input.lower() == 'done':
                break
            elif user_input.lower() == 'run':
                # Check for missing required files
                missing_files = self.dictionary_manager.get_missing_required_files()
                if missing_files:
                    # Ask AI to create missing files
                    missing_files_prompt = f"""Based on the case requirements we discussed, please create the following {solver_name} configuration files:
{', '.join(missing_files)}

For each file, provide the complete content in appropriate code blocks."""
                    
                    response = self.conversation_manager.get_response(missing_files_prompt)
                    self.console.print(Markdown(response))
                    self.dictionary_manager.process_ai_response(response)
                    
                    # Recheck for missing files
                    missing_files = self.dictionary_manager.get_missing_required_files()
                    if missing_files:
                        self.console.print("\n[red]Still missing required files:[/red]")
                        for file in missing_files:
                            self.console.print(f"- {file}")
                        continue
                
                self.mesh_executor.run_mesh()
                # TODO: After running the mesh, run the solver, and then run the post-processing
                # self.solver_plugin.run_solver()
                # self.solver_plugin.run_post_processing()
            
            # Get AI response for user input
            response = self.conversation_manager.get_response(user_input)
            self.console.print(Markdown(response))
            self.dictionary_manager.process_ai_response(response)
        
        self.console.print("\n[green]✓[/green] Case setup complete!")
        self.console.print("\nNext steps:")
        self.console.print("1. Review the generated configuration files")
        self.console.print("2. Run the mesh generation commands")
        self.console.print("3. Check the mesh quality") 