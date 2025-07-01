from mcp.server.fastmcp import FastMCP
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
from whittle.src.infra.registry import SoftwareRegistry, ModelRegistry
import re
import os
import subprocess

#TODO: Implement OpenFOAM case running tool
#TODO: Implement SU2 case running tool, config file generation tool, file saving tool
#TODO: Implement a way for people to save conversations and load them in as context later (One problem: tool calling is based a lot on context)
#TODO: RAG for CFD software documentation and user file (this is far in the future)
#TODO: Implement tool for meshing for CFD software that can't mesh itself (this is far in the future)

mcp = FastMCP("whittle")

@mcp.tool()
def init_server(model_type: str) -> str:
    """Initialize the server with the specified LLM model type. Available models: 'gpt' (OpenAI) or 'claude' (Anthropic). Do not use CFD software names like 'openfoam' here."""
    global llm_model
    model_registry = ModelRegistry(system_prompt="""You are an agent in a multi-tool system for CFD workflows. You MUST pick only ONE tool per user request.

Here's when to use each tool:
- create_cfd_case_without_generating_mesh → user says: "set up a new case", "start a simulation", "initialize files", "create case structure"
- foam_block_mesh_generation → user says: "generate mesh", "run blockMesh", "mesh the domain", "create mesh", "generate a mesh"
- foam_snappy_hex_mesh_generation → user says: "complex mesh", "STL mesh", "snappyHexMesh", "generate complex mesh"
- run_simulation → user says: "run the simulation", "solve it", "start solving", "execute simulation", "run case
- edit_file → user says: "change this file", "modify", "update text", "edit"
- help_tool_selection → use this if you're unsure which tool to pick

CRITICAL RULE: If the user asks to "generate a mesh" or "create a mesh", use foam_block_mesh_generation, NOT create_cfd_case_without_generating_mesh!

Never confuse CFD software like OpenFOAM with LLM model types like GPT or Claude.

Always return only one tool call.""")
    
    try:
        llm_model = model_registry.get_model(model_type)
        return f"Server initialized with LLM model: {model_type}"
    except ValueError as e:
        available_models = model_registry.get_models()
        return f"Error: {e}. Available LLM models: {', '.join(available_models)}. Note: 'openfoam' is a CFD software, not an LLM model."

@mcp.tool()
def list_available_software() -> str:
    """List all available CFD software options"""
    registry = SoftwareRegistry()
    available_software = registry.available_software()
    return f"Available CFD software: {', '.join(available_software)}"

@mcp.tool()
def create_cfd_case_without_generating_mesh(simulation_description: str, case_dir: str, software_name: str) -> str:
    """Use this tool when the user wants to set up the initial case files but does not mention mesh generation. 
    Triggers: 'setup case', 'initialize case', 'create case structure', 'help me set up a case'.
    DO NOT use this tool if the user asks to 'generate mesh', 'create mesh', or 'mesh the domain' - use foam_block_mesh_generation instead."""
    if llm_model is None:
        return "Error: LLM model not initialized"
        
    registry = SoftwareRegistry()
    available_software = registry.available_software()
    
    if software_name not in available_software:
        return f"Error: Unknown software '{software_name}'. Available options: {', '.join(available_software)}"
    
    # Step 1: Initialize the software
    case_path = Path(case_dir)
    case_path.mkdir(parents=True, exist_ok=True)
    
    software_class = registry.get_software(software_name)
    software_instance = software_class(case_dir=case_path)
    
    # Step 2: Generate configuration files
    system_dir = case_path
    system_dir.mkdir(parents=True, exist_ok=True)
    
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
    generated_files = []
    for file in software_instance.get_required_files():
        file_path = case_path / file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        object_name = file_path.name
        
        #TODO: add SU2 header to SU2 files
        response_text = llm_model.return_response(  # type: ignore  
            f"""Generate a {file} file for {software_name} based on this simulation: "{simulation_description}"

The file MUST start with this exact header (with {object_name} as the object name):

{foam_header % object_name}

IMPORTANT MESH GENERATION RULES for blockMeshDict:
- Use simple single-block meshes with uniform grading (simpleGrading 1 1 1)
- Avoid complex multi-block structures that cause point merge failures
- Use symmetryPlane boundaries only for faces that are truly planar
- Keep mesh resolution moderate (e.g., 50-100 cells in each direction) for reliability
- For airfoil cases, use a simple rectangular domain around the airfoil
- Always ensure boundary faces are properly defined and consistent

Provide just the file content starting with this header, followed by the dictionary entries. Do not include ```text``` tags in the file content.""")
        
        with open(file_path, "w") as f:
            f.write(response_text.content[0].text)  # type: ignore
        generated_files.append(file)

    return f"Successfully created {software_name} case in {case_dir}. Generated files: {', '.join(generated_files)}"

