from whittle.src.interfaces.mesh_executor_interface import IMeshExecutor
from pathlib import Path
from rich.console import Console
import subprocess

class MeshExecutor(IMeshExecutor):
    def __init__(self, case_dir: Path, console: Console):
        self.case_dir = case_dir
        self.console = console
    
    def run_mesh(self) -> None:
        self.console.print("\n[green]✓[/green] Running mesh generation commands...")
        subprocess.run(["blockMesh"], cwd=self.case_dir)
        subprocess.run(["checkMesh"], cwd=self.case_dir)
        self.console.print("\n[green]✓[/green] Mesh generation complete!")