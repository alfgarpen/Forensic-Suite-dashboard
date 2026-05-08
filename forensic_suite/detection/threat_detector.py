import logging

logger = logging.getLogger(__name__)

class ThreatDetector:
    def __init__(self):
        self.alerts = []
        self.severity = "low"

    def analyze(self, engine_results: dict) -> dict:
        """
        Analyzes the results from the AnalysisEngine and detects suspicious 
        processes, weird connections, etc.
        """
        self.alerts = []
        self.severity = "low"

        # 1. Check correlations
        correlations = engine_results.get("correlations", {})
        missing_process = correlations.get("connections_missing_process", [])
        if missing_process:
            self.alerts.append(f"Detected {len(missing_process)} network connections without an associated running process.")
            self.severity = "high"

        # 2. Check for suspicious process names
        plugins_data = engine_results.get("plugins", {})
        pslist_data = plugins_data.get("windows.pslist", plugins_data.get("linux.pslist", {}))
        if pslist_data and "processes" in pslist_data:
            suspicious_names = ["malware.exe", "nc.exe", "mimikatz.exe", "cmd.exe", "powershell.exe",
                                "nc", "netcat", "ncat", "cryptominer", "backdoor", "rootkit", "python-shell"]
            for proc in pslist_data["processes"]:
                if any(name in proc["name"].lower() for name in suspicious_names):
                    self.alerts.append(f"Suspicious process detected: {proc['name']} (PID: {proc['pid']})")
                    if self.severity != "high":
                        self.severity = "medium"
                    if any(name in proc["name"].lower() for name in ["malware", "mimikatz", "nc", "cryptominer", "rootkit"]):
                        self.severity = "high"
        
        # 3. YARA matches
        yara_data = engine_results.get("yara", {})
        if yara_data and yara_data.get("status") == "success":
            matches = yara_data.get("matches", [])
            for match in matches:
                self.alerts.append(f"YARA Rule Matched: {match['rule']}")
                self.severity = "high"

        return {
            "alerts": self.alerts,
            "severity": self.severity
        }
