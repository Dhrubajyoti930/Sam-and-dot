import importlib.util
from pathlib import Path

class BasePlugin:
    def run(self, context: dict):
        raise NotImplementedError

class PluginManager:
    def __init__(self, plugin_dir: Path):
        self.plugin_dir = plugin_dir
        self.plugins = []

    def run(self, context: dict):
        for plugin in self.plugins:
            plugin.run(context)

    def load_plugins(self):
        for path in self.plugin_dir.glob("*.py"):
            if path.name == "__init__.py": continue
            spec = importlib.util.spec_from_file_location(path.stem, path)
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                if hasattr(module, "Plugin"):
                    self.plugins.append(module.Plugin())
            except Exception as e:
                print(f"Failed to load plugin {path.name}: {e}")