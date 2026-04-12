import logging
import os
import sys
from enum import Enum

from colorama import Fore, Style

try:
    sys.path.append(os.getcwd())
    from src.governance.memory.memory_bank import MemoryBank
    from src.governance.voting.cav_mtoe import CavMTOE

    ARMY_AVAILABLE = True
except ImportError:
    ARMY_AVAILABLE = False

logger = logging.getLogger("Judge6")


class RiskTier(Enum):
    GREEN = "L (Auto-Approve)"
    YELLOW = "M (Manager Check)"
    ORANGE = "H (Executive Check)"
    RED = "EH (STOP / Kill-Switch)"


# HAZARD DB (ATP 5-19 Mapped) - Updated for Omega Context
HAZARD_DB = [
    {"pattern": "sk-", "name": "API Key Leak", "risk": RiskTier.RED},
    {"pattern": "rm -rf", "name": "System Wipe", "risk": RiskTier.RED},
    {"pattern": "0.0.0.0/0", "name": "Open Network", "risk": RiskTier.RED},
    {"pattern": "grant_all", "name": "Permissive Access", "risk": RiskTier.ORANGE},
    {"pattern": "<TODO>", "name": "Incomplete Code", "risk": RiskTier.YELLOW},
]


class JudgeSixSentinel:
    def __init__(self, engine=None):
        self.engine = engine
        self.name = "Judge #6 V2.0.0 (Omega)"
        self.memory = MemoryBank()
        self.army = CavMTOE(num_soldiers=650) if ARMY_AVAILABLE else None

    def vet_code_diff(self, file_pattern: str, proposed_fix: str) -> tuple[bool, RiskTier, str]:
        logger.info(f"{Fore.YELLOW}>>> ⚖️  Judge 6 Scan: {file_pattern}...{Style.RESET_ALL}")

        # 1. MEMORY CHECK
        if "from * import" in proposed_fix:
            if self.memory.consult(file_pattern, "allow_wildcard_imports") == "ALLOW":
                logger.info(f"{Fore.BLUE}>>> 🧠 MEMORY: Suppressing alert.{Style.RESET_ALL}")
                return True, RiskTier.GREEN, proposed_fix

        # 2. HAZARD SCAN
        max_risk = RiskTier.GREEN
        for h in HAZARD_DB:
            if h["pattern"] in proposed_fix:
                max_risk = h["risk"]
                logger.info(f"{Fore.MAGENTA}>>> ⚠️  HAZARD DETECTED: {h['name']}{Style.RESET_ALL}")

        # 3. AUTHORITY CHECK
        if max_risk == RiskTier.RED:
            logger.info(f"{Fore.RED}>>> ⛔ VERDICT: HARD STOP{Style.RESET_ALL}")
            return False, max_risk, proposed_fix

        if max_risk in [RiskTier.ORANGE, RiskTier.YELLOW] and self.army:
            intent = f"Accept {max_risk.name} risk in {file_pattern}."
            vote = self.army.bottom_up_vote(intent=intent, risk_level="H")
            logger.info(
                f"{Fore.CYAN}>>> 🗳️  ARMY VOTE: {vote['final_action']} ({vote['approval_rate']:.1%}){Style.RESET_ALL}"
            )
            if vote["final_action"] != "A":
                return False, max_risk, proposed_fix

        logger.info(f"{Fore.GREEN}>>> ✅ VERDICT: PASS{Style.RESET_ALL}")
        return True, max_risk, proposed_fix
