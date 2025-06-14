from typing import Protocol
from pathlib import Path

class IFilePathManager(Protocol):
    """Manages OpenFOAM case directory structure"""
    def get_system_dir(self) -> Path: pass
    def get_constant_dir(self) -> Path: pass
    def get_zero_dir(self) -> Path: pass
    def ensure_directories_exist(self) -> None: pass