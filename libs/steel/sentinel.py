# libs/steel/sentinel.py
import logging

# Configure Judge 6 Logger
logger = logging.getLogger("Judge6")


# Mock AntigravityEngine for God Mode prototype
class MockAntigravityEngine:
    def recall_solution(self, code):
        return None

    def remember_fix(self, crime, evidence, status):
        pass


class JudgeSixSentinel:
    """
    The Governance Layer.
    Intercepts Agent intentions and blocks them if they violate Doctrine.
    """

    def __init__(self, db_engine=None):
        self.db = db_engine or MockAntigravityEngine()
        self.banned_patterns = [
            "sk-",
            "ghp_",
            "passwd",
            "rm -rf /",  # Hardcoded "Capital Crimes"
            ".env",
            "id_rsa",
        ]

    def vet_code_diff(self, file_path: str, proposed_code: str) -> bool:
        """
        PRE-CRIME: Checks code before it is written to disk.
        """
        # 1. Regex check for secrets
        for pattern in self.banned_patterns:
            if pattern in proposed_code:
                self._record_violation("SECRET_LEAK", f"Found {pattern} in {file_path}")
                return False

        # 2. Structural Check (AST) - Prevent Logic Bombs (Future connection to ast-grep)

        # 3. Precedent Check (AlloyDB)
        # Ask the Hippocampus: "Have we rejected similar code before?"
        similar_bad_code = self.db.recall_solution(proposed_code)  # Using recall for negative matching
        if similar_bad_code and "REJECTED" in similar_bad_code:
            self._record_violation("PRECEDENT_VIOLATION", "Code matches previously rejected pattern.")
            return False

        return True

    def vet_network_request(self, url: str) -> bool:
        """
        RUNTIME: Checks URL against Allow/Block lists.
        """
        blocked_tlds = [".ru", ".cn", ".tk", ".top"]
        if any(url.endswith(tld) for tld in blocked_tlds):
            self._record_violation("E-BORDER_CROSSING", f"Attempted access to {url}")
            return False
        return True

    def _record_violation(self, crime: str, evidence: str):
        logger.critical(f"🛑 JUDGE 6 INTERVENTION: {crime} - {evidence}")
        # Log to AlloyDB "Criminal Record"
        self.db.remember_fix(f"VIOLATION: {crime}", evidence, "BLOCKED")
