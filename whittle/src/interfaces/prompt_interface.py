from typing import Protocol

class IPromptManager(Protocol):
    """Manages system and user prompts"""
    def get_system_prompt(self) -> str: pass
    def get_initial_prompt(self) -> str: pass
    def update_system_prompt(self, new_prompt: str) -> None: pass