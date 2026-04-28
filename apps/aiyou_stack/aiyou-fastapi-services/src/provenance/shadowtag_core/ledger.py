# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import hashlib
import json
import time


class ShadowTagLedger:
    def __init__(self, log_path="shadowtag_ledger.jsonl"):
        self.log_path = log_path

    def mint_receipt(self, data: dict):
        payload = json.dumps(data, sort_keys=True).encode()
        r_hash = hashlib.sha256(payload).hexdigest()
        entry = {"ts": time.time(), "hash": r_hash, "data": data}
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return r_hash
