# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import re


class JudgeSix:
    BANNED = [r"sk-[a-zA-Z0-9]{20,}", r"rm -rf", r".env"]

    def vet(self, code: str) -> bool:
        """Pre-Crime Analysis."""
        for pattern in self.BANNED:
            if re.search(pattern, code):
                print(f"⛔ JUDGE 6 BLOCK: Hazard {pattern} detected.")
                return False
        return True
