"""
AGNT Two-Stage Classifier & Security Filters

Implements:
- P2.1 Two-Stage Classifier (Tool YOLO vs Block)
- P5.1 Fail-Closed Error Handling
- P5.3 Assistant Text Exclusion
"""

import re
import logging

logger = logging.getLogger(__name__)

# ── XML Intent Router (Domain Classifier) ──

# Map XML tag names to agent domains
_TAG_DOMAIN_MAP = {
    "intent": "db_architect",
    "search": "osint_agent",
    "code": "code_agent",
    "deploy": "deploy_agent",
}


class XMLClassifier:
    """Simple XML-tag intent router.

    Extracts the outermost XML tag and maps it to an agent domain.
    Unknown tags route to 'general_agent'.
    """

    def classify(self, text: str) -> str:
        match = re.match(r"<(\w+)>", text.strip())
        if match:
            tag = match.group(1).lower()
            return _TAG_DOMAIN_MAP.get(tag, "general_agent")
        return "general_agent"

    @staticmethod
    def strip_xml(text: str) -> str:
        """Remove all XML elements (tag pairs + content) from text, returning plain content."""
        # First remove matched tag pairs with their content
        stripped = re.sub(r"<(\w+)[^>]*>.*?</\1>", "", text, flags=re.DOTALL)
        # Then remove any remaining standalone tags
        stripped = re.sub(r"<[^>]+>", "", stripped)
        return stripped.strip()


# ── Two-Stage Security Classifier ──


def fail_closed_handler(func):
    """P5.1: Any exception in classifier MUST result in DENY/BLOCK."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Classifier error (fail-closed triggered): {e}")
            return "BLOCK"  # Or another appropriate deny state

    return wrapper


class AssistantTextExcluder:
    """P5.3: Strip all assistant conversational text BEFORE passing to classifier."""

    @staticmethod
    def extract_tool_blocks(text: str) -> str:
        """
        Only <tool_call> or [COMMAND] blocks are analyzed.
        """
        tool_calls = re.findall(r"<tool_call>(.*?)</tool_call>", text, re.DOTALL)
        commands = re.findall(r"\[COMMAND\](.*?)\[/COMMAND\]", text, re.DOTALL)

        extracted = "\n".join(tool_calls + commands).strip()
        return extracted if extracted else text.strip()


class TwoStageClassifier:
    """
    P2.1: Two-Stage Classifier
    Stage 1: Fast, bias toward blocking.
    Stage 2: Thinking, full chain-of-thought reasoning.
    """

    def __init__(self):
        self.fast_llm_mock_call = self._mock_fast_llm
        self.thinking_llm_mock_call = self._mock_thinking_llm

    def _mock_fast_llm(self, query: str) -> str:
        # Mock logic: bias towards blocking. If safe pattern, ALLOW.
        safe_patterns = ["echo", "ls", "pwd", "git status"]
        for p in safe_patterns:
            if p in query.lower():
                return "ALLOW"
        return "UNKNOWN"

    def _mock_thinking_llm(self, query: str) -> str:
        # Mock CoT logic that outputs <block>yes/no</block>
        if "rm -rf" in query.lower():
            return "<block>yes</block>"
        return "<block>no</block>"

    @fail_closed_handler
    def classify(self, raw_text: str) -> str:
        # P5.3: Strip conversational text
        clean_query = AssistantTextExcluder.extract_tool_blocks(raw_text)

        if not clean_query:
            return "BLOCK"

        # Stage 1
        stage1_result = self.fast_llm_mock_call(clean_query)
        if stage1_result == "ALLOW":
            return "ALLOW"

        # Stage 2 (escalated)
        stage2_result = self.thinking_llm_mock_call(clean_query)
        match = re.search(r"<block>(yes|no)</block>", stage2_result.lower())

        if match and match.group(1) == "no":
            return "ALLOW"

        return "BLOCK"
