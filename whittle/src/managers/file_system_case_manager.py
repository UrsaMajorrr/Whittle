from whittle.src.interfaces.case_structure_interface import ICaseStructureManager
from pathlib import Path

class FileSystemCaseManager(ICaseStructureManager):
    def __init__(self, case_dir: Path):
        self.case_dir = case_dir
        self.system_dir = case_dir / "system"
        self.constant_dir = case_dir / "constant"
    
    def setup_case_structure(self) -> None:
        self.system_dir.mkdir(parents=True, exist_ok=True)
        self.constant_dir.mkdir(parents=True, exist_ok=True)
        (self.case_dir / "0").mkdir(exist_ok=True)
        (self.constant_dir / "triSurface").mkdir(exist_ok=True)