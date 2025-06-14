from abc import ABC, abstractmethod

class ICaseStructureManager(ABC):
    @abstractmethod
    def setup_case_structure(self) -> None: pass