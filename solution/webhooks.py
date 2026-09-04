"""Webhook endpoint handlers."""

from __future__ import annotations

import json

from flask import Blueprint, current_app, jsonify, request

from app.config import get_webhook_secret
from app.signature import verify_signature
from app.store import event_store

webhooks_bp = Blueprint("webhooks", __name__)


@webhooks_bp.post("/webhooks/paystream")
def paystream_webhook():
    raw_body = request.get_data()
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        return jsonify({"error": "invalid json"}), 400

    if not isinstance(payload, dict):
        return jsonify({"error": "invalid json"}), 400

    signature_header = request.headers.get("X-PayStream-Signature")
    secret = get_webhook_secret()

    if not verify_signature(raw_body, signature_header, secret):
        return jsonify({"error": "invalid signature"}), 401

    event_id = payload.get("event_id")
    amount_cents = payload.get("amount_cents")

    if not event_id or not isinstance(amount_cents, int):
        return jsonify({"error": "invalid payload"}), 400

    store = current_app.config.get("EVENT_STORE", event_store)
    store.record_payment(str(event_id), amount_cents)

    return jsonify({"status": "ok", "event_id": event_id}), 200
