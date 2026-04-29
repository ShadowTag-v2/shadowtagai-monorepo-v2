import json
import os


class YoloClassifier:
    def __init__(self):
        self.log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".beads", "yolo_decisions.jsonl")
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def classify_action(self, action_name: str, args: dict) -> str:
        """
        Determine the risk level of a YOLO action.
        LOW: Auto-execute (e.g., reads, safe queries)
        MEDIUM: Auto-execute but requires heavy Tengu logging
        HIGH: Drop to STATE B — Clutch
        """
        low_risk = ["list_dir", "read_file", "search_web", "view_file"]
        high_risk = ["rm", "sudo", "force-push", "db-drop"]

        if any(tool in action_name.lower() for tool in low_risk):
            risk = "LOW"
        elif any(tool in action_name.lower() for tool in high_risk):
            risk = "HIGH"
        else:
            risk = "MEDIUM"

        self._log_decision(action_name, args, risk)
        return risk

    def _log_decision(self, action_name: str, args: dict, risk: str):
        payload = {"action": action_name, "args_summary": str(args)[:100], "risk_assigned": risk}
        with open(self.log_file, "a") as f:
            f.write(json.dumps(payload) + "\n")


if __name__ == "__main__":
    classifier = YoloClassifier()
    print("Action 'list_dir' risk:", classifier.classify_action("list_dir", {"path": "/tmp"}))
    print("Action 'run_command' (rm -rf) risk:", classifier.classify_action("run_command", {"command": "rm -rf /"}))
    print("Action 'generate_image' risk:", classifier.classify_action("generate_image", {"prompt": "test"}))
