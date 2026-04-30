import hashlib


class NeuralHashEngine:
    def generate_fingerprint(self, stream):
        print("    [ShadowTag] Extracting latent vectors (SHA-256)...")
        if isinstance(stream, str):
            stream = stream.encode("utf-8")
        return hashlib.sha256(stream).hexdigest()
