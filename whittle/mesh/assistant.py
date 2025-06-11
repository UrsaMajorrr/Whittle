"""
Interactive mesh generation assistant
"""
from pathlib import Path
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from .templates import create_blockmesh_dict, create_snappyhexmesh_dict

class MeshAssistant:
    """
    Interactive assistant for OpenFOAM mesh generation.
    Guides users through the process of creating and setting up meshes.
    """
    
    def __init__(self, case_dir: Path, console: Optional[Console] = None):
        self.case_dir = case_dir
        self.console = console or Console()
        self.system_dir = case_dir / "system"
        self.constant_dir = case_dir / "constant"
        
    def setup_case_structure(self) -> None:
        """Create the basic OpenFOAM case directory structure"""
        # Create main directories
        self.system_dir.mkdir(parents=True, exist_ok=True)
        self.constant_dir.mkdir(parents=True, exist_ok=True)
        (self.case_dir / "0").mkdir(exist_ok=True)
        
        # Create triSurface directory for STL files
        (self.constant_dir / "triSurface").mkdir(exist_ok=True)
        
    def determine_mesh_strategy(self) -> str:
        """
        Determine the most appropriate meshing strategy based on user input
        """
        self.console.print(Panel(
            "[bold]Mesh Generation Strategy[/bold]\n\n"
            "Let's determine the best meshing approach for your case.",
            title="Whittle Mesh Assistant"
        ))
        
        # Get basic information about the geometry
        has_cad = Confirm.ask("Do you have CAD geometry (STL/OBJ/etc)?")
        
        if has_cad:
            complexity = Prompt.ask(
                "How would you describe the geometry complexity?",
                choices=["simple", "moderate", "complex"],
                default="moderate"
            )
            
            if complexity == "simple":
                return "blockMesh"
            else:
                return "snappyHexMesh"
        else:
            shape = Prompt.ask(
                "What basic shape best describes your geometry?",
                choices=["box", "cylinder", "pipe", "custom"],
                default="box"
            )
            
            return "blockMesh"
            
    def setup_blockmesh(self) -> None:
        """
        Guide user through blockMesh setup
        """
        self.console.print(Panel(
            "[bold]blockMesh Setup[/bold]\n\n"
            "Let's create a blockMeshDict configuration.",
            title="Block Mesh Configuration"
        ))
        
        # Get basic dimensions
        dimensions = {}
        for dim in ['x', 'y', 'z']:
            dimensions[f'{dim}_min'] = float(Prompt.ask(
                f"Enter minimum {dim} coordinate",
                default="0"
            ))
            dimensions[f'{dim}_max'] = float(Prompt.ask(
                f"Enter maximum {dim} coordinate",
                default="1" if dim != 'z' else "0.1"
            ))
            
        cells_per_dim = {}
        for dim in ['x', 'y', 'z']:
            cells_per_dim[dim] = int(Prompt.ask(
                f"Number of cells in {dim} direction",
                default="20"
            ))
            
        # Generate blockMeshDict
        blockmesh_content = create_blockmesh_dict(dimensions, cells_per_dim)
        
        # Write the file
        blockmesh_path = self.system_dir / "blockMeshDict"
        blockmesh_path.write_text(blockmesh_content)
        
        self.console.print(f"\n[green]✓[/green] Created blockMeshDict at {blockmesh_path}")
        
    def setup_snappyhexmesh(self) -> None:
        """
        Guide user through snappyHexMesh setup
        """
        self.console.print(Panel(
            "[bold]snappyHexMesh Setup[/bold]\n\n"
            "Let's configure snappyHexMesh for your geometry.",
            title="SnappyHexMesh Configuration"
        ))
        
        # Get STL file information
        stl_path = Path(Prompt.ask("Path to your STL file"))
        if not stl_path.exists():
            raise FileNotFoundError(f"STL file not found: {stl_path}")
            
        # Copy STL to case/constant/triSurface
        import shutil
        target_stl = self.constant_dir / "triSurface" / stl_path.name
        shutil.copy2(stl_path, target_stl)
        
        # Basic snapping settings
        n_surface_layers = int(Prompt.ask(
            "Number of surface layers",
            default="3"
        ))
        
        # Generate snappyHexMeshDict
        stl_name = stl_path.stem
        snappy_content = create_snappyhexmesh_dict(stl_name, n_surface_layers)
        
        # Write the file
        snappy_path = self.system_dir / "snappyHexMeshDict"
        snappy_path.write_text(snappy_content)
        
        # Also create a basic blockMeshDict for the background mesh
        dimensions = {
            'x_min': -1, 'x_max': 1,
            'y_min': -1, 'y_max': 1,
            'z_min': -1, 'z_max': 1
        }
        cells_per_dim = {'x': 20, 'y': 20, 'z': 20}
        blockmesh_content = create_blockmesh_dict(dimensions, cells_per_dim)
        
        # Write the blockMeshDict
        blockmesh_path = self.system_dir / "blockMeshDict"
        blockmesh_path.write_text(blockmesh_content)
        
        self.console.print(f"\n[green]✓[/green] Created snappyHexMeshDict at {snappy_path}")
        self.console.print(f"[green]✓[/green] Created background blockMeshDict at {blockmesh_path}")
        self.console.print(f"[green]✓[/green] Copied STL file to {target_stl}")
        
    def run(self) -> None:
        """
        Main entry point for the mesh generation assistant
        """
        self.console.print(Panel(
            "[bold blue]Welcome to Whittle Mesh Assistant![/bold blue]\n\n"
            "I'll help you set up and generate your OpenFOAM mesh.",
            title="Whittle"
        ))
        
        # Create case structure
        self.setup_case_structure()
        
        # Determine meshing strategy
        strategy = self.determine_mesh_strategy()
        
        # Execute chosen strategy
        if strategy == "blockMesh":
            self.setup_blockmesh()
        elif strategy == "snappyHexMesh":
            self.setup_snappyhexmesh()
            
        self.console.print("\n[green]✓[/green] Initial mesh setup complete!")
        self.console.print("\nNext steps:")
        self.console.print("1. Review generated dictionary files in system/")
        self.console.print("2. Run mesh generation using 'blockMesh' or 'snappyHexMesh'")
        self.console.print("3. Check mesh quality with 'checkMesh'") 