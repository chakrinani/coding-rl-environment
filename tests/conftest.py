"""Pytest fixtures for grading the webhook receiver."""

from __future__ import annotations

import hashlib
import hmac
import importlib
import os
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO = PROJECT_ROOT / "environment" / "repo"
TEST_SECRET = "test-webhook-secret-for-grader"


def sign_raw_body(raw_body: bytes, secret: str = TEST_SECRET) -> str:
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


@pytest.fixture(autouse=True)
def webhook_secret(monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.setenv("WEBHOOK_SECRET", TEST_SECRET)
    return TEST_SECRET


@pytest.fixture()
def repo_root() -> Path:
    return Path(os.environ.get("GRADER_REPO_ROOT", DEFAULT_REPO)).resolve()


@pytest.fixture()
def flask_app(repo_root: Path, webhook_secret: str):
    repo_str = str(repo_root)
    if repo_str not in sys.path:
        sys.path.insert(0, repo_str)

    for module_name in [
        "app",
        "app.config",
        "app.store",
        "app.signature",
        "app.webhooks",
        "app.main",
    ]:
        if module_name in sys.modules:
            del sys.modules[module_name]

    main = importlib.import_module("app.main")
    store_module = importlib.import_module("app.store")
    fresh_store = store_module.EventStore()
    app = main.create_app(store=fresh_store)
    app.config["TESTING"] = True
    return app


@pytest.fixture()
def client(flask_app):
    return flask_app.test_client()
