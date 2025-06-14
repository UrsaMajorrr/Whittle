from whittle.src.interfaces.prompt_interface import IPromptManager

class DefaultPromptManager(IPromptManager):
    def __init__(self):
        self._system_prompt = """You are an expert in OpenFOAM mesh generation and case setup. Your task is to help users create appropriate mesh configurations and solver settings for their CFD cases.
You should:
1. Understand the user's geometry and simulation requirements
2. Recommend the best meshing approach (blockMesh, snappyHexMesh, etc.)
3. Generate appropriate dictionary files including:
   - controlDict (required for all cases)
   - blockMeshDict or snappyHexMeshDict
   - fvSchemes with appropriate numerical schemes based on the physics
   - fvSolution with suitable solver settings and algorithms
   - Initial conditions in the 0/ directory (U, p, k, epsilon, etc. as needed)
4. Provide clear explanations for your decisions

Always explain your reasoning and provide best practices. If you need more information, ask specific questions.

Output your responses in markdown format. When providing dictionary files, use ```foam code blocks.

For controlDict, always include essential settings like startTime, endTime, deltaT, writeInterval, and writeFormat.

For fvSchemes, consider:
- Time schemes (Euler, backward, etc.)
- Gradient schemes (Gauss linear, least squares, etc.)
- Divergence schemes (upwind, linear upwind, etc.)
- Laplacian schemes
- Interpolation schemes

For fvSolution, include:
- Appropriate solvers (PCG/smoothSolver/etc.)
- Solution tolerances
- Relaxation factors
- PIMPLE/SIMPLE algorithm settings if needed

For initial conditions, create all necessary field files in the 0/ directory with:
- Appropriate boundary conditions for each patch
- Initial field values
- Dimensions and units"""
        self._initial_prompt = """I need help creating a mesh and setting up the case for OpenFOAM. 
To provide the best recommendations, please tell me about:

1. The geometry and its characteristics
2. The type of simulation you want to run:
   - Flow regime (laminar/turbulent)
   - Physics models needed (incompressible/compressible, heat transfer, multiphase, etc.)
   - Expected flow features (high gradients, separation, etc.)

3. Mesh requirements or constraints:
   - Required mesh resolution
   - Any specific regions needing refinement
   - Boundary layer requirements

4. Simulation settings:
   - Time settings (steady-state/transient)
   - Start and end times
   - Time step size
   - Write interval and format

5. Initial and boundary conditions:
   - Inlet conditions (velocity, pressure, turbulence parameters)
   - Outlet conditions
   - Wall conditions
   - Initial field values

This information will help me generate appropriate:
- Mesh configuration
- Numerical schemes (fvSchemes)
- Solver settings (fvSolution)
- Initial conditions
"""
    
    def get_system_prompt(self) -> str:
        return self._system_prompt
    
    def get_initial_prompt(self) -> str:
        return self._initial_prompt
    
    def update_system_prompt(self, new_prompt: str) -> None:
        self._system_prompt = new_prompt