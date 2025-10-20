"""Domain models for WinTree order extraction."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional


@dataclass(slots=True)
class OrderItem:
    """Represents a single line item in a WinTree order."""

    plant_name: str
    plant_size: Optional[str] = None
    pot_size: Optional[str] = None
    quantity: int = 0
    extra_text: Optional[str] = None

    def summary(self) -> str:
        """Return a human-friendly description for Trello bullet lists."""
        parts: List[str] = [self.plant_name]
        if self.plant_size:
            parts.append(f"Size: {self.plant_size}")
        if self.pot_size:
            parts.append(f"Pot: {self.pot_size}")
        parts.append(f"Qty: {self.quantity}")
        if self.extra_text:
            parts.append(self.extra_text)
        return " — ".join(parts)


@dataclass(slots=True)
class Order:
    """Represents a structured order extracted from OCR text."""

    client_name: str
    delivery_date: Optional[str] = None
    items: List[OrderItem] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def total_quantity(self) -> int:
        return sum(item.quantity for item in self.items)

    def extend_notes(self, notes: Iterable[str]) -> None:
        for note in notes:
            clean = note.strip()
            if clean:
                self.notes.append(clean)
