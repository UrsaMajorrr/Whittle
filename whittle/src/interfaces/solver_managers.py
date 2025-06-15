"""Dataclass for grouping solver-specific managers"""
from dataclasses import dataclass

from whittle.src.interfaces.prompt_interface import IPromptManager
from whittle.src.interfaces.conversation_interface import IAIConversationManager

@dataclass
class SolverManagers:
    """Container for all solver-specific managers"""
    prompt_manager: IPromptManager
    conversation_manager: IAIConversationManager 