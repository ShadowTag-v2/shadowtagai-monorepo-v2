# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import hashlib
import struct
import time
from dataclasses import dataclass
from enum import IntEnum


class Decision(IntEnum):
    DENY = 0
    ALLOW = 1
    ESCALATE = 2


class RiskLevel(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    EXTREMELY_HIGH = 3


@dataclass
class DecisionPacket:
    """Fixed-size: 487 bytes max.
    Layout: Header(32) + Decision(4) + Policy(32) + Reason(256) + Audit(163)
    """

    decision: Decision
    risk_level: RiskLevel
    confidence: int  # 0-10000 (0.00-100.00%)
    policy_hash: bytes  # 32 bytes SHA256
    reason: str  # max 256 chars UTF-8
    audit_context: str  # max 163 chars UTF-8
    timestamp: float  # Unix epoch
    session_hash: bytes  # 16 bytes MD5

    # Struct Compilation for Performance
    HEADER_FMT = struct.Struct(">B d 16s 7x")  # Ver(1)+Time(8)+Sess(16)+Pad(7)
    DECISION_FMT = struct.Struct(">B B H")  # Dec(1)+Risk(1)+Conf(2)

    TOTAL_SIZE = 487
    REASON_SIZE = 256
    AUDIT_SIZE = 163

    def to_bytes(self) -> bytes:
        header = self.HEADER_FMT.pack(1, self.timestamp, self.session_hash[:16])
        decision_block = self.DECISION_FMT.pack(
            self.decision.value,
            self.risk_level.value,
            self.confidence,
        )

        # Zero-pad strings strictly
        policy = self.policy_hash[:32].ljust(32, b"\x00")
        reason_b = self.reason.encode("utf-8")[: self.REASON_SIZE].ljust(self.REASON_SIZE, b"\x00")
        audit_b = self.audit_context.encode("utf-8")[: self.AUDIT_SIZE].ljust(
            self.AUDIT_SIZE,
            b"\x00",
        )

        return header + decision_block + policy + reason_b + audit_b

    @classmethod
    def create(
        cls,
        decision,
        risk_level,
        confidence_pct,
        policies,
        reason,
        audit_context,
        session_id,
    ):
        # Deterministic hashing ensures audit capability
        p_hash = hashlib.sha256(",".join(sorted(policies)).encode()).digest()
        s_hash = hashlib.md5(session_id.encode()).digest()

        return cls(
            decision=decision,
            risk_level=risk_level,
            confidence=int(confidence_pct * 100),
            policy_hash=p_hash,
            reason=reason,
            audit_context=audit_context,
            timestamp=time.time(),
            session_hash=s_hash,
        )
