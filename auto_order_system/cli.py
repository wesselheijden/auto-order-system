"""Command line interface for the Auto Order System."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click

from .ocr import OCRFailure, extract_text_from_image
from .parser import ParserConfig, parse_order_text
from .trello import build_trello_card_payload


@click.command()
@click.argument("image_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Optional YAML/JSON configuration overriding parser behaviour.",
)
@click.option(
    "--lang",
    default="eng+nld",
    show_default=True,
    help="Tesseract language codes to use for OCR (e.g. 'eng+nld').",
)
@click.option(
    "--output",
    type=click.Choice(["markdown", "json"], case_sensitive=False),
    default="markdown",
    show_default=True,
    help="Output format for the Trello card.",
)
@click.option(
    "--text-input",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Skip OCR and parse plain text from the provided file.",
)
@click.option("--show-raw", is_flag=True, help="Print the raw OCR/text before parsing.")
def main(
    image_path: Path,
    config_path: Optional[Path],
    lang: str,
    output: str,
    text_input: Optional[Path],
    show_raw: bool,
) -> None:
    """Extract order data from a WinTree screenshot and output Trello data."""

    if text_input:
        raw_text = text_input.read_text(encoding="utf-8")
    else:
        try:
            raw_text = extract_text_from_image(image_path, lang=lang)
        except OCRFailure as exc:
            raise click.ClickException(str(exc)) from exc

    if show_raw:
        click.echo("--- RAW TEXT START ---")
        click.echo(raw_text)
        click.echo("--- RAW TEXT END ---")

    if config_path:
        config = ParserConfig.from_file(str(config_path))
    else:
        config = ParserConfig()

    order = parse_order_text(raw_text, config)
    trello_payload = build_trello_card_payload(order)

    if output.lower() == "json":
        click.echo(json.dumps(trello_payload, indent=2, ensure_ascii=False))
    else:
        click.echo(f"Title: {trello_payload['name']}")
        click.echo("\nDescription:\n")
        click.echo(trello_payload["desc"])


if __name__ == "__main__":  # pragma: no cover
    main()
