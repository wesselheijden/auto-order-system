# Auto Order System

An assistant tool for tree nurseries that extracts order data from WinTree screenshots and formats it into a Trello card. The workflow is:

1. Capture a screenshot of an order in WinTree.
2. Run the command-line tool on the screenshot.
3. Receive a Trello-ready title and description that can be pasted directly into Trello or sent through the API.

## Features

- OCR text extraction powered by [Tesseract](https://github.com/tesseract-ocr/tesseract) via `pytesseract`.
- Configurable parsing so you can adapt to different WinTree layouts.
- Trello card payload generation with clear bullet lists.
- Optional raw text output to debug OCR results.

## Installation

1. Install the system dependency [Tesseract OCR](https://tesseract-ocr.github.io/tessdoc/Installation.html).
2. Install the Python package (ideally in a virtual environment):

```bash
pip install -e .
```

This will install the `auto-order` command.

## Usage

```bash
auto-order path/to/screenshot.png
```

Options:

- `--lang`: Tesseract language codes (default: `eng+nld`).
- `--config`: Path to a YAML/JSON file overriding parser behaviour.
- `--text-input`: Parse plain text without running OCR (useful for testing).
- `--output`: Choose `markdown` (default) or `json` for the Trello payload.
- `--show-raw`: Print the raw OCR/text before parsing.

Example output:

```
Title: Green Garden BV — 120 plants

Description:

**Client:** Green Garden BV
**Delivery Date:** 2024-11-05
**Total Plants:** 120

**Order Details:**
- Acer rubrum — Size: 150-175 — Pot: C10 — Qty: 20 — Top quality
- Buxus sempervirens — Size: 30-40 — Pot: P9 — Qty: 100 — trimmed

**Notes:**
- Note: Deliver before noon
```

To obtain JSON suitable for the Trello API:

```bash
auto-order path/to/screenshot.png --output json
```

## Configuration

You can override how the parser recognises fields by creating a YAML or JSON file:

```yaml
client_pattern: "Clientnaam:\\s*(?P<value>.+)"
delivery_pattern: "Leverdatum:\\s*(?P<value>.+)"
item_header_keywords:
  - plant
  - maat
  - pot
  - aantal
item_field_order:
  - plant_name
  - plant_size
  - pot_size
  - quantity
  - extra_text
```

Then run:

```bash
auto-order screenshot.png --config custom_parser.yaml
```

> **Note**
> YAML support relies on the `pyyaml` dependency (installed with the package). If you prefer to skip it, a JSON file provides the same configuration options.

## Development

Run the unit tests with:

```bash
pytest
```

Pull requests and additional parsing strategies are welcome!
