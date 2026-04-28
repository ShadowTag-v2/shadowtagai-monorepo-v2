# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import hashlib
import sys


class ShadowTagEngine:
    def __init__(self):
        self.seed = "ANTIGRAVITY_PRIME_2026"
        self.signature = hashlib.sha256(self.seed.encode()).hexdigest()[:8]

    def inject(self, filepath):
        try:
            with open(filepath) as f:
                content = f.read()

            # SKIP IF ALREADY TAGGED
            if f"st_{self.signature}" in content:
                return False

            # L1 TAG: COMMENT INJECTION (Visible)
            header = f"# ▛///▞ SHADOWTAG ID: {self.signature} | DO NOT REMOVE\n"

            # L0 TAG: WHITESPACE STEGANOGRAPHY (Invisible)
            # We encode the signature into trailing spaces/tabs on the last line
            binary = "".join(format(ord(c), "08b") for c in self.signature)
            stego = binary.replace("0", " ").replace("1", "\t")

            new_content = header + content + f"\n# {stego}"

            with open(filepath, "w") as f:
                f.write(new_content)
            return True
        except Exception as e:
            print(f"❌ Error injecting {filepath}: {e}")
            return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 shadowtag_injector.py <file>")
        sys.exit(1)

    injector = ShadowTagEngine()
    target_file = sys.argv[1]
    if injector.inject(target_file):
        print(f"✅ TAGGED: {target_file}")
    else:
        print(f"⏩ SKIPPED: {target_file} (Already Tagged)")
