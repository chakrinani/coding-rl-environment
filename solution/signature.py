"""HMAC signature verification for PayStream webhooks."""

from __future__ import annotations

import hashlib
import hmac


def compute_signature(raw_body: bytes, secret: str) -> str:
    """Compute the expected sha256=<hex> signature for raw request body bytes."""
    digest = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"


def verify_signature(raw_body: bytes, signature_header: str | None, secret: str) -> bool:
    """Return True if the signature header matches the raw request body."""
    if not signature_header:
        return False

    expected = compute_signature(raw_body, secret)
    return hmac.compare_digest(expected, signature_header.strip())
