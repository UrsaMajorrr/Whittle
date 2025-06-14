"""
AI-powered OpenFOAM case setup and mesh generation assistant
"""
from pathlib import Path
from typing import Optional, Dict, List, Protocol
from enum import Enum, auto
import re
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import openai
import subprocess
from abc import ABC, abstractmethod

class DictionaryType(Enum):
    SYSTEM = auto()
    CONSTANT = auto()
    INITIAL_CONDITION = auto()
    UNKNOWN = auto()

@dataclass
class DictionaryConfig:
    """Configuration for an OpenFOAM dictionary file"""
    name: str
    type: DictionaryType
    required: bool = False
    dependencies: List[str] = None

class IPromptManager(Protocol):
    """Manages system and user prompts"""
    def get_system_prompt(self) -> str: pass
    def get_initial_prompt(self) -> str: pass
    def update_system_prompt(self, new_prompt: str) -> None: pass

class IFilePathManager(Protocol):
    """Manages OpenFOAM case directory structure"""
    def get_system_dir(self) -> Path: pass
    def get_constant_dir(self) -> Path: pass
    def get_zero_dir(self) -> Path: pass
    def ensure_directories_exist(self) -> None: pass

class IDictionaryClassifier(Protocol):
    """Classifies OpenFOAM dictionary files"""
    def get_dictionary_type(self, dict_name: str) -> DictionaryType: pass
    def get_target_directory(self, dict_type: DictionaryType) -> Path: pass

class IDictionaryExtractor(Protocol):
    """Extracts dictionary content from AI responses"""
    def extract_dictionaries(self, content: str) -> Dict[str, str]: pass

class IDictionaryWriter(Protocol):
    """Writes dictionary files to the appropriate locations"""
    def write_dictionary(self, name: str, content: str, dict_type: DictionaryType) -> None: pass

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

class OpenFOAMFilePathManager(IFilePathManager):
    def __init__(self, case_dir: Path):
        self.case_dir = case_dir
        self.system_dir = case_dir / "system"
        self.constant_dir = case_dir / "constant"
        self.zero_dir = case_dir / "0"
    
    def get_system_dir(self) -> Path:
        return self.system_dir
    
    def get_constant_dir(self) -> Path:
        return self.constant_dir
    
    def get_zero_dir(self) -> Path:
        return self.zero_dir
    
    def ensure_directories_exist(self) -> None:
        self.system_dir.mkdir(parents=True, exist_ok=True)
        self.constant_dir.mkdir(parents=True, exist_ok=True)
        self.zero_dir.mkdir(exist_ok=True)
        (self.constant_dir / "triSurface").mkdir(exist_ok=True)

class OpenFOAMDictionaryClassifier(IDictionaryClassifier):
    def __init__(self, path_manager: IFilePathManager):
        self.path_manager = path_manager
        self.system_files = {
            "blockMeshDict", "snappyHexMeshDict", "controlDict",
            "fvSchemes", "fvSolution"
        }
        self.initial_condition_files = {
            "U", "p", "k", "epsilon", "omega", "nut", "alpha.water", "alpha.air"
        }
    
    def get_dictionary_type(self, dict_name: str) -> DictionaryType:
        if dict_name in self.system_files:
            return DictionaryType.SYSTEM
        elif dict_name in self.initial_condition_files:
            return DictionaryType.INITIAL_CONDITION
        else:
            return DictionaryType.CONSTANT
    
    def get_target_directory(self, dict_type: DictionaryType) -> Path:
        if dict_type == DictionaryType.SYSTEM:
            return self.path_manager.get_system_dir()
        elif dict_type == DictionaryType.INITIAL_CONDITION:
            return self.path_manager.get_zero_dir()
        else:
            return self.path_manager.get_constant_dir()

