"""In-memory store for processed webhook events."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock


@dataclass
class EventStore:
    processed_event_ids: set[str] = field(default_factory=set)
    payment_total_cents: int = 0
    _lock: Lock = field(default_factory=Lock)

    def record_payment(self, event_id: str, amount_cents: int) -> bool:
        """Record a payment event. Returns True if newly processed, False if duplicate."""
        with self._lock:
            if event_id in self.processed_event_ids:
                return False
            self.processed_event_ids.add(event_id)
            self.payment_total_cents += amount_cents
            return True

    def get_payment_total_cents(self) -> int:
        with self._lock:
            return self.payment_total_cents


# Module-level singleton used by the application
event_store = EventStore()
