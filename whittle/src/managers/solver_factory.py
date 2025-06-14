from dataclasses import dataclass
from pathlib import Path
from rich.console import Console
from typing import Optional

from whittle.src.interfaces.prompt_interface import IPromptManager
from whittle.src.interfaces.file_path_interface import IFilePathManager
from whittle.src.interfaces.mesh_executor_interface import IMeshExecutor
from whittle.src.interfaces.conversation_interface import IAIConversationManager
from whittle.src.interfaces.dictionary_interfaces import IDictionaryManager
from whittle.src.managers.plugin_registry import PluginRegistry

@dataclass
class SolverManagers:
    """Container for all solver-specific managers"""
    prompt_manager: IPromptManager
    conversation_manager: IAIConversationManager
    dictionary_manager: IDictionaryManager
    path_manager: IFilePathManager
    mesh_executor: IMeshExecutor

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