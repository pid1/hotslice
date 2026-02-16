"""Configuration loading and merging for hotslice."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Metadata:
    author: str = ""
    date: str = ""


@dataclass
class Config:
    theme: str = "light"
    output: str = "dist/index.html"
    separator: str = "^---$"
    theme_dir: str | None = None
    title: str | None = None
    metadata: Metadata = field(default_factory=Metadata)

    @staticmethod
    def load(config_path: Path | None = None) -> Config:
        """Load config from hotslice.toml if it exists."""
        if config_path is None:
            config_path = Path.cwd() / "hotslice.toml"

        cfg = Config()

        if config_path.is_file():
            with open(config_path, "rb") as f:
                data = tomllib.load(f)

            defaults = data.get("defaults", {})
            for key in ("theme", "output", "separator"):
                if key in defaults:
                    setattr(cfg, key, defaults[key])

            meta = data.get("metadata", {})
            cfg.metadata = Metadata(
                author=meta.get("author", ""),
                date=meta.get("date", ""),
            )

        return cfg

    def merge_cli(self, **kwargs: object) -> None:
        """Override config values with non-None CLI arguments."""
        for key, value in kwargs.items():
            if value is not None and hasattr(self, key):
                setattr(self, key, value)
