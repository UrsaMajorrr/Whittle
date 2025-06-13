"""
AI-powered OpenFOAM mesh generation assistant
"""
from pathlib import Path
from typing import Optional, Dict, List
import re
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import openai
import subprocess
from abc import ABC, abstractmethod

class IAIConversationManager(ABC):
    @abstractmethod
    def get_response(self, user_input: str) -> str: pass

class ICaseStructureManager(ABC):
    @abstractmethod
    def setup_case_structure(self) -> None: pass

class IDictionaryFileManager(ABC):
    @abstractmethod
    def extract_dictionaries(self, content: str) -> Dict[str, str]: pass
    @abstractmethod
    def write_dictionaries(self, dictionaries: Dict[str, str]) -> None: pass

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
            model="gpt-4-turbo-preview",
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

class DictionaryFileManager(IDictionaryFileManager):
    def __init__(self, case_dir: Path, console: Console):
        self.case_dir = case_dir
        self.console = console
        self.system_dir = case_dir / "system"
        self.constant_dir = case_dir / "constant"
    
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
    
    def write_dictionaries(self, dictionaries: Dict[str, str]) -> None:
        for dict_name, content in dictionaries.items():
            if dict_name in ["blockMeshDict", "snappyHexMeshDict", "controlDict", "fvSchemes", "fvSolution"]:
                target_dir = self.system_dir
            else:
                target_dir = self.constant_dir
                
            file_path = target_dir / dict_name
            file_path.write_text(content)
            self.console.print(f"[green]✓[/green] Created {dict_name} at {file_path}")

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
    AI-powered assistant for OpenFOAM mesh generation.
    Uses OpenAI to make intelligent decisions about meshing strategy and configuration.
    """
    
    SYSTEM_PROMPT = """You are an expert in OpenFOAM mesh generation. Your task is to help users create appropriate mesh configurations for their CFD cases.
You should:
1. Understand the user's geometry and simulation requirements
2. Recommend the best meshing approach (blockMesh, snappyHexMesh, etc.)
3. Generate appropriate dictionary files including:
   - controlDict (required for all cases)
   - blockMeshDict or snappyHexMeshDict
   - Other necessary system dictionaries
4. Provide clear explanations for your decisions

Always explain your reasoning and provide best practices. If you need more information, ask specific questions.

Output your responses in markdown format. When providing dictionary files, use ```foam code blocks.
For controlDict, always include essential settings like startTime, endTime, deltaT, writeInterval, and writeFormat."""
    
    def __init__(
        self,
        case_dir: Path,
        api_key: str,
        console: Optional[Console] = None
    ):
        self.console = console or Console()
        self.case_dir = case_dir
        
        # Initialize managers
        self.conversation_manager = OpenAIConversationManager(api_key, self.SYSTEM_PROMPT)
        self.case_manager = FileSystemCaseManager(case_dir)
        self.dictionary_manager = DictionaryFileManager(case_dir, self.console)
        self.mesh_executor = MeshExecutor(case_dir, self.console)
        
    def setup_case_structure(self) -> None:
        """Create the basic OpenFOAM case directory structure"""
        self.case_manager.setup_case_structure()
        
    def run(self) -> None:
        """Main entry point for the AI mesh generation assistant"""
        self.console.print(Panel(
            "[bold blue]Welcome to Whittle AI Mesh Assistant![/bold blue]\n\n"
            "I'll help you set up your OpenFOAM mesh using AI-powered recommendations.",
            title="Whittle"
        ))
        
        # Create case structure
        self.setup_case_structure()
        
        # Initial prompt to understand user's needs
        initial_prompt = """I need help creating a mesh for my OpenFOAM case. 
To provide the best recommendations, please ask me questions about:
1. The geometry and its characteristics
2. The type of simulation I want to run
3. Any specific mesh requirements or constraints
4. Simulation time settings needed for controlDict:
   - Start and end times
   - Time step size
   - Write interval
   - Output format"""
        
        # Get AI response
        response = self.conversation_manager.get_response(initial_prompt)
        
        # Display the response
        self.console.print(Markdown(response))
        
        # Continue conversation until mesh is set up
        while True:
            user_input = input("\nYour response ('done' to finish, 'run' to run the mesh): ")
            if user_input.lower() == 'done':
                break
            elif user_input.lower() == 'run':
                self.mesh_executor.run_mesh()
                break
                
            # Get AI response
            response = self.conversation_manager.get_response(user_input)
            
            # Display the response
            self.console.print(Markdown(response))
            
            # Check for dictionary files in the response
            dictionaries = self.dictionary_manager.extract_dictionaries(response)
            if dictionaries:
                self.dictionary_manager.write_dictionaries(dictionaries)
                
        self.console.print("\n[green]✓[/green] Mesh setup complete!")
        self.console.print("\nNext steps:")
        self.console.print("1. Review the generated dictionary files in system/")
        self.console.print("2. Run the suggested mesh generation commands")
        self.console.print("3. Check the mesh quality") 