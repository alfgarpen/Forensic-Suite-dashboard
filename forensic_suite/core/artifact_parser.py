import logging
import re

logger = logging.getLogger(__name__)

class GenericTableParser:
    """
    Utility to parse columnar text output (like ps, netstat, tasklist) into a list of dicts.
    """
    @staticmethod
    def parse_text_table(text: str) -> list:
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        if not lines:
            return []

        # Heuristic: First line is usually the header
        header_line = lines[0]
        # Split header by multiple spaces
        headers = re.split(r'\s{2,}', header_line)
        if len(headers) < 2:
            # Try splitting by single space if it looks like a simple table
            headers = header_line.split()

        results = []
        for line in lines[1:]:
            # Attempt to split line according to header positions or whitespace
            # Simple approach: split by whitespace but try to match header count
            parts = re.split(r'\s+', line, maxsplit=len(headers) - 1)
            
            if len(parts) == len(headers):
                row = {headers[i]: parts[i] for i in range(len(headers))}
                results.append(row)
            else:
                # If splitting fails to match header count, store as raw if necessary or skip
                # For now, we skip malformed lines in this generic parser
                pass
        
        return results

class ArtifactParser:
    @staticmethod
    def parse(plugin_name: str, raw_data) -> dict:
        """
        Normalizes raw Volatility 3 JSON data or fallback text into a structured format.
        """
        # Handle fallback text output
        if isinstance(raw_data, str):
            table_data = GenericTableParser.parse_text_table(raw_data)
            if table_data:
                return {
                    "status": "success",
                    "type": "table",
                    "items": table_data,
                    "count": len(table_data)
                }
            return {"status": "success", "output": raw_data}

        if not isinstance(raw_data, list):
            return {"error": "Invalid data format (expected list or string)"}

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
