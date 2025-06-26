from mcp.server.fastmcp import FastMCP
from pathlib import Path
from whittle.src.infra.registry import SoftwareRegistry, ModelRegistry
import re
import os
import subprocess

#TODO: Implement OpenFOAM case running tool, mesh generation tool
#TODO: Implement SU2 case running tool, config file generation tool, file saving tool
#TODO: RAG for CFD software documentation and user file (this is far in the future)
#TODO: Implement tool for meshing for CFD software that can't mesh itself (this is far in the future)

# Initialize OpenFOAM environment if available
def setup_openfoam_env():
    possible_paths = [
        "/usr/lib/openfoam/openfoam2312/etc/bashrc",
        "/opt/openfoam2312/etc/bashrc",
        "/usr/lib/openfoam/openfoam2306/etc/bashrc",
        "/opt/openfoam2306/etc/bashrc",
        "/opt/openfoam12/etc/bashrc",
    ]
    for path in possible_paths:
        if os.path.exists(path):
            # Export the environment from sourcing OpenFOAM's bashrc
            env_cmd = f'bash -c "source {path} && env"'
            try:
                env_output = subprocess.check_output(env_cmd, shell=True).decode()
                for line in env_output.splitlines():
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
                print(f"OpenFOAM environment sourced from {path}")
                return True
            except subprocess.CalledProcessError:
                print(f"Failed to source OpenFOAM environment from {path}")
    print("No OpenFOAM environment found")
    return False

mcp = FastMCP("whittle")
llm_model = None

@mcp.tool()
def init_server(model_type: str) -> str:
    """Initialize the server with the specified model type"""
    global llm_model
    model_registry = ModelRegistry(system_prompt="You are a helpful assistant that can help with CFD simulations.")
    llm_model = model_registry.get_model(model_type)
    return "Server initialized with model: " + model_type

@mcp.tool()
def setup_cfd_case(prompt: str, case_dir: str) -> str:
    """Choose the best CFD software based on the prompt and generate its config files"""
    if llm_model is None:
        return "Error: LLM model not initialized"
        
    registry = SoftwareRegistry()
    available_software = registry.available_software()
    
    # First try to identify the software from the prompt
    selected_software = None
    for software_name in available_software:
        if software_name.lower() in prompt.lower():
            selected_software = software_name
            break
            
    if not selected_software:
        return "Please specify which CFD software you'd prefer to use from: " + ", ".join(available_software)
    
    # Create OpenFOAM case directory structure
    case_path = Path(case_dir)
    system_dir = case_path / "system"
    system_dir.mkdir(parents=True, exist_ok=True)
    
    # Get the software class and instantiate it
    software_class = registry.get_software(selected_software)
    software_instance = software_class(case_dir=case_path)
    
    # OpenFOAM header template
    foam_header = """/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\\\    /   O peration     | Website:  https://openfoam.org
    \\\\  /    A nd           | Version:  12
     \\\\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       dictionary;
    location    "system";
    object      %s;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //"""
    
    # Generate config files
    for file in software_instance.get_required_files():
        file_path = case_path / file  # This will handle the system/ prefix correctly
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get the object name from the file path (e.g., "controlDict" from "system/controlDict")
        object_name = file_path.name
        
        response_text = llm_model.return_response(
            f"""Generate a {file} file for the {selected_software} software. The file MUST start with this exact header (with {object_name} as the object name):

{foam_header % object_name}

Provide just the file content starting with this header, followed by the dictionary entries. Do not include ```text``` tags in the file content.""")
        
        with open(file_path, "w") as f:
            f.write(response_text)

    return f"Successfully set up {selected_software} case with config files in {case_dir}"

@mcp.tool()
def run_simulation(software_name: str, case_dir: str) -> str:
    """Run a simulation for the given CFD software"""

@mcp.tool()
def edit_file(file_path: str, content_to_change: str, new_content: str) -> str:
    """Edit a file with the given content. If the file exists, returns its current content first."""
    try:
        current_content = ""
        if Path(file_path).exists():
            with open(file_path, "r") as f:
                current_content = f.read()

        print(content_to_change)
        print(new_content)
        
        current_content = re.sub(content_to_change, new_content, current_content)

        with open(file_path, "w") as f:
            f.write(current_content)
        
        return f"Current content:\n{current_content}"
    except Exception as e:
        return f"Error editing file: {str(e)}"

@mcp.tool()
def foam_block_mesh_generation(case_dir: str) -> str:
    """Generate a mesh for the given OpenFOAM case. This will run blockMesh for simple cases. Write the blockMeshDict file to the case directory. Remember to write the files to the system folder in the case directory."""
    software_class = SoftwareRegistry().get_software("OpenFOAM")
    case_path = Path(case_dir)
    system_dir = case_path / "system"
    system_dir.mkdir(parents=True, exist_ok=True)
    
    foam_header = """/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\\\    /   O peration     | Website:  https://openfoam.org
    \\\\  /    A nd           | Version:  12
     \\\\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       dictionary;
    location    "system";
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //"""
    
    software_instance = software_class(case_dir=case_path)
    response_text = llm_model.return_response(
        f"""Generate a blockMeshDict file for the {case_dir} case. The file MUST start with this exact header:

{foam_header}

Provide just the file content starting with this header, followed by the blockMesh configuration. Do not include ```text``` tags in the file content.""")
    
    blockMeshDict_path = system_dir / "blockMeshDict"
    with open(blockMeshDict_path, "w") as f:
        f.write(response_text)

    # Run blockMesh
    software_instance.block_mesh()
    
    # Read and return the generated file content
    with open(blockMeshDict_path, "r") as f:
        file_content = f.read()
    
    return f"Successfully generated blockMeshDict and ran blockMesh.\n\nGenerated blockMeshDict content:\n\n{file_content}"

@mcp.tool()
def foam_snappy_hex_mesh_generation(case_dir: str) -> str:
    """Generate a mesh for the given OpenFOAM case. This will run snappyHexMesh for complex cases. Write the snappyHexMeshDict file to the case directory. Remember to write the files to the system folder in the case directory."""
    software_class = SoftwareRegistry().get_software("OpenFOAM")
    case_path = Path(case_dir)
    system_dir = case_path / "system"
    system_dir.mkdir(parents=True, exist_ok=True)
    
    foam_header = """/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\\\    /   O peration     | Website:  https://openfoam.org
    \\\\  /    A nd           | Version:  12
     \\\\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    format      ascii;
    class       dictionary;
    location    "system";
    object      snappyHexMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //"""
    
    software_instance = software_class(case_dir=case_path)
    response_text = llm_model.return_response(
        f"""Generate a snappyHexMeshDict file for the {case_dir} case. The file MUST start with this exact header:

{foam_header}

Provide just the file content starting with this header, followed by the snappyHexMesh configuration. Do not include ```text``` tags in the file content.""")
    
    snappyHexMeshDict_path = system_dir / "snappyHexMeshDict"
    with open(snappyHexMeshDict_path, "w") as f:
        f.write(response_text)

    # Run snappyHexMesh
    software_instance.snappy_hex_mesh()
    
    # Read and return the generated file content
    with open(snappyHexMeshDict_path, "r") as f:
        file_content = f.read()
    
    return f"Successfully generated snappyHexMeshDict and ran snappyHexMesh.\n\nGenerated snappyHexMeshDict content:\n\n{file_content}"

if __name__ == "__main__":
    setup_openfoam_env()
    mcp.run(transport="stdio")



