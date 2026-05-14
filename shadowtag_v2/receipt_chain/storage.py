# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Chain Storage

Handles persistent storage and retrieval of receipt chains.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import sqlite3
from datetime import datetime

from .chain import ReceiptChain


class ChainStorage:
    """
    Persistent storage for receipt chains.

    Supports:
    - SQLite database storage
    - JSON file export/import
    - Chain indexing and querying
    """

    def __init__(self, db_path: Path | None = None):
        """
        Initialize chain storage.

        Args:
            db_path: Path to SQLite database. Uses in-memory if None.
        """
        self.db_path = db_path or ":memory:"
        self.conn: sqlite3.Connection | None = None
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize database schema"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

        # Create chains table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS chains (
                chain_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                block_count INTEGER NOT NULL,
                is_valid BOOLEAN NOT NULL,
                data TEXT NOT NULL
            )
        """)

        # Create receipts table for indexing
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chain_id TEXT NOT NULL,
                operation_id TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                media_type TEXT NOT NULL,
                method TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                media_hash TEXT NOT NULL,
                FOREIGN KEY (chain_id) REFERENCES chains(chain_id),
                UNIQUE(chain_id, operation_id)
            )
        """)

        # Create indices
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_receipts_chain_id
            ON receipts(chain_id)
        """)

        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_receipts_operation_id
            ON receipts(operation_id)
        """)

        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_receipts_timestamp
            ON receipts(timestamp)
        """)

        self.conn.commit()

    def save_chain(self, chain: ReceiptChain) -> None:
        """
        Save a chain to storage.

        Args:
            chain: Chain to save
        """
        chain_data = chain.export_to_json()
        now = datetime.utcnow().isoformat()

        # Insert or replace chain
        self.conn.execute(
            """
            INSERT OR REPLACE INTO chains
            (chain_id, created_at, updated_at, block_count, is_valid, data)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                chain.chain_id,
                chain.blocks[0].header.timestamp if chain.blocks else now,
                now,
                len(chain.blocks),
                chain.verify_chain(),
                chain_data,
            ),
        )

        # Delete old receipts for this chain
        self.conn.execute(
            """
            DELETE FROM receipts WHERE chain_id = ?
        """,
            (chain.chain_id,),
        )

        # Index receipts
        for block in chain.blocks[1:]:  # Skip genesis
            receipt = block.receipt
            self.conn.execute(
                """
                INSERT INTO receipts
                (chain_id, operation_id, operation_type, timestamp,
                 media_type, method, payload_hash, media_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    chain.chain_id,
                    receipt.operation_id,
                    receipt.operation_type,
                    receipt.timestamp,
                    receipt.media_type,
                    receipt.method,
                    receipt.payload_hash,
                    receipt.media_hash,
                ),
            )

        self.conn.commit()

    def load_chain(self, chain_id: str) -> ReceiptChain | None:
        """
        Load a chain from storage.

        Args:
            chain_id: ID of chain to load

        Returns:
            ReceiptChain if found, None otherwise
        """
        cursor = self.conn.execute(
            """
            SELECT data FROM chains WHERE chain_id = ?
        """,
            (chain_id,),
        )

        row = cursor.fetchone()
        if not row:
            return None

        chain_data = json.loads(row["data"])
        return ReceiptChain.import_from_dict(chain_data)

    def list_chains(self) -> list[dict[str, Any]]:
        """
        List all chains in storage.

        Returns:
            List of chain metadata dictionaries
        """
        cursor = self.conn.execute("""
            SELECT chain_id, created_at, updated_at, block_count, is_valid
            FROM chains
            ORDER BY updated_at DESC
        """)

        return [dict(row) for row in cursor.fetchall()]

    def delete_chain(self, chain_id: str) -> bool:
        """
        Delete a chain from storage.

        Args:
            chain_id: ID of chain to delete

        Returns:
            True if deleted, False if not found
        """
        # Delete receipts first
        self.conn.execute(
            """
            DELETE FROM receipts WHERE chain_id = ?
        """,
            (chain_id,),
        )

        # Delete chain
        cursor = self.conn.execute(
            """
            DELETE FROM chains WHERE chain_id = ?
        """,
            (chain_id,),
        )

        self.conn.commit()
        return cursor.rowcount > 0

    def search_receipts(
        self,
        operation_id: str | None = None,
        operation_type: str | None = None,
        media_type: str | None = None,
        payload_hash: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for receipts matching criteria.

        Args:
            operation_id: Filter by operation ID
            operation_type: Filter by operation type
            media_type: Filter by media type
            payload_hash: Filter by payload hash

        Returns:
            List of matching receipts with chain information
        """
        query = "SELECT * FROM receipts WHERE 1=1"
        params = []

        if operation_id:
            query += " AND operation_id = ?"
            params.append(operation_id)

        if operation_type:
            query += " AND operation_type = ?"
            params.append(operation_type)

        if media_type:
            query += " AND media_type = ?"
            params.append(media_type)

        if payload_hash:
            query += " AND payload_hash = ?"
            params.append(payload_hash)

        query += " ORDER BY timestamp DESC"

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def export_chain_to_file(self, chain_id: str, filepath: Path) -> bool:
        """
        Export a chain to JSON file.

        Args:
            chain_id: Chain to export
            filepath: Output file path

        Returns:
            True if successful, False if chain not found
        """
        chain = self.load_chain(chain_id)
        if not chain:
            return False

        chain.export_to_json(filepath)
        return True

    def import_chain_from_file(self, filepath: Path) -> str:
        """
        Import a chain from JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            Chain ID of imported chain

        Raises:
            ValueError: If file is invalid
        """
        json_str = filepath.read_text()
        chain = ReceiptChain.import_from_json(json_str)
        self.save_chain(chain)
        return chain.chain_id

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
