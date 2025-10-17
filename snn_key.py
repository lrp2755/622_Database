import os, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# Accept either name; prefer MY_APP_MASTER_SECRET but SECRET_KEY works too.
_MASTER_B64 = os.environ.get("SECRET_KEY")
if not _MASTER_B64:
    raise RuntimeError(
        "Missing encryption key. Set SECRET_KEY to a base64-encoded 32-byte random value."
    )

try:
    MASTER = base64.b64decode(_MASTER_B64)
except Exception as e:
    raise RuntimeError("Failed to base64-decode the key env var.") from e

if len(MASTER) < 32:
    raise RuntimeError(
        f"Key too short: need >= 32 bytes after base64 decode, got {len(MASTER)}."
    )

def _derive_keys(master: bytes):
    hkdf = HKDF(algorithm=hashes.SHA256(), length=64, salt=None, info=b"ssn-storage-v1")
    out = hkDF = hkdf.derive(master)
    return out[:32], out[32:]  # enc_key, hmac_key

ENC_KEY, HMAC_KEY = _derive_keys(MASTER)

def encrypt_ssn(plain_ssn: str) -> str:
    aes = AESGCM(ENC_KEY)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, plain_ssn.encode("utf-8"), None)
    return base64.b64encode(nonce + ct).decode("ascii")

def decrypt_ssn(b64_payload: str) -> str:
    raw = base64.b64decode(b64_payload)
    nonce, ct = raw[:12], raw[12:]
    aes = AESGCM(ENC_KEY)
    pt = aes.decrypt(nonce, ct, None)
    return pt.decode("utf-8")

def ssn_hash(plain_ssn: str) -> str:
    h = hmac.HMAC(HMAC_KEY, hashes.SHA256())
    h.update(plain_ssn.encode("utf-8"))
    return h.finalize().hex()
