"""CLI interface for hotslice."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from hotslice import __version__
from hotslice.config import Config
from hotslice.parser import parse_deck
from hotslice.renderer import render_deck, write_deck


def _serve(args: argparse.Namespace) -> None:
    """Start the hotslice web server."""
    from hotslice.web import main as web_main

    web_main(host=args.host, port=args.port)


def _build(args: argparse.Namespace) -> None:
    """Execute the build command."""
    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Load config and merge CLI overrides
    config = Config.load()
    config.merge_cli(
        theme=args.theme,
        output=args.output,
        title=args.title,
        separator=args.separator,
        theme_dir=args.theme_dir,
    )

    # Default output: <input_stem>.html in current directory
    if config.output is None:
        config.output = input_path.stem + ".html"

    # Read and parse markdown
    markdown_text = input_path.read_text(encoding="utf-8")
    deck = parse_deck(markdown_text, separator=config.separator)

    # Apply frontmatter overrides
    if "theme" in deck.frontmatter:
        config.theme = deck.frontmatter["theme"]
    if "title" in deck.frontmatter and not args.title:
        config.title = deck.frontmatter["title"]

    # Render and write
    html = render_deck(deck, config)
    out = write_deck(html, config.output)
    print(f"✓ Built {len(deck.slides)} slides → {out}")


def main(argv: list[str] | None = None) -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="hotslice",
        description="🍕 A hot take, one slice at a time. Markdown → HTML slide decks.",
    )
    parser.add_argument(
        "--version", action="version", version=f"hotslice {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # build subcommand
    build_parser = subparsers.add_parser(
        "build", help="Build an HTML slide deck from markdown"
    )
    build_parser.add_argument("input", help="Path to the input markdown file")
    build_parser.add_argument("-o", "--output", help="Output HTML file path")
    build_parser.add_argument("--theme", help="Theme name or path")
    build_parser.add_argument("--theme-dir", help="Base directory to search for themes")
    build_parser.add_argument("--title", help="Presentation title override")
    build_parser.add_argument(
        "--separator", help="Slide separator regex (default: ^---$)"
    )
    build_parser.set_defaults(func=_build)

    # serve subcommand
    serve_parser = subparsers.add_parser("serve", help="Start the hotslice web server")
    serve_parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
    )
    serve_parser.add_argument(
        "--port", type=int, default=8000, help="Port to listen on (default: 8000)"
    )
    serve_parser.set_defaults(func=_serve)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
