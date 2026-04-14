"""Security utilities for secret management and encryption.
"""

import base64
import os
from pathlib import Path
from typing import Any

import yaml
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


class SecretManager:
    """Manages secrets and sensitive configuration.

    Supports:
    - Environment variable loading
    - YAML secrets file
    - Encrypted storage
    """

    def __init__(self, secrets_file: Path | None = None, encryption_key: bytes | None = None):
        """Initialize secret manager.

        Args:
            secrets_file: Path to secrets YAML file
            encryption_key: Optional encryption key for encrypted secrets

        """
        self.secrets_file = secrets_file or Path("configs/secrets.yml")
        self.encryption_key = encryption_key
        self._secrets: dict[str, Any] = {}
        self._cipher = None

        if encryption_key:
            self._cipher = Fernet(encryption_key)

        self._load_secrets()

    def _load_secrets(self) -> None:
        """Load secrets from file and environment"""
        # Load from file if exists
        if self.secrets_file.exists():
            with open(self.secrets_file) as f:
                self._secrets = yaml.safe_load(f) or {}

        # Override with environment variables
        for key, value in os.environ.items():
            if key.startswith("SHADOWTAG_"):
                clean_key = key.replace("SHADOWTAG_", "").lower()
                self._secrets[clean_key] = value

    def get(self, key: str, default: Any = None, decrypt: bool = False) -> Any:
        """Get a secret value.

        Args:
            key: Secret key (supports dot notation, e.g., 'database.password')
            default: Default value if key not found
            decrypt: Whether to decrypt the value

        Returns:
            Secret value

        """
        # Navigate nested dict using dot notation
        parts = key.split(".")
        value = self._secrets

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return default

            if value is None:
                return default

        # Decrypt if requested and cipher available
        if decrypt and self._cipher and isinstance(value, str):
            try:
                value = self._cipher.decrypt(value.encode()).decode()
            except Exception:
                pass  # Return encrypted value if decryption fails

        return value

    def set(self, key: str, value: Any, encrypt: bool = False) -> None:
        """Set a secret value (in memory only).

        Args:
            key: Secret key
            value: Secret value
            encrypt: Whether to encrypt the value

        """
        # Encrypt if requested and cipher available
        if encrypt and self._cipher:
            value = self._cipher.encrypt(str(value).encode()).decode()

        # Handle nested keys
        parts = key.split(".")
        target = self._secrets

        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]

        target[parts[-1]] = value

    def save(self, filepath: Path | None = None) -> None:
        """Save secrets to file.

        WARNING: Only save to secure locations!

        Args:
            filepath: Path to save to (uses default if None)

        """
        path = filepath or self.secrets_file
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            yaml.dump(self._secrets, f, default_flow_style=False)

    @staticmethod
    def generate_key(password: str, salt: bytes | None = None) -> bytes:
        """Generate encryption key from password.

        Args:
            password: Password to derive key from
            salt: Optional salt (generated if None)

        Returns:
            Encryption key

        """
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )

        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key


class EnvironmentLoader:
    """Load and validate environment variables"""

    @staticmethod
    def load_dotenv(env_file: Path = Path(".env")) -> dict[str, str]:
        """Load environment variables from .env file.

        Args:
            env_file: Path to .env file

        Returns:
            Dictionary of environment variables

        """
        env_vars = {}

        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        env_vars[key] = value
                        os.environ[key] = value

        return env_vars

    @staticmethod
    def validate_required(required_vars: list) -> bool:
        """Validate that required environment variables are set.

        Args:
            required_vars: List of required variable names

        Returns:
            True if all required vars are set

        Raises:
            ValueError: If any required var is missing

        """
        missing = [var for var in required_vars if var not in os.environ]

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        return True


# Global secret manager instance
_secret_manager: SecretManager | None = None


def get_secret_manager() -> SecretManager:
    """Get global secret manager instance"""
    global _secret_manager

    if _secret_manager is None:
        _secret_manager = SecretManager()

    return _secret_manager


def get_secret(key: str, default: Any = None) -> Any:
    """Convenience function to get a secret.

    Args:
        key: Secret key
        default: Default value

    Returns:
        Secret value

    """
    return get_secret_manager().get(key, default)
