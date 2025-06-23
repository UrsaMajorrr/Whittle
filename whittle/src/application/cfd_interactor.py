from whittle.src.entities.cfd_software import CFDSoftware
from pathlib import Path
from subprocess import run

class FOAM(CFDSoftware):
    def __init__(self, case_dir: Path):
        super().__init__(case_dir)

    def get_required_files(self) -> list[str]:
        return [f"{self.case_dir}/system/controlDict", f"{self.case_dir}/system/fvSchemes", f"{self.case_dir}/system/fvSolution"]

    def get_available_commands(self) -> list[str]:
        return ["blockMesh", "decomposePar", "snappyHexMesh", "checkMesh", "setFields", "icoFoam"]
    
    def run_command(self, command: str, options: dict[str, str]) -> None:
        if command not in self.get_available_commands():
            raise ValueError(f"Command {command} not found in available commands")
        run(command, options, cwd=self.case_dir)

    def get_case_dir(self) -> Path:
        return self.case_dir
    
    def set_case_dir(self, case_dir: Path) -> None:
        self.case_dir = case_dir

class SU2(CFDSoftware):
    def __init__(self, case_dir: Path):
        super().__init__(case_dir)

    def get_required_files(self) -> list[str]:
        return [f"{self.case_dir}/*.su2", f"{self.case_dir}/*.cfg"]
    
    def get_available_commands(self) -> list[str]:
        return ["SU2_DEF", "SU2_CFD", "SU2_SOL", "SU2_GEO"]
    
    def run_command(self, command: str, options: dict[str, str]) -> None:
        if command not in self.get_available_commands():
            raise ValueError(f"Command {command} not found in available commands")
        run(command, options, cwd=self.case_dir)
    
    def get_case_dir(self) -> Path:
        return self.case_dir
    
    def set_case_dir(self, case_dir: Path) -> None:
        self.case_dir = case_dir
