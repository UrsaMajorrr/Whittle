"""Plugin initialization"""
from whittle.src.managers.plugin_registry import PluginRegistry
from whittle.src.plugins.openfoam_plugin import OpenFOAMPlugin

# Register available plugins
PluginRegistry.register_plugin(OpenFOAMPlugin)

# When adding a new solver plugin:
# 1. Create a new plugin class implementing SolverPlugin
# 2. Import it here
# 3. Register it with PluginRegistry.register_plugin()

# Package marker for plugins 