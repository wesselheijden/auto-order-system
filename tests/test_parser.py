import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from auto_order_system.models import OrderItem
from auto_order_system.parser import ParserConfig, parse_order_text


SAMPLE_TEXT = """
Client: Green Garden BV
Delivery Date: 2024-11-05

Plant | Size | Pot | Qty | Extra
Acer rubrum | 150-175 | C10 | 20 | Top quality
Buxus sempervirens | 30-40 | P9 | 100 | trimmed
Note: Deliver before noon
Total items: 120
""".strip()


def test_parse_order_text_extracts_fields():
    order = parse_order_text(SAMPLE_TEXT)
    assert order.client_name == "Green Garden BV"
    assert order.delivery_date == "2024-11-05"
    assert order.total_quantity == 120
    assert len(order.items) == 2
    first_item = order.items[0]
    assert isinstance(first_item, OrderItem)
    assert first_item.plant_name == "Acer rubrum"
    assert first_item.quantity == 20
    assert order.notes == ["Note: Deliver before noon"]


def test_custom_config_changes_patterns(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "client_pattern": r"Clientnaam:\s*(?P<value>.+)",
                "delivery_pattern": r"Leverdatum:\s*(?P<value>.+)",
                "item_header_keywords": ["plant", "maat", "pot", "aantal"],
            }
        )
    )

    text = """
Clientnaam: BoomExpert
Leverdatum: 2024-12-12
Plant | maat | pot | aantal
Tilia cordata | 200-250 | C12 | 15
"""
    order = parse_order_text(text, ParserConfig.from_file(config_file))
    assert order.client_name == "BoomExpert"
    assert order.delivery_date == "2024-12-12"
    assert order.items[0].quantity == 15
