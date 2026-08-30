"""Highlight.js theme registry for hotslice.

Provides a complete catalog of highlight.js themes with human-readable
display names and light/dark variant classification.
"""

from __future__ import annotations

# Special-case name mappings for non-obvious slug-to-name conversions.
_SPECIAL_NAMES: dict[str, str] = {
    "a11y-dark": "A11y Dark",
    "a11y-light": "A11y Light",
    "github": "GitHub",
    "github-dark": "GitHub Dark",
    "github-dark-dimmed": "GitHub Dark Dimmed",
    "vs": "Visual Studio",
    "vs2015": "Visual Studio 2015",
    "xt256": "XT256",
    "gml": "GML",
    "ir-black": "IR Black",
    "nnfx-dark": "NNFX Dark",
    "nnfx-light": "NNFX Light",
    "isbl-editor-dark": "ISBL Editor Dark",
    "isbl-editor-light": "ISBL Editor Light",
    "qtcreator-dark": "Qt Creator Dark",
    "qtcreator-light": "Qt Creator Light",
    "1c-light": "1C Light",
    "androidstudio": "Android Studio",
    "googlecode": "Google Code",
    "routeros": "RouterOS",
    "stackoverflow-dark": "Stack Overflow Dark",
    "stackoverflow-light": "Stack Overflow Light",
    "srcery": "Srcery",
    "purebasic": "PureBasic",
}


def slug_to_display_name(slug: str) -> str:
    """Convert a highlight.js theme slug to a human-readable display name."""
    if slug in _SPECIAL_NAMES:
        return _SPECIAL_NAMES[slug]
    # Default: replace hyphens with spaces and title-case
    return slug.replace("-", " ").replace("_", " ").title()


def _classify_base16(slug: str) -> str:
    """Classify a base16 theme as light or dark based on its slug."""
    if "-light" in slug:
        return "light"
    if "-dark" in slug:
        return "dark"
    # Ambiguous base16 themes default to dark
    return "dark"


# Complete registry of highlight.js themes.
# Each entry is (slug, display_name, variant) where variant is "light" or "dark".

_CORE_LIGHT_SLUGS: list[str] = [
    "1c-light",
    "a11y-light",
    "arduino-light",
    "ascetic",
    "atom-one-light",
    "brown-paper",
    "color-brewer",
    "default",
    "docco",
    "foundation",
    "github",
    "googlecode",
    "gradient-light",
    "grayscale",
    "idea",
    "intellij-light",
    "isbl-editor-light",
    "kimbie-light",
    "lightfair",
    "magula",
    "mono-blue",
    "nnfx-light",
    "panda-syntax-light",
    "paraiso-light",
    "purebasic",
    "qtcreator-light",
    "routeros",
    "school-book",
    "stackoverflow-light",
    "tokyo-night-light",
    "vs",
    "xcode",
    "cybertopia-icecap",
    "rose-pine-dawn",
]

_CORE_DARK_SLUGS: list[str] = [
    "a11y-dark",
    "agate",
    "an-old-hope",
    "androidstudio",
    "arta",
    "atom-one-dark",
    "atom-one-dark-reasonable",
    "codepen-embed",
    "cybertopia-cherry",
    "cybertopia-dimmer",
    "cybertopia-saturated",
    "dark",
    "devibeans",
    "far",
    "felipec",
    "github-dark",
    "github-dark-dimmed",
    "gml",
    "gradient-dark",
    "hybrid",
    "ir-black",
    "isbl-editor-dark",
    "kimbie-dark",
    "lioshi",
    "monokai",
    "monokai-sublime",
    "night-owl",
    "nnfx-dark",
    "nord",
    "obsidian",
    "panda-syntax-dark",
    "paraiso-dark",
    "pojoaque",
    "rainbow",
    "rose-pine",
    "rose-pine-moon",
    "shades-of-purple",
    "srcery",
    "stackoverflow-dark",
    "sunburst",
    "tokyo-night-dark",
    "tomorrow-night-blue",
    "tomorrow-night-bright",
    "vs2015",
    "xt256",
]

