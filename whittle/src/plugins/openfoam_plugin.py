from pathlib import Path
from rich.console import Console
from typing import Optional

from whittle.src.interfaces.solver_plugin import SolverPlugin
from whittle.src.interfaces.prompt_interface import IPromptManager
from whittle.src.interfaces.solver_managers import SolverManagers
from whittle.src.managers.prompt_manager import DefaultPromptManager
from whittle.src.managers.conversation_manager import OpenAIConversationManager

class OpenFOAMPlugin(SolverPlugin):
    """OpenFOAM solver plugin implementation"""
    
    @property
    def solver_name(self) -> str:
        return "openfoam"
    
    def create_managers(
        self,
        case_dir: Path,
        api_key: str,
        console: Optional[Console] = None,
        prompt_manager: Optional[IPromptManager] = None,
    ) -> SolverManagers:
        """Create OpenFOAM-specific managers"""
        console = console or Console()
        
        prompt_manager = prompt_manager or DefaultPromptManager()
        conversation_manager = OpenAIConversationManager(
            api_key,
            prompt_manager.get_system_prompt()
        )
        
        return SolverManagers(
            prompt_manager=prompt_manager,
            conversation_manager=conversation_manager,
            case_dir=case_dir
        ) 