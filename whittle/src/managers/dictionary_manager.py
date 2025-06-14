from typing import List, Dict
from whittle.src.interfaces.dictionary_interfaces import (
    IDictionaryExtractor, IDictionaryClassifier, IDictionaryWriter, DictionaryType)
from whittle.src.interfaces.file_path_interface import IFilePathManager
from pathlib import Path
import re
from rich.console import Console

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
    def __init__(self, solver_name: str):
        self.solver_name = solver_name

    def extract_dictionaries(self, content: str) -> Dict[str, str]:
        # Try solver-specific code block first
        pattern = rf"```{self.solver_name}\n(.*?)```"
        matches = list(re.finditer(pattern, content, re.DOTALL))
        # Fallback: match any code block
        if not matches:
            pattern = r"```[a-zA-Z]*\n(.*?)```"
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