"""Outcome-based grader for the PayStream webhook task."""

from __future__ import annotations

import hashlib
import hmac
import json

import pytest

from conftest import TEST_SECRET, sign_raw_body


def post_signed(client, payload: dict, *, secret: str = TEST_SECRET, tamper: bool = False):
    raw_body = json.dumps(payload).encode("utf-8")
    signature = sign_raw_body(raw_body, secret)
    if tamper:
        tampered_payload = {**payload, "amount_cents": payload.get("amount_cents", 0) + 9999}
        raw_body = json.dumps(tampered_payload).encode("utf-8")
    return client.post(
        "/webhooks/paystream",
        data=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-PayStream-Signature": signature,
        },
    )


class TestHealthEndpoint:
    def test_health_returns_healthy(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.get_json() == {"status": "healthy"}


class TestValidSignatures:
    def test_accepts_canonical_json_body(self, client):
        payload = {"event_id": "evt_001", "amount_cents": 2500}
        response = post_signed(client, payload)
        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "ok"
        assert body["event_id"] == "evt_001"

    def test_accepts_pretty_printed_json_body(self, client):
        """PayStream may send pretty-printed JSON; signature covers exact raw bytes."""
        payload = {"event_id": "evt_pretty", "amount_cents": 100}
        raw_body = json.dumps(payload, indent=2).encode("utf-8")
        signature = sign_raw_body(raw_body)

        response = client.post(
            "/webhooks/paystream",
            data=raw_body,
            headers={
                "Content-Type": "application/json",
                "X-PayStream-Signature": signature,
            },
        )
        assert response.status_code == 200

    def test_accepts_key_order_different_from_alphabetical(self, client):
        """Signature must use raw bytes, not a re-serialized dict with sorted keys."""
        raw_body = b'{"amount_cents":500,"event_id":"evt_order"}'
        signature = sign_raw_body(raw_body)

        response = client.post(
            "/webhooks/paystream",
            data=raw_body,
            headers={
                "Content-Type": "application/json",
                "X-PayStream-Signature": signature,
            },
        )
        assert response.status_code == 200
        assert response.get_json()["event_id"] == "evt_order"


class TestInvalidSignatures:
    def test_rejects_missing_signature_header(self, client):
        payload = {"event_id": "evt_no_sig", "amount_cents": 100}
        raw_body = json.dumps(payload).encode("utf-8")
        response = client.post(
            "/webhooks/paystream",
            data=raw_body,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 401

    def test_rejects_wrong_secret(self, client):
        payload = {"event_id": "evt_wrong_secret", "amount_cents": 100}
        response = post_signed(client, payload, secret="wrong-secret")
        assert response.status_code == 401

    def test_rejects_tampered_body(self, client):
        payload = {"event_id": "evt_tamper", "amount_cents": 100}
        response = post_signed(client, payload, tamper=True)
        assert response.status_code == 401

    def test_rejects_malformed_signature_header(self, client):
        payload = {"event_id": "evt_bad_header", "amount_cents": 100}
        raw_body = json.dumps(payload).encode("utf-8")
        response = client.post(
            "/webhooks/paystream",
            data=raw_body,
            headers={
                "Content-Type": "application/json",
                "X-PayStream-Signature": "not-a-valid-signature",
            },
        )
        assert response.status_code == 401

    def test_rejects_hardcoded_bypass_with_invalid_signature(self, client):
        """Agent must not accept requests when signature verification should fail."""
        payload = {"event_id": "evt_bypass", "amount_cents": 9999}
        raw_body = json.dumps(payload).encode("utf-8")
        response = client.post(
            "/webhooks/paystream",
            data=raw_body,
            headers={
                "Content-Type": "application/json",
                "X-PayStream-Signature": "sha256=" + "0" * 64,
            },
        )
        assert response.status_code == 401


class TestIdempotency:
    def test_duplicate_event_does_not_double_count(self, client, flask_app):
        payload = {"event_id": "evt_dup", "amount_cents": 300}
        first = post_signed(client, payload)
        second = post_signed(client, payload)

        assert first.status_code == 200
        assert second.status_code == 200

        store = flask_app.config["EVENT_STORE"]
        assert store.get_payment_total_cents() == 300


class TestPayloadValidation:
    def test_rejects_invalid_json(self, client):
        raw_body = b"{not-json"
        signature = sign_raw_body(raw_body)
        response = client.post(
            "/webhooks/paystream",
            data=raw_body,
            headers={
                "Content-Type": "application/json",
                "X-PayStream-Signature": signature,
            },
        )
        assert response.status_code == 400

    def test_rejects_missing_amount(self, client):
        payload = {"event_id": "evt_no_amount"}
        response = post_signed(client, payload)
        assert response.status_code == 400
