import os
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


def generate_did_key():
  """Generates an Ed25519 key pair for a DID and saves them to local files."""
  private_key = ed25519.Ed25519PrivateKey.generate()
  public_key = private_key.public_key()

  # Extract raw public bytes for did:key (simplified representation for PoC)
  raw_public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
  )
  did_key = f"did:key:z{raw_public_bytes.hex()}"
  print(f"Generated DID: {did_key}")

  # Save private key in OpenSSH format for git commit signing
  priv_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.OpenSSH,
    encryption_algorithm=serialization.NoEncryption(),
  )

  # Save public key in OpenSSH format
  pub_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.OpenSSH, format=serialization.PublicFormat.OpenSSH
  )

  os.makedirs("keys", exist_ok=True)
  with open("keys/agent_did_ed25519", "wb") as f:
    f.write(priv_bytes)

  with open("keys/agent_did_ed25519.pub", "wb") as f:
    f.write(pub_bytes)

  print("Keys saved to keys/agent_did_ed25519 and keys/agent_did_ed25519.pub")


if __name__ == "__main__":
  generate_did_key()
