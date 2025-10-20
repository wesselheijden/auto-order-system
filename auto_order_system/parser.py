"""OCR parsing utilities for WinTree screenshots."""
from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import List, Optional, Sequence

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    yaml = None  # type: ignore[assignment]

from .models import Order, OrderItem


@dataclass
class ParserConfig:
    """Configuration driving how structured data is extracted from OCR text."""

    client_pattern: str = r"Client(?: Name)?:\s*(?P<value>.+)"
    delivery_pattern: str = r"Delivery(?: Date)?:\s*(?P<value>.+)"
    item_header_keywords: Sequence[str] = ("plant", "size", "pot", "qty")
    item_field_order: Sequence[str] = (
        "plant_name",
        "plant_size",
        "pot_size",
        "quantity",
        "extra_text",
    )
    item_delimiters: Sequence[str] = ("|", ";", ",")
    quantity_patterns: Sequence[str] = (r"(?P<quantity>\d+)",)
    notes_prefixes: Sequence[str] = ("note", "remark", "opmerking")
    stop_markers: Sequence[str] = ("total", "totaal", "subtotal")

    def __post_init__(self) -> None:
        self._client_regex = re.compile(self.client_pattern, re.IGNORECASE)
        self._delivery_regex = re.compile(self.delivery_pattern, re.IGNORECASE)
        self._quantity_regexes = [re.compile(pattern, re.IGNORECASE) for pattern in self.quantity_patterns]

    @classmethod
    def from_file(cls, path: "os.PathLike[str] | str") -> "ParserConfig":
        from pathlib import Path

        config_path = Path(path)
        with config_path.open("r", encoding="utf-8") as handle:
            if config_path.suffix.lower() in {".yaml", ".yml"}:
                if yaml is None:
                    raise RuntimeError(
                        "PyYAML is required to load YAML configuration files. Install 'pyyaml' or use JSON."
                    )
                data = yaml.safe_load(handle)
            else:
                data = json.load(handle)
        if data is None:
            data = {}
        return cls(**data)

    def find_client_name(self, text: str) -> Optional[str]:
        match = self._client_regex.search(text)
        if match:
            return match.group("value").strip()
        return None

    def find_delivery_date(self, text: str) -> Optional[str]:
        match = self._delivery_regex.search(text)
        if match:
            return match.group("value").strip()
        return None

    def looks_like_note(self, line: str) -> bool:
        lowered = line.lower()
        return any(lowered.startswith(prefix) for prefix in self.notes_prefixes)

    def is_stop_marker(self, line: str) -> bool:
        lowered = line.lower()
        return any(marker in lowered for marker in self.stop_markers)


def normalise_lines(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def locate_items_header(lines: Sequence[str], keywords: Sequence[str]) -> Optional[int]:
    for idx, line in enumerate(lines):
        lowered = line.lower()
        if all(keyword in lowered for keyword in keywords):
            return idx
    return None


def split_item_line(line: str, delimiters: Sequence[str]) -> List[str]:
    for delimiter in delimiters:
        if delimiter in line:
            return [part.strip() for part in line.split(delimiter)]
    # fall back to large whitespace gaps
    return re.split(r"\s{2,}", line.strip())


def coerce_quantity(value: str, quantity_regexes: Sequence[re.Pattern[str]]) -> int:
    value = value.strip()
    for regex in quantity_regexes:
        match = regex.search(value)
        if match and match.group("quantity"):
            return int(match.group("quantity"))
    try:
        return int(value)
    except ValueError:
        return 0


def parse_items(lines: Sequence[str], start_index: int, config: ParserConfig) -> List[OrderItem]:
    items: List[OrderItem] = []
    for line in lines[start_index + 1 :]:
        if not line:
            continue
        if config.is_stop_marker(line):
            break
        fields = split_item_line(line, config.item_delimiters)
        if len(fields) < 2:
            continue
        mapped: dict[str, Optional[str]] = {}
        for idx, field_name in enumerate(config.item_field_order):
            if idx < len(fields):
                mapped[field_name] = fields[idx].strip()
            else:
                mapped[field_name] = None
        quantity_raw = mapped.get("quantity") or "0"
        quantity = coerce_quantity(quantity_raw, config._quantity_regexes)
        item = OrderItem(
            plant_name=mapped.get("plant_name") or "Unknown plant",
            plant_size=mapped.get("plant_size") or None,
            pot_size=mapped.get("pot_size") or None,
            quantity=quantity,
            extra_text=mapped.get("extra_text") or None,
        )
        items.append(item)
    return items


def parse_order_text(text: str, config: Optional[ParserConfig] = None) -> Order:
    """Convert OCR text into a structured :class:`Order`."""

    config = config or ParserConfig()
    lines = normalise_lines(text)
    client_name = config.find_client_name(text) or "Unknown client"
    delivery_date = config.find_delivery_date(text)

    notes: List[str] = []
    for line in lines:
        if config.looks_like_note(line):
            notes.append(line)

    header_index = locate_items_header(lines, config.item_header_keywords)
    items: List[OrderItem]
    if header_index is not None:
        items = parse_items(lines, header_index, config)
    else:
        items = []

    order = Order(client_name=client_name, delivery_date=delivery_date, items=items)
    order.extend_notes(notes)
    return order
