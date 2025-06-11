"""
AI-powered OpenFOAM mesh generation assistant
"""
from pathlib import Path
from typing import Optional, Dict, Any
import re
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import openai

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
    
    def __init__(self, case_dir: Path, console: Optional[Console] = None):
        self.case_dir = case_dir
        self.console = console or Console()
        self.system_dir = case_dir / "system"
        self.constant_dir = case_dir / "constant"
        self.messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        
    def setup_case_structure(self) -> None:
        """Create the basic OpenFOAM case directory structure"""
        self.system_dir.mkdir(parents=True, exist_ok=True)
        self.constant_dir.mkdir(parents=True, exist_ok=True)
        (self.case_dir / "0").mkdir(exist_ok=True)
        (self.constant_dir / "triSurface").mkdir(exist_ok=True)
        
    def get_ai_response(self, user_input: str) -> str:
        """Get response from OpenAI API"""
        self.messages.append({"role": "user", "content": user_input})
        
        response = openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=self.messages,
            temperature=0.7,
        )
        
        ai_response = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": ai_response})
        return ai_response
        
    def extract_dictionary_files(self, ai_response: str) -> Dict[str, str]:
        """Extract OpenFOAM dictionary files from AI response"""
        
        # Find all foam code blocks
        pattern = r"```foam\n(.*?)```"
        matches = re.finditer(pattern, ai_response, re.DOTALL)
        
        # Extract dictionary names and content
        dictionaries = {}
        for match in matches:
            content = match.group(1)
            # Try to find the dictionary name from the FoamFile header
            dict_match = re.search(r"object\s+(\w+);", content)
            if dict_match:
                dict_name = dict_match.group(1)
                dictionaries[dict_name] = content
                
        return dictionaries
        
    def write_dictionary_files(self, dictionaries: Dict[str, str]) -> None:
        """Write dictionary files to the case directory"""
        for dict_name, content in dictionaries.items():
            # Determine the correct directory based on dictionary type
            if dict_name in ["blockMeshDict", "snappyHexMeshDict", "controlDict", "fvSchemes", "fvSolution"]:
                target_dir = self.system_dir
            else:
                target_dir = self.constant_dir
                
            file_path = target_dir / dict_name
            file_path.write_text(content)
            self.console.print(f"[green]✓[/green] Created {dict_name} at {file_path}")
            
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
        response = self.get_ai_response(initial_prompt)
        
        # Display the response
        self.console.print(Markdown(response))
        
        # Continue conversation until mesh is set up
        while True:
            user_input = input("\nYour response (or 'done' to finish): ")
            if user_input.lower() == 'done':
                break
                
            # Get AI response
            response = self.get_ai_response(user_input)
            
            # Display the response
            self.console.print(Markdown(response))
            
            # Check for dictionary files in the response
            dictionaries = self.extract_dictionary_files(response)
            if dictionaries:
                self.write_dictionary_files(dictionaries)
                
        self.console.print("\n[green]✓[/green] Mesh setup complete!")
        self.console.print("\nNext steps:")
        self.console.print("1. Review the generated dictionary files in system/")
        self.console.print("2. Run the suggested mesh generation commands")
        self.console.print("3. Check the mesh quality") 