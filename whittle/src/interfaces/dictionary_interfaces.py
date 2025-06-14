from typing import Dict, Protocol, List
from dataclasses import dataclass
from pathlib import Path
from enum import Enum, auto

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
    dependencies: List[str] = None # List of dictionary names that this dictionary depends on

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