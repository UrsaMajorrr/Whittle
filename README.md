# Whittle - AI-Powered CFD Assistant

An AI-powered assistant for CFD case setup and mesh generation, supporting multiple CFD solvers through a plugin architecture. Whittle integrates with Claude Desktop to provide an intelligent interface for OpenFOAM and other CFD software workflows.

## Prerequisites

Before installing Whittle, ensure you have:

1. **Python 3.12+** installed on your system
2. **Docker Desktop** installed and running
3. **Claude Desktop** installed and configured
4. **uv** package manager (recommended) or pip

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Whittle
```

### 2. Install Dependencies

**Option A: Using uv (Recommended)**
```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

**Option B: Using pip**
```bash
pip install -e .
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root with your API keys:

```bash
# For OpenAI GPT models (optional)
OPENAI_API_KEY=your_openai_api_key_here

# For Claude models (required for Claude Desktop integration)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 4. Configure Claude Desktop

Whittle uses the Model Context Protocol (MCP) to communicate with Claude Desktop. You need to configure Claude Desktop to connect to the Whittle MCP server.

1. **Open Claude Desktop**
2. **Go to Settings** → **Model Context Protocol**
3. **Add a new server** with the following configuration:

```json
{
    "mcpServers": {
        "whittle": {
            "command": "/path/to/bin/uv",
            "args": ["--directory", "/path/to/Whittle/whittle/src/api", "run", "server.py"]
        }
    }
}
```

**Important Notes:**
- Replace `/path/to/your/whittle/project` with the actual absolute path to your Whittle project directory
- The `PYTHONPATH` environment variable is crucial for the server to find the Whittle modules
- Make sure the path uses forward slashes (/) even on Windows

### 5. Pull OpenFOAM Docker Image

Whittle uses Docker to run OpenFOAM commands. Pull the required image:

```bash
docker pull opencfd/openfoam-run:latest
```

## Usage

### Starting Whittle with Claude Desktop

1. **Launch Claude Desktop**
2. **Start a new conversation**
3. **Whittle will automatically connect** via MCP and provide CFD tools

### Basic Workflow

Once connected, you can interact with Whittle through Claude Desktop using natural language:

1. **Set up a case**: "Help me set up an OpenFOAM case for airfoil simulation"
2. **Generate mesh**: "Generate a mesh for my case"
3. **Run simulation**: "Run the simulation"
4. **Check mesh quality**: "Check the mesh quality"

### Available Tools

Whittle provides several specialized tools for CFD workflows:

- **`create_cfd_case_without_generating_mesh`** - Set up initial case files (controlDict, fvSchemes, etc.)
- **`foam_block_mesh_generation`** - Generate simple meshes using blockMesh
- **`foam_snappy_hex_mesh_generation`** - Generate complex meshes using snappyHexMesh
- **`run_openfoam_simulation`** - Run OpenFOAM solvers (simpleFoam, pimpleFoam, etc.)
- **`check_foam_mesh_quality`** - Check mesh quality and topology
- **`edit_file`** - Modify case files
- **`help_tool_selection`** - Get guidance on which tool to use

### Example Conversation

```
You: "I want to simulate flow around a NACA 0012 airfoil at 10 degrees angle of attack"

Claude: I'll help you set up an OpenFOAM case for your airfoil simulation. Let me create the necessary case files first.

[Claude uses create_cfd_case_without_generating_mesh tool]

You: "Now generate a mesh for this case"

Claude: I'll generate a mesh using blockMesh for your airfoil case.

[Claude uses foam_block_mesh_generation tool]

You: "Run the simulation"

Claude: I'll run the simulation using the simpleFoam solver for your incompressible steady-state case.

[Claude uses run_openfoam_simulation tool]
```

## Project Structure

```
whittle/
├── __init__.py              # Package initialization
├── config.py               # Configuration settings
└── src/                    # Source code
    ├── __init__.py
    ├── api/                # MCP server and API
    │   ├── server.py       # Main MCP server
    │   └── stdio_server.py # Alternative stdio server
    ├── application/        # Application layer
    │   ├── cfd_interactor.py
    │   └── llm_agent_interactor.py
    ├── entities/           # Domain entities
    │   ├── cfd_software.py
    │   └── llm_agent.py
    ├── infra/              # Infrastructure layer
    │   └── registry.py
    └── UI/                 # User interface
        └── cli.py
```

## Supported CFD Software

Currently supported CFD solvers:
- **OpenFOAM** - Full support for case setup, mesh generation, and simulation
- **SU2** - Basic support (planned expansion)

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure `PYTHONPATH` is set correctly in Claude Desktop config
   - Use absolute paths in the configuration

2. **Docker connection issues**
   - Verify Docker Desktop is running
   - Check that the OpenFOAM image is pulled: `docker images | grep openfoam`

3. **API key errors**
   - Verify your `.env` file contains the correct API keys
   - Ensure the keys have sufficient credits/permissions

4. **MCP connection failures**
   - Restart Claude Desktop after configuration changes
   - Check the server path in Claude Desktop config
   - Verify Python can find the Whittle modules

### Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are installed correctly
3. Ensure Docker is running and accessible
4. Check that Claude Desktop can connect to the MCP server


### Adding New CFD Software

Whittle uses a plugin architecture. To add support for new CFD software:

1. Create a new class in `whittle/src/entities/cfd_software.py`
2. Implement the required methods
3. Register the software in `whittle/src/infra/registry.py`

## Dependencies

- Python 3.12+
- Docker Desktop with OpenFOAM image (`opencfd/openfoam-run:latest`)
- Claude Desktop
- uv (recommended) or pip
- Anthropic API key (required)
- OpenAI API key (optional)

## License

[Add your license information here]
