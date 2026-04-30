import traceback

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

try:
    print("Hashing empty password...")
    h = pwd_context.hash("")
    print(f"Hash: {h}")
except Exception:
    traceback.print_exc()

try:
    print("Hashing long password...")
    h = pwd_context.hash("a" * 73)
    print(f"Hash: {h}")
except Exception:
    traceback.print_exc()
