
from mcp.server.fastmcp import FastMCP
from pathlib import Path
from whittle.src.infra.registry import SoftwareRegistry, ModelRegistry
import re

#TODO: Implement OpenFOAM case running tool, mesh generation tool
#TODO: Implement SU2 case running tool, config file generation tool, file saving tool
#TODO: RAG for CFD software documentation and user file (this is far in the future)
#TODO: Implement tool for meshing for CFD software that can't mesh itself (this is far in the future)

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
    
    # Get the software class and instantiate it
    software_class = registry.get_software(selected_software)
    software_instance = software_class(case_dir=Path(case_dir))
    
    # Generate config files
    for file in software_instance.get_required_files():
        response_text = llm_model.return_response(f"Generate a {file} file for the {selected_software} software. Provide just the file content, no other text. Since it is in plain text, it will be wrapped in ```text``` tags. Do not include those tags in the file content.")
        with open(Path(case_dir) / file, "w") as f:
            f.write(response_text)

    return f"Successfully set up {selected_software} case with config files in {case_dir}"

@mcp.tool()
def run_simulation(software_name: str, case_dir: str) -> str:
    """Run a simulation for the given CFD software"""

@mcp.tool()
def edit_file(file_path: str, content_to_change :str,  new_content: str) -> str:
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
def foam_mesh_generation(case_dir: str) -> str:
    """Generate a mesh for the given OpenFOAM case. This will run blockMesh for simple cases and snappyHexMesh for complex cases."""
    software_class = SoftwareRegistry().get_software("OpenFOAM")
    software_instance = software_class(case_dir=Path(case_dir))
    software_instance.block_mesh()
    software_instance.snappy_hex_mesh()
    return f"Successfully generated a mesh for the {case_dir} case"

if __name__ == "__main__":
    mcp.run(transport="stdio")



