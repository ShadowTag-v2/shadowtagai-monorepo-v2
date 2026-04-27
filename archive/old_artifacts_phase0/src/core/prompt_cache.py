import hashlib


class CacheManager:
    def __init__(self):
        self.last_hashes = {}

    def get_hash(self, content):
        return hashlib.sha256(str(content).encode("utf-8")).hexdigest()

    def detect_break(self, tool_schemas, system_prompt, cache_read_tokens):
        current = {name: self.get_hash(schema) for name, schema in tool_schemas.items()}
        current["system_static"] = self.get_hash(system_prompt.split("<DYNAMIC_BOUNDARY>")[0])

        if cache_read_tokens == 0 and self.last_hashes:
            for key, curr_hash in current.items():
                if self.last_hashes.get(key) != curr_hash:
                    print(f"⚠️ CACHE BUST DETECTED: {key} changed.")
        self.last_hashes = current

    def build_prompt(self, static_rules, dynamic_state):
        return f"{static_rules}\n<DYNAMIC_BOUNDARY>\n{dynamic_state}"
