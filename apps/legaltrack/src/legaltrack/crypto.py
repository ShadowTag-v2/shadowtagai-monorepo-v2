from cryptography.fernet import Fernet

from .config import settings


class CryptoHelper:
  def __init__(self):
    # In a real environment, this should be fetched from GCP Secret Manager/KMS
    self.fernet = Fernet(settings.FERNET_KEY) if settings.FERNET_KEY else None

  def encrypt(self, plain_text: str) -> bytes | None:
    if not self.fernet:
      return plain_text.encode()  # fallback for dev
    return self.fernet.encrypt(plain_text.encode())

  def decrypt(self, cipher_text: bytes) -> str | None:
    if not self.fernet:
      return cipher_text.decode()
    return self.fernet.decrypt(cipher_text).decode()


crypto = CryptoHelper()
