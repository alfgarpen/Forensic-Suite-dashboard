import importlib
import pkgutil
import logging
from forensic_suite.plugins.base_plugin import BasePlugin
from forensic_suite.plugins import windows, linux

logger = logging.getLogger(__name__)

class VolatilityService:
    """Service to manage and discover plugins"""
    
    def __init__(self):
        self.plugins = {}
        self._discover_plugins()

    def _discover_plugins(self):
        """Dynamically loads plugins from the specific namespace/packages."""
        self._load_package(windows)
        self._load_package(linux)

    def _load_package(self, package):
        prefix = package.__name__ + "."
        for _, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
            if not ispkg:
                try:
                    module = importlib.import_module(modname)
                    for attribute_name in dir(module):
                        attribute = getattr(module, attribute_name)
                        if isinstance(attribute, type) and issubclass(attribute, BasePlugin) and attribute is not BasePlugin:
                            plugin_instance = attribute()
                            self.plugins[plugin_instance.name] = plugin_instance
                            logger.info(f"Loaded plugin: {plugin_instance.name}")
                except Exception as e:
                    logger.error(f"Failed to load plugin {modname}: {e}")

    def get_available_plugins(self) -> list:
        return list(self.plugins.keys())

    def get_plugin(self, name: str) -> BasePlugin:
        return self.plugins.get(name)
