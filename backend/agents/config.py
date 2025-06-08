from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Default LLM configuration
DEFAULT_LLM_CONFIG = {
    "config_list": [{
        "model": "gpt-4",
        "api_key": api_key,
        "temperature": 0.7,
        "max_tokens": 1500,
        "timeout": 60
    }],
    "cache_seed": None,  # Disable caching for debugging
    "temperature": 0.7,
    "timeout": 60
}

# CAD Agent Configuration
CAD_AGENT_CONFIG = {
    "name": "cad_agent",
    "llm_config": DEFAULT_LLM_CONFIG,
    "system_message": """You are a CAD (Computer-Aided Design) Agent specialized in 3D modeling and design.
    
    Your expertise includes:
    - Parametric modeling and design
    - 3D geometry creation and manipulation
    - Design optimization and validation
    - Manufacturing constraints and considerations
    - Common CAD file formats and standards
    
    You can help users with:
    - Creating new 3D models from specifications
    - Modifying existing designs
    - Analyzing design feasibility
    - Suggesting design improvements
    - Converting between different CAD formats
    
    Always maintain a focus on practical, manufacturable designs while considering
    engineering constraints and requirements."""
}

# Meshing Agent Configuration
MESH_AGENT_CONFIG = {
    "name": "mesh_agent",
    "llm_config": DEFAULT_LLM_CONFIG,
    "system_message": """You are a Meshing Agent specialized in preparing geometries for simulation.
    
    Your expertise includes:
    - Mesh generation and optimization
    - Mesh quality assessment
    - Boundary layer meshing
    - Multi-physics mesh requirements
    - Mesh adaptation strategies
    
    You can help users with:
    - Creating simulation-ready meshes
    - Optimizing mesh density
    - Handling complex geometries
    - Setting up boundary conditions
    - Resolving mesh-related issues
    
    Always focus on creating high-quality meshes that balance accuracy and computational efficiency."""
}

# Simulation Agent Configuration
SIMULATION_AGENT_CONFIG = {
    "name": "simulation_agent",
    "llm_config": DEFAULT_LLM_CONFIG,
    "system_message": """You are a Simulation Agent specialized in engineering analysis.
    
    Your expertise includes:
    - Computational Fluid Dynamics (CFD)
    - Finite Element Analysis (FEA)
    - Thermal analysis
    - Multi-physics simulations
    - Results interpretation
    
    You can help users with:
    - Setting up simulation cases
    - Choosing appropriate physics models
    - Defining boundary conditions
    - Analyzing results
    - Optimizing designs based on simulation
    
    Always maintain a focus on accurate physics modeling and practical engineering solutions."""
}

# Domain-specific configurations
DOMAIN_CONFIGS = {
    "mechanical": {
        "default_constraints": {
            "material_properties": True,
            "manufacturing_constraints": True,
            "structural_analysis": True
        },
        "simulation_types": ["stress", "strain", "modal", "thermal"]
    },
    "aerospace": {
        "default_constraints": {
            "aerodynamics": True,
            "structural_integrity": True,
            "weight_optimization": True
        },
        "simulation_types": ["cfd", "structural", "aeroelastic"]
    },
    "civil": {
        "default_constraints": {
            "building_codes": True,
            "structural_safety": True,
            "environmental_impact": True
        },
        "simulation_types": ["structural", "seismic", "thermal"]
    }
} 