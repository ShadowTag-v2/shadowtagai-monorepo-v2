import re
from dataclasses import dataclass

# --- Regex Compilation (Module Level for Speed) ---
PROB_PATTERNS = [
    ("A", re.compile(r"(always|continuous|constant|every time)")),
    ("B", re.compile(r"(often|usually|regularly|common)")),
    ("C", re.compile(r"(sometimes|occasional|intermittent)")),
    ("D", re.compile(r"(rarely|seldom|infrequent|unlikely)")),
    ("E", re.compile(r"(almost never|improbable|remote)")),
]

SEV_PATTERNS = [
    ("I", re.compile(r"(death|total loss|regulatory shutdown|criminal|catastrophic)")),
    ("II", re.compile(r"(major injury|severe damage|significant fine|critical)")),
    ("III", re.compile(r"(minor injury|degraded capability|warning|marginal)")),
    ("IV", re.compile(r"(no injury|minimal impact|cosmetic|negligible)")),
]

ENTITY_PATTERNS = [
    ("PHI", re.compile(r"(phi|health|medical|patient|hipaa)")),
    ("PII", re.compile(r"(pii|personal|ssn|identity)")),
    ("financial", re.compile(r"(financial|payment|credit|bank)")),
    ("classified", re.compile(r"(classified|secret|confidential|restricted)")),
]

# Action verbs mapped to governance intent
ACTION_REGEX = re.compile(r"(create|delete|modify|access|transfer|approve|deny|escalate)")
VIOLATION_REGEX = re.compile(r"(breach|unauthorized|prohibited|restricted|blocked|denied)")
POLICY_REGEX = re.compile(r"([A-Z]{2,}-[\d\.]+|PNKLN-[A-Z]+-\d+)")

# Fast set lookup for sentence filtering
KEYWORD_SET = {
    "must",
    "shall",
    "prohibited",
    "allowed",
    "denied",
    "risk",
    "require",
    "critical",
    "urgent",
}

# --- Risk Matrix (ATP 5-19 Standard) ---
RISK_MATRIX = {
    ("A", "I"): "EH",
    ("A", "II"): "EH",
    ("A", "III"): "H",
    ("A", "IV"): "M",
    ("B", "I"): "EH",
    ("B", "II"): "H",
    ("B", "III"): "H",
    ("B", "IV"): "L",
    ("C", "I"): "H",
    ("C", "II"): "H",
    ("C", "III"): "M",
    ("C", "IV"): "L",
    ("D", "I"): "H",
    ("D", "II"): "M",
    ("D", "III"): "L",
    ("D", "IV"): "L",
    ("E", "I"): "M",
    ("E", "II"): "L",
    ("E", "III"): "L",
    ("E", "IV"): "L",
}


@dataclass
class ATP519Extract:
    risk_probability: str
    risk_severity: str
    risk_level: str
    action_requested: str
    entity_type: str
    violations: list[str]
    policy_refs: list[str]
    compressed_context: str


def atp_519_scan(
    context: str,
    domain: str = "general",
    max_context_chars: int = 500,
) -> ATP519Extract:
    if not context:
        return ATP519Extract("C", "III", "M", "access", "general", [], [], "")

    context_lower = context.lower()

    # 1. Probability
    prob = "C"
    for level, pattern in PROB_PATTERNS:
        if pattern.search(context_lower):
            prob = level
            break

    # 2. Severity
    sev = "III"
    for level, pattern in SEV_PATTERNS:
        if pattern.search(context_lower):
            sev = level
            break

    # 3. Risk Level
    risk_level = RISK_MATRIX.get((prob, sev), "M")

    # 4. Semantics
    action_match = ACTION_REGEX.search(context_lower)
    action = action_match.group(1) if action_match else "access"

    entity = "general"
    for etype, pattern in ENTITY_PATTERNS:
        if pattern.search(context_lower):
            entity = etype
            break

    violations = list(set(VIOLATION_REGEX.findall(context_lower)))[:3]
    policy_refs = list(set(POLICY_REGEX.findall(context)))[:5]

    # 5. Semantic Context Filtering
    sentences = context.replace("!", ".").replace("?", ".").split(".")
    key_sentences = []
    current_chars = 0

    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        # Fast intersection check
        sent_words = set(sent.lower().split())
        if not sent_words.isdisjoint(KEYWORD_SET):
            sent_len = len(sent)
            if current_chars + sent_len > max_context_chars:
                break
            key_sentences.append(sent)
            current_chars += sent_len + 2

    compressed_context = ". ".join(key_sentences)[:max_context_chars]

    return ATP519Extract(
        risk_probability=prob,
        risk_severity=sev,
        risk_level=risk_level,
        action_requested=action,
        entity_type=entity,
        violations=violations,
        policy_refs=policy_refs,
        compressed_context=compressed_context,
    )