class FoamDictionaryExtractor(IDictionaryExtractor):
    def extract_dictionaries(self, content: str) -> Dict[str, str]:
        pattern = r"```foam\n(.*?)```"
        matches = re.finditer(pattern, content, re.DOTALL)
        
        dictionaries = {}
        for match in matches:
            content = match.group(1)
            dict_match = re.search(r"object\s+(\w+);", content)
            if dict_match:
                dict_name = dict_match.group(1)
                dictionaries[dict_name] = content
        
        return dictionaries

class OpenFOAMDictionaryWriter(IDictionaryWriter):
    def __init__(self, classifier: IDictionaryClassifier, console: Console):
        self.classifier = classifier
        self.console = console
    
    def write_dictionary(self, name: str, content: str, dict_type: DictionaryType) -> None:
        target_dir = self.classifier.get_target_directory(dict_type)
        file_path = target_dir / name
        file_path.write_text(content)
        self.console.print(f"[green]✓[/green] Created {name} at {file_path}")

class DictionaryManager:
    """Coordinates dictionary operations using the component classes"""
    def __init__(
        self,
        extractor: IDictionaryExtractor,
        classifier: IDictionaryClassifier,
        writer: IDictionaryWriter
    ):
        self.extractor = extractor
        self.classifier = classifier
        self.writer = writer
        
        # Track required files and their status
        self.required_files = {
            "controlDict": False,
            "fvSchemes": False,
            "fvSolution": False,
            "blockMeshDict": False,  # At least one of blockMeshDict or snappyHexMeshDict is required
            "snappyHexMeshDict": False,
            "U": False,  # Basic initial conditions
            "p": False,
        }
        self.written_files = set()
    
    def process_ai_response(self, response: str) -> None:
        """Process an AI response and write any dictionary files found"""
        dictionaries = self.extractor.extract_dictionaries(response)
        for name, content in dictionaries.items():
            dict_type = self.classifier.get_dictionary_type(name)
            self.writer.write_dictionary(name, content, dict_type)
            self.written_files.add(name)
            if name in self.required_files:
                self.required_files[name] = True
    
    def get_missing_required_files(self) -> List[str]:
        """Get list of required files that haven't been written yet"""
        missing = []
        for name, written in self.required_files.items():
            # Special handling for mesh dictionary (need either blockMesh or snappyHexMesh)
            if name in ["blockMeshDict", "snappyHexMeshDict"]:
                if not (self.required_files["blockMeshDict"] or self.required_files["snappyHexMeshDict"]):
                    missing.append("blockMeshDict or snappyHexMeshDict")
                    break
            elif not written:
                missing.append(name)
        return missing

class IAIConversationManager(ABC):
    @abstractmethod
    def get_response(self, user_input: str) -> str: pass

class ICaseStructureManager(ABC):
    @abstractmethod
    def setup_case_structure(self) -> None: pass

class IMeshExecutor(ABC):
    @abstractmethod
    def run_mesh(self) -> None: pass

class OpenAIConversationManager(IAIConversationManager):
    def __init__(self, api_key: str, system_prompt: str):
        self.client = openai.Client(api_key=api_key)
        self.messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
    
    def get_response(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages,
            temperature=0.7,
        )
        
        ai_response = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": ai_response})
        return ai_response

class FileSystemCaseManager(ICaseStructureManager):
    def __init__(self, case_dir: Path):
        self.case_dir = case_dir
        self.system_dir = case_dir / "system"
        self.constant_dir = case_dir / "constant"
    
    def setup_case_structure(self) -> None:
        self.system_dir.mkdir(parents=True, exist_ok=True)
        self.constant_dir.mkdir(parents=True, exist_ok=True)
        (self.case_dir / "0").mkdir(exist_ok=True)
        (self.constant_dir / "triSurface").mkdir(exist_ok=True)

class MeshExecutor(IMeshExecutor):
    def __init__(self, case_dir: Path, console: Console):
        self.case_dir = case_dir
        self.console = console
    
    def run_mesh(self) -> None:
        self.console.print("\n[green]✓[/green] Running mesh generation commands...")
        subprocess.run(["blockMesh"], cwd=self.case_dir)
        subprocess.run(["checkMesh"], cwd=self.case_dir)
        self.console.print("\n[green]✓[/green] Mesh generation complete!")

