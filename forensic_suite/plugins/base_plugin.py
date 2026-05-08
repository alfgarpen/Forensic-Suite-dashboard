from abc import ABC, abstractmethod

class BasePlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the plugin (e.g., 'windows.pslist')"""
        pass

    @abstractmethod
    def run(self, dump_path: str) -> dict:
        """
        Executes the plugin analysis on the given memory dump.
        Returns a dictionary with the results.
        """
        pass
