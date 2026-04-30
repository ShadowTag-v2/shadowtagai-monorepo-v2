class ContentModerator:
    def scan_content(self, payload):
        print("    [SafetyNet] Scanning for toxicity...")
        toxic_keywords = ["malware", "exploit", "attack", "virus"]
        content = str(payload).lower()
        for kw in toxic_keywords:
            if kw in content:
                print(f"    [SafetyNet] BLOCKED: Found {kw}")
                return {"status": "BLOCKED", "reason": kw}
        return {"status": "CLEAN", "score": 0.99}
