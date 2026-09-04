import os


def get_webhook_secret() -> str:
    secret = os.environ.get("WEBHOOK_SECRET", "")
    if not secret:
        raise RuntimeError("WEBHOOK_SECRET environment variable is required")
    return secret
