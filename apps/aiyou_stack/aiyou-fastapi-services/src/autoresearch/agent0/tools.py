import json
import zlib


def atp_519_scan(rule_json: str, scenario_json: str) -> dict:
    """Simulates the ATP 5-19 scan which checks if a rule detects a scenario.
    Also returns compression ratio as a proxy for 'semantic compression'.
    """
    try:
        rule = json.loads(rule_json)
        scenario = json.loads(scenario_json)
    except json.JSONDecodeError:
        return {"detected": False, "compression": 0.0, "error": "Invalid JSON"}

    # Simple logic simulation:
    # If rule 'keywords' are in scenario 'action' or 'args', detected = True.
    detected = False
    keywords = rule.get("keywords", [])

    scenario_text = json.dumps(scenario).lower()

    for kw in keywords:
        if kw.lower() in scenario_text:
            detected = True
            break

    # Semantic compression metric (simulated)
    # Higher is better (smaller rule for same detection)
    rule_bytes = len(rule_json.encode("utf-8"))
    compressed_bytes = len(zlib.compress(rule_json.encode("utf-8")))
    compression_ratio = rule_bytes / compressed_bytes if compressed_bytes > 0 else 0

    return {
        "detected": detected,
        "compression_ratio": compression_ratio,
        "rule_size_bytes": rule_bytes,
    }


def judge6_simulator(rule_json: str, scenario_json: str) -> dict:
    """Simulates Judge #6 decision based on the rule.
    Returns { "allowed": bool, "reason": str }
    """
    scan_result = atp_519_scan(rule_json, scenario_json)
    if scan_result["detected"]:
        return {"allowed": False, "reason": "Blocked by ATP 5-19 Rule"}
    return {"allowed": True, "reason": "Allowed (No detection)"}
