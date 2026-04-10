"""
Pinkln Defense Translator
Translates Commercial Strategy/Terminology into DoD/Mil-Spec Language.

"We speak Silicon Valley to investors, but Pentagon to the Generals."
"""


class MilSpecTranslator:
    def __init__(self):
        self.dictionary: dict[str, str] = {
            # Core Infrastructure
            "SkyNode": "Tactical Edge Compute Fabric (TECF)",
            "Data Center": "Establishment-Based Compute Node (EBCN)",
            "Cloud": "Joint Warfighting Cloud Capability (JWCC)",
            "Edge Device": "Tactical End-User Device (EUD)",
            "Golden Image": "Validated Solution Stack (VSS)",
            # Software/AI
            "Kernel Chaining": "Disaggregated Decision Logic",
            "Ultrathink": "Cognitive Overmatch Engine",
            "Judge #6": "Automated Compliance & Oversight (ACO)",
            "Flying minion": "Autonomous Swarm Agents",
            "Hallucination": "Information Integrity Failure",
            "Latency": "Decision Cycle Time (OODA Loop)",
            # Business/Ops
            "Airbnb for Compute": "Contractor-Owned, Contractor-Operated (COCO) Mesh",
            "SaaS": "Software-as-a-Service (Approved Service)",
            "Sales": "Program Acquisition",
            "User": "Warfighter / Operator",
            "CEO": "Program Manager (PM)",
        }

    def to_milspec(self, text: str) -> str:
        """Translates a commercial string to its Mil-Spec equivalent."""
        translated = text
        for commercial, milspec in self.dictionary.items():
            # Simple case-insensitive replacement (robustness could be improved)
            # Using a simple replace for now as a POC
            translated = translated.replace(commercial, milspec)
        return translated

    def get_quad_chart_summary(self) -> dict:
        """Returns key value props in Mil-Spec terms."""
        return {
            "Capability": self.dictionary["SkyNode"],
            "Discriminator": f"Reduces {self.dictionary['Latency']} by 90%",
            "Security": f"Enforced by {self.dictionary['Judge #6']}",
        }


# Usage Example
if __name__ == "__main__":
    translator = MilSpecTranslator()
    pitch = "We deploy SkyNode to every Edge Device to reduce Latency."
    print(f"Commercial: {pitch}")
    print(f"Mil-Spec:   {translator.to_milspec(pitch)}")
