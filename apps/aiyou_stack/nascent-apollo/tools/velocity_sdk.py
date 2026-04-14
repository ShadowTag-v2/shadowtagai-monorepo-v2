import json
import subprocess


class VelocityEngine:
    """The Hunter-Killer.
    Wraps 'rg' (RipGrep) and 'sg' (ast-grep) for high-speed code search and refactoring.
    Includes PM2 Log Bridge.
    """

    def search(self, query: str, path: str = ".", type: str = "text") -> str:
        """Executes a high-speed search.
        type: 'text' (rg) or 'ast' (sg)
        """
        if type == "ast":
            # Semantic/Structural Search (Placeholder for ast-grep)
            # cmd = ["sg", "scan", "-p", query, path]
            return "COMBAT LOG: 'sg' (ast-grep) not yet installed. Use 'text' (rg)."

        # Default: Text Search (RipGrep)
        try:
            cmd = ["rg", "--json", query, path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return self._parse_rg_json(result.stdout)
        except FileNotFoundError:
            return "COMBAT LOG: 'rg' (ripgrep) not found. Install it for Hunter-Killer mode."

    def _parse_rg_json(self, output: str) -> str:
        matches = []
        for line in output.split("\n"):
            if not line:
                continue
            try:
                data = json.loads(line)
                if data["type"] == "match":
                    file = data["data"]["path"]["text"]
                    line_num = data["data"]["line_number"]
                    content = data["data"]["lines"]["text"].strip()
                    matches.append(f"🎯 [{file}:{line_num}] {content}")
            except:
                continue
        return "\n".join(matches[:20])  # Limit output to avoid flooding

    def read_pm2_logs(self, service: str = "backend", lines: int = 50) -> str:
        """Reads the logs of a PM2 managed process.
        """
        try:
            cmd = ["pm2", "logs", service, "--lines", str(lines), "--nostream", "--raw"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return f"PM2 ERROR: {result.stderr}"
            return result.stdout
        except FileNotFoundError:
            return "PM2 ERROR: 'pm2' command not found."


if __name__ == "__main__":
    eng = VelocityEngine()
    print(eng.search("TODO"))
