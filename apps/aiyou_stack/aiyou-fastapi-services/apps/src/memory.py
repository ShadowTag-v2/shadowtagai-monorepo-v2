# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import datetime
import os
from typing import Any

from google.cloud import firestore

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v2")
COLLECTION_NAME = "n-autoresearch/Kosmos/BioAgents_memory"


class FirestoreMemory:
    def __init__(self, project_id: str = PROJECT_ID):
        self.project_id = project_id
        try:
            self.db = firestore.Client(project=project_id)
            print(f"✅ Firestore initialized for project: {project_id}")
        except Exception as e:
            print(f"❌ Failed to initialize Firestore: {e}")
            self.db = None

    def load_from_firestore(self, doc_id: str = "global_context") -> dict[str, Any]:
        """Loads memory context from Firestore."""
        if not self.db:
            return {"status": "ERROR", "detail": "Firestore not initialized"}

        try:
            doc_ref = self.db.collection(COLLECTION_NAME).document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return {"status": "EMPTY", "detail": "No memory found"}
        except Exception as e:
            print(f"❌ Error loading from Firestore: {e}")
            return {"status": "ERROR", "detail": str(e)}

    def save_context(self, data: dict[str, Any], doc_id: str = "global_context"):
        """Saves memory context to Firestore."""
        if not self.db:
            return

        try:
            doc_ref = self.db.collection(COLLECTION_NAME).document(doc_id)
            data["updated_at"] = datetime.datetime.utcnow().isoformat()
            doc_ref.set(data, merge=True)
            print(f"✅ Context saved to {COLLECTION_NAME}/{doc_id}")
        except Exception as e:
            print(f"❌ Error saving to Firestore: {e}")


def get_memory_storage():
    return FirestoreMemory()
