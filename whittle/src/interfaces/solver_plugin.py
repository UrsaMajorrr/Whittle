from abc import ABC, abstractmethod
from pathlib import Path
from rich.console import Console
from typing import Optional

from whittle.src.interfaces.prompt_interface import IPromptManager
from whittle.src.interfaces.solver_managers import SolverManagers

class SolverPlugin(ABC):
    """Interface that all solver plugins must implement"""
    
    @abstractmethod
    def create_managers(
        self,
        case_dir: Path,
        api_key: str,
        console: Optional[Console] = None,
        prompt_manager: Optional[IPromptManager] = None,
    ) -> SolverManagers:
        """Create all necessary managers for this solver type"""
        pass
    
    @property
    @abstractmethod
    def solver_name(self) -> str:
        """Return the name of this solver"""
        pass 