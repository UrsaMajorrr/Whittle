from abc import ABC, abstractmethod

class IAIConversationManager(ABC):
    @abstractmethod
    def get_response(self, user_input: str) -> str: pass