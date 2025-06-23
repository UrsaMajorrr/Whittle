from abc import ABC, abstractmethod

class LLMAgent(ABC):
    def __init__(self):
        self.api_key = self._get_api_key_from_env()

    @abstractmethod
    def return_response(self, prompt: str) -> str:
        pass

    @abstractmethod
    def _get_api_key_from_env(self) -> str:
        pass

    @abstractmethod
    def _store_conversation(self, conversation: list[str]) -> None:
        pass