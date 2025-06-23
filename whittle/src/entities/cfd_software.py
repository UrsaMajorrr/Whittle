from abc import ABC, abstractmethod
from pathlib import Path

class CFDSoftware(ABC):

    def __init__(self, case_dir: Path):
        self.case_dir = case_dir

    @abstractmethod
    def get_required_files(self) -> list[str]:
        pass

    @abstractmethod
    def get_available_commands(self) -> list[str]:
        pass

    @abstractmethod
    def run_command(self, command: str, options: dict[str, str]) -> None:
        pass

    @abstractmethod
    def get_case_dir(self) -> Path:
        pass

    @abstractmethod
    def set_case_dir(self, case_dir: Path) -> None:
        pass


