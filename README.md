# Whittle - AI-Powered CFD Assistant

An AI-powered assistant for CFD case setup and mesh generation, supporting multiple CFD solvers through a plugin architecture.

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Whittle
```

2. Install the package in development mode:
```bash
pip3 install -e .
```

This will install all required dependencies and make the `whittle` module importable.

## Project Structure

```
whittle/
├── __init__.py              # Package initialization
├── config.py               # Configuration settings
└── src/                    # Source code
    ├── __init__.py
    ├── ai_assistant.py     # Main AI assistant class
    ├── api/                # API-related modules
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

## Usage

### Basic Usage

```python
from whittle.src.ai_assistant import AIAssistant
from pathlib import Path

# Initialize the assistant
assistant = AIAssistant(
    api_key="your_openai_api_key",
    solver_name="openfoam",
    case_dir=Path.cwd()
)

# Run the assistant
assistant.run()
```

### Available Solvers

Currently supported CFD solvers:
- OpenFOAM
- SU2

### Environment Variables

Set the following environment variables for API access:
- `OPENAI_API_KEY` - For OpenAI GPT models
- `ANTHROPIC_API_KEY` - For Claude models

## Development

### Testing Imports

Run the test script to verify all modules can be imported correctly:

```bash
python3 test_imports.py
```

### Running the Main Application

```bash
python3 main.py
```

Note: You'll need to set the `OPENAI_API_KEY` environment variable for full functionality.

## Dependencies

- Python 3.12+
- rich - For beautiful console output
- openai - For OpenAI API integration
- anthropic - For Claude API integration
- python-dotenv - For environment variable management

## License

[Add your license information here]