@mcp.tool()
def run_openfoam_simulation(software_name: str, case_dir: str) -> str:  # type: ignore
    """Run a simulation for the OpenFOAM CFD software. This tool will run the simulation using Docker. Triggers: 'run simulation', 'solve', 'execute simulation', 'run case'"""
    if llm_model is None:
        return "Error: LLM model not initialized"
    
    registry = SoftwareRegistry()
    available_software = registry.available_software()
    
    if software_name not in available_software:
        return f"Error: Unknown software '{software_name}'. Available options: {', '.join(available_software)}"
    
    case_path = Path(case_dir)
    
    # Get the software instance and available commands
    software_instance = registry.get_software(software_name)(case_dir=case_path)
    available_commands = software_instance.get_available_commands()
    
    # Ask LLM to choose the command (single call, no loop)
    try:
        response = llm_model.return_response(  # type: ignore
            f"""Choose the correct command to run the simulation for {software_name} in {case_dir}. 
            Available commands: {', '.join(available_commands)}
            
            IMPORTANT: Choose from the available commands only. For OpenFOAM cases, typically use:
            - simpleFoam for incompressible steady-state
            - pimpleFoam for incompressible transient
            - icoFoam for incompressible laminar
            
            Return ONLY the command name, nothing else."""
        )
        command_to_run = response.content[0].text.strip()  # type: ignore
    except Exception as e:
        # If LLM fails, use a sensible default
        if "simpleFoam" in available_commands:
            command_to_run = "simpleFoam"
        elif "pimpleFoam" in available_commands:
            command_to_run = "pimpleFoam"
        elif "icoFoam" in available_commands:
            command_to_run = "icoFoam"
        else:
            command_to_run = available_commands[0] if available_commands else "simpleFoam"
        
        print(f"LLM API error: {e}. Using default command: {command_to_run}")
    
    # Validate the command
    if command_to_run not in available_commands:
        return f"Error: Invalid command '{command_to_run}'. Available commands: {', '.join(available_commands)}"
    
    # Run the simulation with Docker
    try:
        # Use Docker to run the simulation with explicit working directory change
        case_name = case_path.name  # Get the actual case directory name
        docker_cmd = [
            "docker", "run", "--rm", "-v", 
            f"{case_path.absolute()}:/{case_name}", 
            "opencfd/openfoam-run:latest",  # Use the actual Docker image name
            "bash", "-c", f"cd /{case_name} && {command_to_run}"
        ]
        
        result = subprocess.run(docker_cmd, capture_output=True, text=True, cwd=case_path)
        
        if result.returncode == 0:
            return f"Successfully ran {command_to_run} via Docker.\nOutput:\n{result.stdout}"
        else:
            return f"Simulation failed.\nError:\n{result.stderr}\nOutput:\n{result.stdout}"
    except Exception as e:
        return f"Failed to run simulation via Docker: {str(e)}"

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
    """Generate a mesh for an OpenFOAM case using blockMesh. This is the MAIN mesh generation tool for simple geometries. Use this when the user asks to generate a mesh, create a mesh, or run blockMesh. This tool will create or update the blockMeshDict file and run blockMesh to generate the actual mesh files."""
    software_class = SoftwareRegistry().get_software("openfoam")
    case_path = Path(case_dir)
    system_dir = case_path / "system"
    system_dir.mkdir(parents=True, exist_ok=True)

    # Run blockMesh using Docker
    try:
        # Use Docker to run blockMesh with explicit working directory change
        case_name = case_path.name  # Get the actual case directory name
        docker_cmd = [
            "docker", "run", "--rm", "-v", 
            f"{case_path.absolute()}:/{case_name}", 
            "opencfd/openfoam-run:latest",  # Use the actual Docker image name
            "bash", "-c", f"cd /{case_name} && blockMesh"
        ]
        
        result = subprocess.run(docker_cmd, capture_output=True, text=True, cwd=case_path)
        
        if result.returncode == 0:
            mesh_result = f"Successfully ran blockMesh via Docker.\nOutput:\n{result.stdout}"
        else:
            mesh_result = f"blockMesh failed via Docker.\nError:\n{result.stderr}\nOutput:\n{result.stdout}"
            
    except Exception as e:
        mesh_result = f"Failed to run blockMesh via Docker: {str(e)}"
    
    return f"Successfully ran blockMesh via Docker.\n\nMesh generation result:\n{mesh_result}"

