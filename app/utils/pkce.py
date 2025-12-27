import hashlib
import base64


def verify_pkce(code_verifier: str, code_challenge: str) -> bool:
    digest = hashlib.sha256(code_verifier.encode()).digest()
    calculated = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return calculated == code_challenge