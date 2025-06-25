"""Base class for LLM agents"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMAgent(ABC):
    def __init__(self, system_prompt: str):
        self.api_key = self._get_api_key_from_env()
        self.messages = [{"role": "system", "content": system_prompt}]
        self.context: Dict[str, Any] = {}

    @abstractmethod
    def return_response(self, prompt: str) -> str:
        """Return a response for the given prompt"""
        pass

    @abstractmethod
    def _get_api_key_from_env(self) -> str:
        """Get API key from environment variables"""
        pass

    @abstractmethod
    def _store_conversation(self, conversation: list[str]) -> None:
        pass