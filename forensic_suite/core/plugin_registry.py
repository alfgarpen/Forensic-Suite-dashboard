# plugin_registry.py

PLUGIN_REGISTRY = {
    "windows": {
        "System Info": {
            "windows.info": "General system information and metadata.",
        },
        "Processes": {
            "windows.pslist": "List of running processes.",
            "windows.pstree": "Process tree structure.",
            "windows.cmdline": "Command line arguments for processes.",
            "windows.handles": "Open handles for each process.",
            "windows.dlllist": "Loaded DLLs for each process.",
        },
        "Network": {
            "windows.netscan": "Active network connections and sockets.",
            "windows.netstat": "Network statistics and status.",
        },
        "Malware": {
            "windows.malfind": "Detection of potentially injected code and memory artifacts.",
            "windows.ldrmodules": "Detect unlinked DLLs.",
        },
        "Registry/Persistence": {
            "windows.registry.printkey": "Print registry keys and values.",
            "windows.registry.hivelist": "List available registry hives.",
            "windows.services": "List of Windows services.",
        },
        "Users": {
            "windows.getsids": "List SIDs for processes.",
            "windows.hashdump": "Extract password hashes from memory.",
        }
    },
    "linux": {
        "System Info": {
            "linux.info": "Linux system information.",
            "linux.banner": "Display the kernel banner.",
        },
        "Processes": {
            "linux.pslist": "List of running processes.",
            "linux.pstree": "Process tree structure.",
        },
        "Network": {
            "linux.netstat": "Network connections and statistics.",
        },
        "Kernel": {
            "linux.lsmod": "List loaded kernel modules.",
            "linux.check_modules": "Check for hidden kernel modules.",
        },
        "Environment": {
            "linux.bash": "Recover bash command history.",
            "linux.envars": "List process environment variables.",
        }
    },
    "mac": {
        "Processes": {
            "mac.pslist": "List of running processes.",
        },
        "Network": {
            "mac.netstat": "Network connections.",
        }
    }
}

def get_plugins_for_os(os_name: str) -> dict:
    """Returns the plugin categories and plugins for a specific OS."""
    return PLUGIN_REGISTRY.get(os_name.lower(), {})

def get_all_plugins() -> list:
    """Returns a flat list of all plugin names."""
    all_plugins = []
    for os_plugins in PLUGIN_REGISTRY.values():
        for category in os_plugins.values():
            all_plugins.extend(category.keys())
    return list(set(all_plugins))

def is_plugin_compatible(plugin_name: str, os_name: str) -> bool:
    """Checks if a plugin is compatible with the given OS."""
    os_plugins = get_plugins_for_os(os_name)
    for category in os_plugins.values():
        if plugin_name in category:
            return True
    return False
