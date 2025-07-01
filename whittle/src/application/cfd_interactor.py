from whittle.src.entities.cfd_software import CFDSoftware
from pathlib import Path
from subprocess import run, PIPE, CalledProcessError

class FOAM(CFDSoftware):
    def __init__(self, case_dir: Path):
        super().__init__(case_dir)
    
    def __name__(self) -> str:
        return "OpenFOAM"

    def get_required_files(self) -> list[str]:
        return ["system/controlDict", "system/fvSchemes", "system/fvSolution", "0/U", "0/p", \
        "0/T", "0/nut", "0/nuTilda" "system/blockMeshDict"]

    def get_available_commands(self) -> list[str]:
        return ["blockMesh", "decomposePar", "snappyHexMesh", "checkMesh", "setFields", "icoFoam"]
    
    def run_command(self, command: str) -> str:
        """Run an OpenFOAM command and return its output"""
        if command not in self.get_available_commands():
            raise ValueError(f"Command {command} not found in available commands")
        try:
            result = run(command, cwd=self.case_dir, capture_output=True, text=True, check=True)
            return f"Command output:\n{result.stdout}\n{result.stderr}"
        except CalledProcessError as e:
            return f"Command failed with error:\n{e.stdout}\n{e.stderr}"

    def block_mesh(self) -> str:
        output = []
        output.append(self.run_command("blockMesh"))
        output.append(self.run_command("checkMesh"))
        return "\n".join(output)

    def snappy_hex_mesh(self) -> str:
        output = []
        output.append(self.run_command("snappyHexMesh"))
        output.append(self.run_command("checkMesh"))
        return "\n".join(output)

    def get_case_dir(self) -> Path:
        return self.case_dir
    
    def set_case_dir(self, case_dir: Path) -> None:
        self.case_dir = case_dir

class SU2(CFDSoftware):
    def __init__(self, case_dir: Path):
        super().__init__(case_dir)

    def __name__(self) -> str:
        return "SU2"

    def get_required_files(self) -> list[str]:
        return ["*.su2", "*.cfg"]
    
    def get_available_commands(self) -> list[str]:
        return ["SU2_DEF", "SU2_CFD", "SU2_SOL", "SU2_GEO"]
    
    def run_command(self, command: str, options: dict[str, str]) -> None:
        if command not in self.get_available_commands():
            raise ValueError(f"Command {command} not found in available commands")
        run(command, options, cwd=self.case_dir) #type: ignore
    
    def get_case_dir(self) -> Path:
        return self.case_dir
    
    def set_case_dir(self, case_dir: Path) -> None:
        self.case_dir = case_dir