@mcp.tool()
def foam_snappy_hex_mesh_generation(case_dir: str) -> str:
    """Generate a mesh for an OpenFOAM case using snappyHexMesh. This is for complex geometries with STL files. Use this when the user asks to generate a mesh for complex geometry, use snappyHexMesh, or work with STL files. This tool will create or update the snappyHexMeshDict file and run snappyHexMesh to generate the actual mesh files."""
    software_class = SoftwareRegistry().get_software("OpenFOAM")
    case_path = Path(case_dir)
    system_dir = case_path / "system"
    system_dir.mkdir(parents=True, exist_ok=True)

    # Run snappyHexMesh using Docker
    try:
        # Use Docker to run snappyHexMesh with explicit working directory change
        case_name = case_path.name  # Get the actual case directory name
        docker_cmd = [
            "docker", "run", "--rm", "-v", 
            f"{case_path.absolute()}:/{case_name}", 
            "opencfd/openfoam-run:latest",  # Use the actual Docker image name
            "bash", "-c", f"cd /{case_name} && snappyHexMesh"
        ]
        
        result = subprocess.run(docker_cmd, capture_output=True, text=True, cwd=case_path)
        
        if result.returncode == 0:
            mesh_result = f"Successfully ran snappyHexMesh via Docker.\nOutput:\n{result.stdout}"
        else:
            mesh_result = f"snappyHexMesh failed via Docker.\nError:\n{result.stderr}\nOutput:\n{result.stdout}"
            
    except Exception as e:
        mesh_result = f"Failed to run snappyHexMesh via Docker: {str(e)}"
    
    return f"Successfully ran snappyHexMesh via Docker.\n\nMesh generation result:\n{mesh_result}"

@mcp.tool()
def check_foam_mesh_quality(case_dir: str) -> str:
    """Check the quality of the mesh for an OpenFOAM case"""
    software_class = SoftwareRegistry().get_software("openfoam")
    case_path = Path(case_dir)
    system_dir = case_path / "system"
    system_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Use Docker to run checkMesh with explicit working directory change
        case_name = case_path.name  # Get the actual case directory name
        docker_cmd = [
            "docker", "run", "--rm", "-v", 
            f"{case_path.absolute()}:/{case_name}", 
            "opencfd/openfoam-run:latest",  # Use the actual Docker image name
            "bash", "-c", f"cd /{case_name} && checkMesh"
        ]

        result = subprocess.run(docker_cmd, capture_output=True, text=True, cwd=case_path)
        
        if result.returncode == 0:
            mesh_result = f"Successfully ran checkMesh via Docker.\nOutput:\n{result.stdout}"
        else:
            mesh_result = f"checkMesh failed via Docker.\nError:\n{result.stderr}\nOutput:\n{result.stdout}"
            
    except Exception as e:
        mesh_result = f"Failed to run checkMesh via Docker: {str(e)}"
    
    return f"Successfully ran checkMesh via Docker.\n\nMesh quality result:\n{mesh_result}"

@mcp.tool()
def recommend_software(simulation_description: str) -> str:
    """Get a recommendation for which CFD software to use based on the simulation description"""
    if llm_model is None:
        return "Error: LLM model not initialized"
    
    registry = SoftwareRegistry()
    available_software = registry.available_software()
    
    response_text = llm_model.return_response(  # type: ignore
        f"""Based on this simulation description: "{simulation_description}"

Available CFD software: {', '.join(available_software)}

Which software would be most appropriate for this simulation? Consider factors like:
- Type of physics (compressible/incompressible, multiphase, etc.)
- Geometry complexity
- Computational requirements
- User expertise level

Provide a clear recommendation with brief reasoning.""")
    
    return response_text.content[0].text  # type: ignore

@mcp.tool()
def help_tool_selection() -> str:
    """Help with tool selection. Use this when you're unsure which tool to use or want to clarify the workflow."""
    return """Tool Selection Guide:

1. create_cfd_case_without_generating_mesh - Use when user wants to SET UP case files (controlDict, fvSchemes, etc.)
   - Triggers: "setup case", "initialize case", "create case structure"
   - NOT for mesh generation

2. foam_block_mesh_generation - Use when user wants to GENERATE MESH
   - Triggers: "generate mesh", "create mesh", "mesh the domain", "run blockMesh"
   - This is the MAIN mesh generation tool

3. foam_snappy_hex_mesh_generation - Use for COMPLEX mesh generation
   - Triggers: "complex mesh", "STL mesh", "snappyHexMesh"
   - For geometries with STL files

4. run_openfoam_simulation - Use when user wants to RUN the simulation
   - Triggers: "run simulation", "solve", "execute simulation"

5. edit_file - Use when user wants to MODIFY files
   - Triggers: "change file", "modify", "edit"

CRITICAL: If user says "generate mesh" or "create mesh", use foam_block_mesh_generation, NOT create_cfd_case_without_generating_mesh!"""

if __name__ == "__main__":
    #setup_openfoam_env()
    mcp.run(transport="stdio")



