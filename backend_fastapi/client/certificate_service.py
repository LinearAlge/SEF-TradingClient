from __future__ import annotations

import base64
import json
from typing import Dict

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


class CertificateService:
    def verify_signature(self, public_jwk: str, challenge: str, signature: str) -> bool:
        try:
            jwk = json.loads(public_jwk)
            public_key = self._load_public_key(jwk)
            if not public_key:
                return False
            signature_bytes = base64.b64decode(signature)
            public_key.verify(
                signature_bytes,
                challenge.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False

    def _load_public_key(self, jwk: Dict[str, str]):
        if jwk.get("kty") != "RSA":
            return None
        n = self._int_from_base64url(jwk.get("n", ""))
        e = self._int_from_base64url(jwk.get("e", ""))
        if n is None or e is None:
            return None
        from cryptography.hazmat.primitives.asymmetric import rsa

        return rsa.RSAPublicNumbers(e, n).public_key()

    def _int_from_base64url(self, value: str) -> int | None:
        try:
            padded = value + "=" * (-len(value) % 4)
            return int.from_bytes(base64.urlsafe_b64decode(padded), "big")
        except Exception:
            return None
