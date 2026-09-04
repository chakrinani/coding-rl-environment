"""HMAC signature verification for PayStream webhooks."""

from __future__ import annotations

import hashlib
import hmac
import json


def compute_signature(payload: dict, secret: str) -> str:
    """Compute the expected sha256=<hex> signature for a payload dict."""
    # BUG: serializes the parsed dict instead of using the provider's raw body bytes.
    # JSON key order and whitespace will differ from what PayStream signed.
    body = json.dumps(payload, separators=(",", ":"))
    digest = hmac.new(
        secret.encode("utf-8"),
        body.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"


def verify_signature(payload: dict, signature_header: str | None, secret: str) -> bool:
    """Return True if the signature header matches the payload."""
    if not signature_header:
        return False

    expected = compute_signature(payload, secret)
    return hmac.compare_digest(expected, signature_header.strip())
