# Whittle

An AI-powered assistant for OpenFOAM meshing and workflows. This tool helps with:

- AI-driven mesh generation and configuration
- Intelligent dictionary file generation and validation
- Best practices recommendations
- Interactive mesh setup workflow

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd Whittle

# Install in development mode
pip install -e .
```

## Usage

### Interactive Mesh Generation

```bash
# Start the AI-powered mesh generation assistant
whittle mesh path/to/case

# You can also provide your OpenAI API key directly
whittle mesh path/to/case --api-key YOUR_API_KEY
```

The assistant will guide you through:
1. Understanding your geometry and simulation requirements
2. Choosing the best meshing approach (blockMesh, snappyHexMesh)
3. Generating all necessary dictionary files (controlDict, blockMeshDict, etc.)
4. Validating configurations and providing best practices
5. Suggesting improvements and optimizations

## Features

### Current
- AI-powered interactive mesh generation
- Intelligent dictionary file creation and validation:
  - controlDict with simulation settings
  - blockMeshDict for simple geometries
  - snappyHexMeshDict for complex geometries
- Best practices recommendations
- Real-time configuration validation
- Dynamic mesh strategy optimization

### Planned
- Advanced mesh quality analysis
- Common error detection and resolution
- Integration with more OpenFOAM utilities
- Support for additional meshing tools:
  - cfMesh
  - Third-party meshing tools
- Mesh visualization and preview

## Development

This project uses modern Python tooling:
- `pyproject.toml` for project configuration
- Type hints throughout the codebase
- Rich for beautiful terminal output
- OpenAI GPT-4 for intelligent assistance

To contribute:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Environment Setup

The tool requires an OpenAI API key which can be provided in several ways:
1. Command line argument: `--api-key`
2. Environment variable: `OPENAI_API_KEY`
3. `.env` file in the current directory
4. `.env` file in your home directory

## License

MIT
