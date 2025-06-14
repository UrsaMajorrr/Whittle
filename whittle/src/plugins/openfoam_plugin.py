from pathlib import Path
from rich.console import Console
from typing import Optional

from whittle.src.interfaces.solver_plugin import SolverPlugin
from whittle.src.interfaces.prompt_interface import IPromptManager
from whittle.src.interfaces.solver_managers import SolverManagers
from whittle.src.managers.dictionary_manager import DictionaryManager, OpenFOAMDictionaryClassifier, FoamDictionaryExtractor, OpenFOAMDictionaryWriter
from whittle.src.managers.prompt_manager import DefaultPromptManager
from whittle.src.managers.file_path_manager import OpenFOAMFilePathManager
from whittle.src.managers.conversation_manager import OpenAIConversationManager
from whittle.src.managers.mesh_executor import MeshExecutor

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
        
        path_manager = OpenFOAMFilePathManager(case_dir)
        classifier = OpenFOAMDictionaryClassifier(path_manager)
        solver_name = self.solver_name
        extractor = FoamDictionaryExtractor(solver_name)
        writer = OpenFOAMDictionaryWriter(classifier, console)
        dictionary_manager = DictionaryManager(extractor, classifier, writer)
        
        prompt_manager = prompt_manager or DefaultPromptManager()
        conversation_manager = OpenAIConversationManager(
            api_key,
            prompt_manager.get_system_prompt()
        )
        mesh_executor = MeshExecutor(case_dir, console)
        
        return SolverManagers(
            prompt_manager=prompt_manager,
            conversation_manager=conversation_manager,
            dictionary_manager=dictionary_manager,
            path_manager=path_manager,
            mesh_executor=mesh_executor
        ) 