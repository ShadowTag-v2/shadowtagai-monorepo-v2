"""ShadowTag cryptographic verification models.

Provides provenance attestation for all platform operations.
"""

import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class VerificationRecord(Base):
    """Individual verification record.

    Each record represents a single signed event in the system.
    """

    __tablename__ = "shadowtag_verifications"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Event details
    event_type = Column(
        String(100), nullable=False, index=True,
    )  # content_upload, payment, session_start
    entity_type = Column(String(100), nullable=False, index=True)  # content, order, stream
    entity_id = Column(String(36), nullable=False, index=True)

    # Cryptographic proof
    signature = Column(String(500), nullable=False, unique=True, index=True)
    public_key = Column(String(500), nullable=False)
    algorithm = Column(String(50), default="ED25519")

    # Provenance chain
    chain_id = Column(String(100), nullable=False, index=True)
    previous_signature = Column(String(500), index=True)  # Links to previous record
    merkle_root = Column(String(500))

    # Metadata
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True,
    )
    node_id = Column(String(36), index=True)  # Which infrastructure node signed
    location_data = Column(JSON)  # GPS coords (if applicable)

    # Payload
    payload_hash = Column(String(128), nullable=False)  # SHA-512 hash of payload
    payload_metadata = Column(JSON)  # Additional context

    # Verification status
    is_verified = Column(Boolean, default=True, index=True)
    verified_at = Column(DateTime(timezone=True))
    verification_failures = Column(Integer, default=0)

    # Relationships
    chain = relationship(
        "VerificationChain",
        foreign_keys="VerificationRecord.chain_id",
        primaryjoin="VerificationRecord.chain_id==VerificationChain.id",
        back_populates="records",
    )

    def __repr__(self):
        return f"<VerificationRecord(id={self.id}, event_type={self.event_type}, signature={self.signature[:16]}...)>"


class VerificationChain(Base):
    """Verification chain model.

    Groups related verification records into a provenance chain.
    """

    __tablename__ = "shadowtag_chains"

    # Primary key
    id = Column(String(100), primary_key=True)  # User-defined or generated

    # Chain metadata
    chain_type = Column(String(100), nullable=False, index=True)  # content, transaction, session
    root_entity_type = Column(String(100))
    root_entity_id = Column(String(36), index=True)

    # Genesis
    genesis_signature = Column(String(500), unique=True, index=True)
    genesis_timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Current state
    latest_signature = Column(String(500))
    latest_timestamp = Column(DateTime(timezone=True))
    record_count = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_immutable = Column(Boolean, default=False)  # Once immutable, no more records can be added
    immutable_at = Column(DateTime(timezone=True))

    # Merkle tree
    merkle_tree_root = Column(String(500))
    merkle_tree_depth = Column(Integer)

    # Audit
    audit_log_url = Column(String(1000))  # External audit trail
    compliance_flags = Column(JSON)  # Regulatory compliance markers

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    records = relationship(
        "VerificationRecord",
        foreign_keys="VerificationRecord.chain_id",
        primaryjoin="VerificationChain.id==VerificationRecord.chain_id",
        back_populates="chain",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<VerificationChain(id={self.id}, type={self.chain_type}, records={self.record_count})>"
