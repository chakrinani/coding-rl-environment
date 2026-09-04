# Task: Fix the payment webhook receiver

You are working on a small Flask service that receives payment webhooks from an external provider called **PayStream**.

The service is deployed and the health check works, but **every legitimate webhook from PayStream is being rejected with HTTP 401**. The operations team confirmed:

- PayStream signs the **raw HTTP request body** using HMAC-SHA256
- The signature is sent in the `X-PayStream-Signature` header as `sha256=<hex_digest>`
- The shared secret is configured via the `WEBHOOK_SECRET` environment variable
- PayStream's own retry dashboard shows our endpoint returning 401 for valid events

Your job is to **fix the webhook signature verification** so that:

1. **Valid signed events are accepted** and return HTTP 200 with a JSON body containing `status: "ok"` and the processed `event_id`.
2. **Invalid, missing, or tampered signatures are rejected** with HTTP 401.
3. **Idempotent processing is preserved**: submitting the same `event_id` twice must not double-count the payment total. The second request should still return 200 but must not increase the stored total again.
4. The existing **`GET /health`** endpoint must keep working and return `{"status": "healthy"}`.

## What you have

The codebase lives under `app/`:

- `main.py` — Flask application factory and route registration
- `webhooks.py` — webhook endpoint handler
- `signature.py` — signature verification helpers
- `store.py` — in-memory event store and payment total tracking
- `config.py` — configuration from environment variables

## Constraints

- Do **not** remove signature verification or disable it behind a feature flag.
- Do **not** modify the test suite (there isn't one in the repo — verification happens externally).
- You may modify any files in the repository as needed.
- Keep using the standard library `hmac` and `hashlib` modules for cryptography.

## How success is measured

An external verifier will send HTTP requests to your application with correctly and incorrectly signed payloads, including edge cases (tampered bodies, duplicate events, missing headers). All behavioral requirements above must pass.

## Getting started

```bash
pip install -r requirements.txt
export WEBHOOK_SECRET=dev-secret-key
python -m flask --app app.main run --port 5000
```

Or use Docker (see project README).

Good luck.
