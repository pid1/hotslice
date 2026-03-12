"""Configuration loading and merging for hotslice."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

USER_CONFIG_DIR = Path.home() / ".config" / "hotslice"


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
    def _apply_toml(cfg: Config, path: Path) -> None:
        """Apply values from a TOML config file onto an existing Config."""
        if not path.is_file():
            return
        with open(path, "rb") as f:
            data = tomllib.load(f)

        defaults = data.get("defaults", {})
        for key in ("theme", "output", "separator"):
            if key in defaults:
                setattr(cfg, key, defaults[key])

        meta = data.get("metadata", {})
        if meta:
            cfg.metadata = Metadata(
                author=meta.get("author", cfg.metadata.author),
                date=meta.get("date", cfg.metadata.date),
            )

    @staticmethod
    def load(config_path: Path | None = None) -> Config:
        """Load config, layering user-level and project-level files.

        Priority (highest wins):
        project hotslice.toml > user ~/.config/hotslice/hotslice.toml > defaults.
        When config_path is explicitly provided, only that file is used.
        """
        cfg = Config()

        if config_path is not None:
            Config._apply_toml(cfg, config_path)
        else:
            # Layer 1: user config (lower priority)
            Config._apply_toml(cfg, USER_CONFIG_DIR / "hotslice.toml")
            # Layer 2: project config (higher priority, overrides user)
            Config._apply_toml(cfg, Path.cwd() / "hotslice.toml")

        return cfg

    def merge_cli(self, **kwargs: object) -> None:
        """Override config values with non-None CLI arguments."""
        for key, value in kwargs.items():
            if value is not None and hasattr(self, key):
                setattr(self, key, value)
