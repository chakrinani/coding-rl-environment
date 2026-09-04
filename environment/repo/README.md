# PayStream Webhook Receiver

Minimal Flask service for receiving signed payment webhooks.

```bash
export WEBHOOK_SECRET=dev-secret-key
pip install -r requirements.txt
python -m flask --app app.main run --port 5000
```

Endpoints:

- `GET /health` — health check
- `POST /webhooks/paystream` — payment webhook receiver