_BASE16_SLUGS: list[str] = [
    "base16-3024",
    "base16-apathy",
    "base16-apprentice",
    "base16-ashes",
    "base16-atelier-cave",
    "base16-atelier-cave-light",
    "base16-atelier-dune",
    "base16-atelier-dune-light",
    "base16-atelier-estuary",
    "base16-atelier-estuary-light",
    "base16-atelier-forest",
    "base16-atelier-forest-light",
    "base16-atelier-heath",
    "base16-atelier-heath-light",
    "base16-atelier-lakeside",
    "base16-atelier-lakeside-light",
    "base16-atelier-plateau",
    "base16-atelier-plateau-light",
    "base16-atelier-savanna",
    "base16-atelier-savanna-light",
    "base16-atelier-seaside",
    "base16-atelier-seaside-light",
    "base16-atelier-sulphurpool",
    "base16-atelier-sulphurpool-light",
    "base16-atlas",
    "base16-bespin",
    "base16-black-metal",
    "base16-black-metal-bathory",
    "base16-black-metal-burzum",
    "base16-black-metal-dark-funeral",
    "base16-black-metal-gorgoroth",
    "base16-black-metal-immortal",
    "base16-black-metal-khold",
    "base16-black-metal-marduk",
    "base16-black-metal-mayhem",
    "base16-black-metal-nile",
    "base16-black-metal-venom",
    "base16-brewer",
    "base16-bright",
    "base16-brogrammer",
    "base16-brush-trees",
    "base16-brush-trees-dark",
    "base16-chalk",
    "base16-circus",
    "base16-classic-dark",
    "base16-classic-light",
    "base16-codeschool",
    "base16-colors",
    "base16-cupcake",
    "base16-cupertino",
    "base16-danqing",
    "base16-darcula",
    "base16-dark-violet",
    "base16-darkmoss",
    "base16-darktooth",
    "base16-decaf",
    "base16-default-dark",
    "base16-default-light",
    "base16-dirtysea",
    "base16-dracula",
    "base16-edge-dark",
    "base16-edge-light",
    "base16-eighties",
    "base16-embers",
    "base16-equilibrium-dark",
    "base16-equilibrium-gray-dark",
    "base16-equilibrium-gray-light",
    "base16-equilibrium-light",
    "base16-espresso",
    "base16-eva",
    "base16-eva-dim",
    "base16-flat",
    "base16-framer",
    "base16-fruit-soda",
    "base16-gigavolt",
    "base16-github",
    "base16-google-dark",
    "base16-google-light",
    "base16-grayscale-dark",
    "base16-grayscale-light",
    "base16-green-screen",
    "base16-gruvbox-dark-hard",
    "base16-gruvbox-dark-medium",
    "base16-gruvbox-dark-pale",
    "base16-gruvbox-dark-soft",
    "base16-gruvbox-light-hard",
    "base16-gruvbox-light-medium",
    "base16-gruvbox-light-soft",
    "base16-hardcore",
    "base16-harmonic16-dark",
    "base16-harmonic16-light",
    "base16-heetch-dark",
    "base16-heetch-light",
    "base16-helios",
    "base16-hopscotch",
    "base16-horizon-dark",
    "base16-horizon-light",
    "base16-humanoid-dark",
    "base16-humanoid-light",
    "base16-ia-dark",
    "base16-ia-light",
    "base16-icy-dark",
    "base16-ir-black",
    "base16-isotope",
    "base16-kimber",
    "base16-london-tube",
    "base16-macintosh",
    "base16-marrakesh",
    "base16-materia",
    "base16-material",
    "base16-material-darker",
    "base16-material-lighter",
    "base16-material-palenight",
    "base16-material-vivid",
    "base16-mellow-purple",
    "base16-mexico-light",
    "base16-mocha",
    "base16-monokai",
    "base16-nebula",
    "base16-nord",
    "base16-nova",
    "base16-ocean",
    "base16-oceanicnext",
    "base16-one-light",
    "base16-onedark",
    "base16-outrun-dark",
    "base16-papercolor-dark",
    "base16-papercolor-light",
    "base16-paraiso",
    "base16-pasque",
    "base16-phd",
    "base16-pico",
    "base16-pop",
    "base16-porple",
    "base16-qualia",
    "base16-railscasts",
    "base16-rebecca",
    "base16-ros-pine",
    "base16-ros-pine-dawn",
    "base16-ros-pine-moon",
    "base16-sagelight",
    "base16-sandcastle",
    "base16-seti-ui",
    "base16-shapeshifter",
    "base16-silk-dark",
    "base16-silk-light",
    "base16-snazzy",
    "base16-solar-flare",
    "base16-solar-flare-light",
    "base16-solarized-dark",
    "base16-solarized-light",
    "base16-spacemacs",
    "base16-summercamp",
    "base16-summerfruit-dark",
    "base16-summerfruit-light",
    "base16-synth-midnight-terminal-dark",
    "base16-synth-midnight-terminal-light",
    "base16-tango",
    "base16-tender",
    "base16-tomorrow",
    "base16-tomorrow-night",
    "base16-twilight",
    "base16-unikitty-dark",
    "base16-unikitty-light",
    "base16-vulcan",
    "base16-windows-10",
    "base16-windows-10-light",
    "base16-windows-95",
    "base16-windows-95-light",
    "base16-windows-high-contrast",
    "base16-windows-high-contrast-light",
    "base16-windows-nt",
    "base16-windows-nt-light",
    "base16-woodland",
    "base16-xcode-dusk",
    "base16-zenburn",
]

# Build the unified theme list at module level.
HLJS_THEMES: list[tuple[str, str, str]] = []

for _slug in _CORE_LIGHT_SLUGS:
    HLJS_THEMES.append((_slug, slug_to_display_name(_slug), "light"))

for _slug in _CORE_DARK_SLUGS:
    HLJS_THEMES.append((_slug, slug_to_display_name(_slug), "dark"))

for _slug in _BASE16_SLUGS:
    HLJS_THEMES.append((_slug, slug_to_display_name(_slug), _classify_base16(_slug)))

# Index for fast slug lookups.
_SLUG_INDEX: dict[str, tuple[str, str, str]] = {t[0]: t for t in HLJS_THEMES}


def get_hljs_theme_info(slug: str) -> dict[str, str] | None:
    """Return theme info dict or None if the slug is not a known hljs theme.

    Returns ``{"slug": ..., "name": ..., "variant": ...}`` when found.
    """
    entry = _SLUG_INDEX.get(slug)
    if entry is None:
        return None
    return {"slug": entry[0], "name": entry[1], "variant": entry[2]}


def all_hljs_themes() -> list[dict[str, str]]:
    """Return all hljs themes as a list of info dicts."""
    return [{"slug": s, "name": n, "variant": v} for s, n, v in HLJS_THEMES]


def light_hljs_themes() -> list[dict[str, str]]:
    """Return only light-variant themes, sorted by display name."""
    return sorted(
        [{"slug": s, "name": n, "variant": v} for s, n, v in HLJS_THEMES if v == "light"],
        key=lambda t: t["name"],
    )


def dark_hljs_themes() -> list[dict[str, str]]:
    """Return only dark-variant themes, sorted by display name."""
    return sorted(
        [{"slug": s, "name": n, "variant": v} for s, n, v in HLJS_THEMES if v == "dark"],
        key=lambda t: t["name"],
    )
