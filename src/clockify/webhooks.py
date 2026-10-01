from __future__ import annotations

import hmac
from typing import Final

SIGNATURE_HEADER: Final = "Clockify-Signature"
EVENT_TYPE_HEADER: Final = "Clockify-Webhook-Event-Type"


def verify_signature(signature: str | None, auth_token: str) -> bool:
    if not signature or not auth_token:
        return False
    # compare_digest runs in constant time, so a wrong signature does not reveal how
    # many leading characters matched.
    return hmac.compare_digest(signature.encode(), auth_token.encode())
