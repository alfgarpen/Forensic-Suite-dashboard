# plugin_registry.py

PLUGIN_REGISTRY = {
    "windows": {
        "System Info": {
            "windows.info.Info": "General system information and metadata.",
        },
        "Processes": {
            "windows.pslist.PsList": "List of running processes.",
            "windows.pstree.PsTree": "Process tree structure.",
            "windows.cmdline.CmdLine": "Command line arguments for processes.",
            "windows.handles.Handles": "Open handles for each process.",
            "windows.dlllist.DllList": "Loaded DLLs for each process.",
        },
        "Network": {
            "windows.netscan.NetScan": "Active network connections and sockets.",
            "windows.netstat.NetStat": "Network statistics and status.",
        },
        "Malware": {
            "windows.malfind.Malfind": "Detection of potentially injected code and memory artifacts.",
            "windows.ldrmodules.LdrModules": "Detect unlinked DLLs.",
        },
        "Registry/Persistence": {
            "windows.registry.printkey.PrintKey": "Print registry keys and values.",
            "windows.registry.hivelist.HiveList": "List available registry hives.",
            "windows.services.Services": "List of Windows services.",
        },
        "Users": {
            "windows.getsids.GetSIDs": "List SIDs for processes.",
            "windows.hashdump.Hashdump": "Extract password hashes from memory.",
        }
    },
    "linux": {
        "System Info": {
            "banners.Banners": "Display the kernel banner and system info.",
        },
        "Processes": {
            "linux.pslist.PsList": "List of running processes.",
            "linux.pstree.PsTree": "Process tree structure.",
            "linux.psaux.PsAux": "List processes with aux information.",
        },
        "Network": {
            "linux.sockstat.Sockstat": "Network connections and statistics.",
        },
        "Kernel": {
            "linux.lsmod.Lsmod": "List loaded kernel modules.",
            "linux.check_modules.Check_modules": "Check for hidden kernel modules.",
        },
        "Environment": {
            "linux.bash.Bash": "Recover bash command history.",
            "linux.envars.Envars": "List process environment variables.",
        }
    },
    "mac": {
        "Processes": {
            "mac.pslist.PsList": "List of running processes.",
        },
        "Network": {
            "mac.netstat.Netstat": "Network connections.",
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