# Main class using dependency injection
class AIAssistant:
    """
    AI-powered assistant for OpenFOAM case setup and mesh generation.
    """
    def __init__(
        self,
        case_dir: Path,
        api_key: str,
        console: Optional[Console] = None,
        prompt_manager: Optional[IPromptManager] = None,
    ):
        self.console = console or Console()
        
        # Initialize managers
        path_manager = OpenFOAMFilePathManager(case_dir)
        classifier = OpenFOAMDictionaryClassifier(path_manager)
        extractor = FoamDictionaryExtractor()
        writer = OpenFOAMDictionaryWriter(classifier, self.console)
        
        self.prompt_manager = prompt_manager or DefaultPromptManager()
        self.conversation_manager = OpenAIConversationManager(
            api_key, 
            self.prompt_manager.get_system_prompt()
        )
        self.dictionary_manager = DictionaryManager(extractor, classifier, writer)
        self.path_manager = path_manager
        self.mesh_executor = MeshExecutor(case_dir, self.console)
    
    def run(self) -> None:
        """Main entry point for the AI mesh generation assistant"""
        self.console.print(Panel(
            "[bold blue]Welcome to Whittle AI Mesh Assistant![/bold blue]\n\n"
            "I'll help you set up your OpenFOAM case using AI-powered recommendations.",
            title="Whittle"
        ))
        
        # Create case structure
        self.path_manager.ensure_directories_exist()
        
        # Get initial response
        response = self.conversation_manager.get_response(
            self.prompt_manager.get_initial_prompt()
        )
        self.console.print(Markdown(response))
        
        # Continue conversation until mesh is set up
        while True:
            # Check for missing required files
            missing_files = self.dictionary_manager.get_missing_required_files()
            if missing_files:
                self.console.print("\n[yellow]Missing required files:[/yellow]")
                for file in missing_files:
                    self.console.print(f"- {file}")
                self.console.print("\nPlease provide information about these files or type 'generate' to auto-generate them.")
            
            user_input = input("\nYour response ('done' to finish, 'run' to run the mesh, 'generate' for missing files): ")
            
            if user_input.lower() == 'done':
                # Final check for required files before finishing
                missing_files = self.dictionary_manager.get_missing_required_files()
                if missing_files:
                    self.console.print("\n[red]Cannot finish - missing required files:[/red]")
                    for file in missing_files:
                        self.console.print(f"- {file}")
                    continue
                break
            elif user_input.lower() == 'run':
                # Check required files before running mesh
                missing_files = self.dictionary_manager.get_missing_required_files()
                if missing_files:
                    self.console.print("\n[red]Cannot run mesh - missing required files:[/red]")
                    for file in missing_files:
                        self.console.print(f"- {file}")
                    continue
                self.mesh_executor.run_mesh()
                break
            elif user_input.lower() == 'generate':
                # Ask AI to create missing files
                missing_files = self.dictionary_manager.get_missing_required_files()
                missing_files_prompt = f"""Please create the following required OpenFOAM dictionary files that are still missing:
{', '.join(missing_files)}

For each file, provide the complete dictionary content in ```foam code blocks."""
                
                response = self.conversation_manager.get_response(missing_files_prompt)
                self.console.print(Markdown(response))
                self.dictionary_manager.process_ai_response(response)
            else:
                # Get AI response for user input
                response = self.conversation_manager.get_response(user_input)
                self.console.print(Markdown(response))
                
                # Process any dictionary files in the response
                self.dictionary_manager.process_ai_response(response)
        
        self.console.print("\n[green]✓[/green] Case setup complete!")
        self.console.print("\nNext steps:")
        self.console.print("1. Review the generated dictionary files")
        self.console.print("2. Run the mesh generation commands")
        self.console.print("3. Check the mesh quality") 