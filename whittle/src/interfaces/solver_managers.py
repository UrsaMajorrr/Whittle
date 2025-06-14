"""Dataclass for grouping solver-specific managers"""
from dataclasses import dataclass

from whittle.src.interfaces.prompt_interface import IPromptManager
from whittle.src.interfaces.file_path_interface import IFilePathManager
from whittle.src.interfaces.mesh_executor_interface import IMeshExecutor
from whittle.src.interfaces.conversation_interface import IAIConversationManager
from whittle.src.interfaces.dictionary_interfaces import IDictionaryManager

@dataclass
class SolverManagers:
    """Container for all solver-specific managers"""
    prompt_manager: IPromptManager
    conversation_manager: IAIConversationManager
    dictionary_manager: IDictionaryManager
    path_manager: IFilePathManager
    mesh_executor: IMeshExecutor 