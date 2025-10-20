"""Trello formatting helpers."""
from __future__ import annotations

from typing import Dict

from .models import Order


def build_trello_card_payload(order: Order) -> Dict[str, str]:
    """Create a Trello-ready payload from an :class:`Order`."""

    title = f"{order.client_name} — {order.total_quantity} plants"
    details_lines = [f"- {item.summary()}" for item in order.items]
    if not details_lines:
        details_lines.append("- No items detected")

    description_parts = [
        f"**Client:** {order.client_name}",
    ]
    if order.delivery_date:
        description_parts.append(f"**Delivery Date:** {order.delivery_date}")
    description_parts.append(f"**Total Plants:** {order.total_quantity}")
    description_parts.append("\n**Order Details:**")
    description_parts.extend(details_lines)

    if order.notes:
        description_parts.append("\n**Notes:**")
        description_parts.extend(f"- {note}" for note in order.notes)

    description = "\n".join(description_parts)

    payload: Dict[str, str] = {
        "name": title,
        "desc": description,
    }

    # Trello expects ISO date strings. We leave due unset if parsing is uncertain.
    return payload
