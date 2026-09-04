"""Flask application entrypoint."""

from __future__ import annotations

from flask import Flask, jsonify

from app.store import EventStore, event_store
from app.webhooks import webhooks_bp


def create_app(store: EventStore | None = None) -> Flask:
    app = Flask(__name__)

    if store is not None:
        app.config["EVENT_STORE"] = store
    else:
        app.config["EVENT_STORE"] = event_store

    @app.get("/health")
    def health():
        return jsonify({"status": "healthy"}), 200

    app.register_blueprint(webhooks_bp)
    return app


app = create_app()
