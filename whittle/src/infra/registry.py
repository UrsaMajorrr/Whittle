from typing import Type
from whittle.src.application.cfd_interactor import FOAM, SU2
from whittle.src.application.llm_agent_interactor import OpenAILLMAgent, ClaudeLLMAgent
from whittle.src.entities.cfd_software import CFDSoftware

class SoftwareRegistry:
    def __init__(self):
        self.software = {
            "OpenFOAM": FOAM,
            "SU2": SU2
        }

    def register_software(self, software_name: str, software_class: Type[CFDSoftware]) -> None:
        self.software[software_name] = software_class

    def get_software(self, software_name: str) -> Type[CFDSoftware]:
        if software_name not in self.software:
            raise ValueError(f"Unknown software: {software_name}")
        return self.software[software_name]
    
    def available_software(self) -> list[str]:
        return list(self.software.keys())
    
class ModelRegistry:
    def __init__(self, system_prompt: str = "You are a helpful assistant that can help with CFD simulations."):
        self.models = {
            "gpt": OpenAILLMAgent,
            "claude": ClaudeLLMAgent,
        }
        self.system_prompt = system_prompt

    def get_models(self) -> list[str]:
        return list(self.models.keys())
    
    def get_model(self, model_name: str) -> str:
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        return self.models[model_name](system_prompt=self.system_prompt)