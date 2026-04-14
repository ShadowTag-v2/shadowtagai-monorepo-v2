"""ShadowTag Immutable Ledger (BigQuery Implementation)

Implements a secure, append-only ledger for ShadowTag verification events using Google BigQuery.
Future upgrades can bridge this to public chains (Ethereum/Solana) via Oracle.

Schema:
- content_id: STRING (UUID)
- content_hash: STRING (Neural Hash)
- timestamp: TIMESTAMP
- judge_six_verdict: STRING
- trust_score: FLOAT
- provenance_chain: ARRAY<STRING>
"""

import datetime
import logging
from typing import Any

from google.cloud import bigquery

logger = logging.getLogger(__name__)


class ShadowLedger:
    def __init__(
        self,
        project_id: str = "acquired-jet-478701-b3",
        dataset_id: str = "antigravity_bi",
        table_id: str = "shadowtag_ledger",
    ):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.client = bigquery.Client(project=project_id)
        self.table_ref = f"{project_id}.{dataset_id}.{table_id}"

        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Create the ledger table if it doesn't exist."""
        try:
            self.client.get_table(self.table_ref)
        except Exception:
            logger.info(f"Creating Ledger Table: {self.table_ref}")
            schema = [
                bigquery.SchemaField("content_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("content_hash", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("judge_six_verdict", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("trust_score", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("provenance_chain", "STRING", mode="REPEATED"),
            ]
            table = bigquery.Table(self.table_ref, schema=schema)
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY, field="timestamp",
            )
            self.client.create_table(table)

    def record_verification(self, verification_result: dict[str, Any]) -> bool:
        """Record a verification event to the immutable ledger.

        Args:
            verification_result: Dict containing:
                - content_id
                - content_hash (signature)
                - judge_six_verdict
                - trust_score
                - provenance_chain (list of signer IDs)

        Returns:
            bool: True if recorded successfully.

        """
        rows_to_insert = [
            {
                "content_id": verification_result.get("content_id"),
                "content_hash": verification_result.get("content_hash"),
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "judge_six_verdict": verification_result.get("judge_six_verdict"),
                "trust_score": verification_result.get("trust_score"),
                "provenance_chain": verification_result.get("provenance_chain", []),
            },
        ]

        errors = self.client.insert_rows_json(self.table_ref, rows_to_insert)
        if errors == []:
            logger.info(f"Ledger Entry Recorded: {verification_result.get('content_id')}")
            return True
        logger.error(f"Ledger Write Failed: {errors}")
        return False


# Singleton
_ledger_instance = None


def get_ledger() -> ShadowLedger:
    global _ledger_instance
    if _ledger_instance is None:
        _ledger_instance = ShadowLedger()
    return _ledger_instance
