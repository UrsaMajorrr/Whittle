from whittle.src.interfaces.file_path_interface import IFilePathManager
from pathlib import Path

class OpenFOAMFilePathManager(IFilePathManager):
    def __init__(self, case_dir: Path):
        self.case_dir = case_dir
        self.system_dir = case_dir / "system"
        self.constant_dir = case_dir / "constant"
        self.zero_dir = case_dir / "0"
    
    def get_system_dir(self) -> Path:
        return self.system_dir
    
    def get_constant_dir(self) -> Path:
        return self.constant_dir
    
    def get_zero_dir(self) -> Path:
        return self.zero_dir
    
    def ensure_directories_exist(self) -> None:
        self.system_dir.mkdir(parents=True, exist_ok=True)
        self.constant_dir.mkdir(parents=True, exist_ok=True)
        self.zero_dir.mkdir(exist_ok=True)
        (self.constant_dir / "triSurface").mkdir(exist_ok=True)