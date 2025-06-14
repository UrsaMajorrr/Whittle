from typing import Dict, Type
from whittle.src.interfaces.solver_plugin import SolverPlugin

class PluginRegistry:
    """Registry for solver plugins"""
    
    _plugins: Dict[str, Type[SolverPlugin]] = {}
    
    @classmethod
    def register_plugin(cls, plugin_class: Type[SolverPlugin]) -> None:
        """Register a new solver plugin"""
        plugin = plugin_class()
        cls._plugins[plugin.solver_name.lower()] = plugin_class
    
    @classmethod
    def get_plugin(cls, solver_name: str) -> SolverPlugin:
        """Get a plugin instance by solver name"""
        plugin_class = cls._plugins.get(solver_name.lower())
        if not plugin_class:
            available = ", ".join(cls._plugins.keys())
            raise ValueError(
                f"No plugin found for solver '{solver_name}'. "
                f"Available solvers: {available}"
            )
        return plugin_class()
    
    @classmethod
    def available_solvers(cls) -> list[str]:
        """Get list of available solver names"""
        return list(cls._plugins.keys()) 