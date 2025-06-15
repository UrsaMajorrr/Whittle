from abc import ABC, abstractmethod

class IMeshExecutor(ABC):
    @abstractmethod
    def run_mesh(self) -> None: pass