from pathlib import Path
from rich.console import Console
from typing import Optional

from whittle.src.interfaces.prompt_interface import IPromptManager
from whittle.src.interfaces.solver_managers import SolverManagers
from whittle.src.managers.plugin_registry import PluginRegistry

class SolverFactory:
    """Factory for creating solver-specific managers"""
    
    @staticmethod
    def create_managers(
        solver_name: str,
        case_dir: Path,
        api_key: str,
        console: Optional[Console] = None,
        prompt_manager: Optional[IPromptManager] = None,
    ) -> SolverManagers:
        """Create a set of managers for the given solver"""
        # Get the appropriate plugin
        plugin = PluginRegistry.get_plugin(solver_name)
        
        # Use the plugin to create managers
        return plugin.create_managers(
            case_dir=case_dir,
            api_key=api_key,
            console=console,
            prompt_manager=prompt_manager
        ) 