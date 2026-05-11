# artifact_parser.py

import logging

logger = logging.getLogger(__name__)

class ArtifactParser:
    @staticmethod
    def parse(plugin_name: str, raw_data: list) -> dict:
        """
        Normalizes raw Volatility 3 JSON data into a structured format.
        """
        if not isinstance(raw_data, list):
            return {"error": "Invalid data format (expected list)"}

        if "pslist" in plugin_name:
            return ArtifactParser._parse_pslist(raw_data)
        elif "netscan" in plugin_name or "netstat" in plugin_name:
            return ArtifactParser._parse_network(raw_data)
        elif "malfind" in plugin_name:
            return ArtifactParser._parse_malfind(raw_data)
        elif "info" in plugin_name:
            return ArtifactParser._parse_info(raw_data)
        
        # Default: return raw data wrapped in a success status
        return {"status": "success", "data": raw_data}

    @staticmethod
    def _parse_pslist(data: list) -> dict:
        processes = []
        for entry in data:
            processes.append({
                "pid": entry.get("PID", entry.get("Pid", "N/A")),
                "ppid": entry.get("PPID", entry.get("PPid", "N/A")),
                "name": entry.get("ImageFileName", entry.get("Name", "Unknown")),
                "offset": hex(entry.get("Offset", 0)) if "Offset" in entry else "N/A",
                "threads": entry.get("Threads", "N/A"),
                "handles": entry.get("Handles", "N/A"),
                "session": entry.get("SessionId", "N/A"),
                "wow64": entry.get("Wow64", "N/A"),
                "create_time": entry.get("CreateTime", entry.get("Created", "N/A")),
                "exit_time": entry.get("ExitTime", "N/A")
            })
        return {
            "status": "success",
            "type": "processes",
            "items": processes,
            "count": len(processes)
        }

    @staticmethod
    def _parse_network(data: list) -> dict:
        connections = []
        for entry in data:
            connections.append({
                "pid": entry.get("PID", entry.get("Pid", "N/A")),
                "local_addr": entry.get("LocalAddr", entry.get("Address", "N/A")),
                "local_port": entry.get("LocalPort", entry.get("Port", "N/A")),
                "remote_addr": entry.get("ForeignAddr", entry.get("RemoteAddr", "N/A")),
                "remote_port": entry.get("ForeignPort", entry.get("RemotePort", "N/A")),
                "proto": entry.get("Proto", entry.get("Protocol", "N/A")),
                "state": entry.get("State", "N/A"),
                "owner": entry.get("Owner", "N/A")
            })
        return {
            "status": "success",
            "type": "network",
            "items": connections,
            "count": len(connections)
        }

    @staticmethod
    def _parse_malfind(data: list) -> dict:
        findings = []
        for entry in data:
            findings.append({
                "pid": entry.get("PID", "N/A"),
                "process": entry.get("Process", "Unknown"),
                "start": hex(entry.get("StartPtr", 0)) if "StartPtr" in entry else "N/A",
                "end": hex(entry.get("EndPtr", 0)) if "EndPtr" in entry else "N/A",
                "tag": entry.get("Tag", "N/A"),
                "protection": entry.get("Protection", "N/A")
            })
        return {
            "status": "success",
            "type": "malware",
            "items": findings,
            "count": len(findings)
        }

    @staticmethod
    def _parse_info(data: list) -> dict:
        # Volatility info usually returns a single entry or a list of key-values
        info = {}
        if data and isinstance(data[0], dict):
            info = data[0]
        return {
            "status": "success",
            "type": "system_info",
            "data": info
        }
