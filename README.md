# OpenFOAM Copilot

An AI-powered assistant for OpenFOAM meshing and workflows. This tool helps with:

- Dictionary file validation and improvement suggestions
- Mesh generation and manipulation
- Best practices recommendations
- Common error resolution

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd openfoam-copilot

# Install in development mode
pip install -e .
```

## Usage

### Check Dictionary Files

```bash
# Check a blockMeshDict file
openfoam-copilot check path/to/blockMeshDict

# Check a snappyHexMeshDict file with explicit type
openfoam-copilot check path/to/dict --type snappyHexMeshDict
```

### Interactive Mesh Generation (Coming Soon)

```bash
# Start interactive mesh generation assistant
openfoam-copilot mesh path/to/case
```

## Features

### Current
- OpenFOAM dictionary file parsing and validation
- Basic syntax checking
- Improvement suggestions

### Planned
- Interactive mesh generation workflow
- Mesh quality analysis
- Common error detection and resolution
- Integration with OpenFOAM utilities
- Support for various mesh generation approaches:
  - blockMesh
  - snappyHexMesh
  - cfMesh
  - Other third-party meshing tools

## Development

This project uses modern Python tooling:
- `pyproject.toml` for project configuration
- Type hints throughout the codebase
- Ruff for linting
- Pytest for testing

To contribute:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT
