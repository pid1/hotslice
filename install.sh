#!/usr/bin/env bash
set -euo pipefail

# hotslice installer
# Usage: curl -fsSL https://raw.githubusercontent.com/pid1/hotslice/main/install.sh | bash

REPO="git+https://github.com/pid1/hotslice"
CONFIG_DIR="$HOME/.config/hotslice"
CONFIG_FILE="$CONFIG_DIR/hotslice.toml"
THEMES_DIR="$CONFIG_DIR/themes"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

info() {
    printf '\033[1;34m[info]\033[0m %s\n' "$*"
}

warn() {
    printf '\033[1;33m[warn]\033[0m %s\n' "$*"
}

error() {
    printf '\033[1;31m[error]\033[0m %s\n' "$*" >&2
    exit 1
}

success() {
    printf '\033[1;32m[ok]\033[0m %s\n' "$*"
}

# ---------------------------------------------------------------------------
# OS detection
# ---------------------------------------------------------------------------

detect_os() {
    local os
    os="$(uname -s)"
    case "$os" in
        Darwin) info "Detected macOS" ;;
        Linux)  info "Detected Linux" ;;
        *)      error "Unsupported operating system: $os. Only macOS and Linux are supported." ;;
    esac
}

# ---------------------------------------------------------------------------
# uv installation
# ---------------------------------------------------------------------------

ensure_uv() {
    if command -v uv >/dev/null 2>&1; then
        info "uv is already installed ($(uv --version))"
        return
    fi

    info "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Make uv available in the current session
    if [ -f "$HOME/.local/bin/env" ]; then
        # shellcheck source=/dev/null
        . "$HOME/.local/bin/env"
    else
        export PATH="$HOME/.local/bin:$PATH"
    fi

    if ! command -v uv >/dev/null 2>&1; then
        error "Failed to install uv. Please install it manually: https://docs.astral.sh/uv/"
    fi
    success "uv installed successfully"
}

# ---------------------------------------------------------------------------
# hotslice installation
# ---------------------------------------------------------------------------

install_hotslice() {
    info "Installing hotslice via uv..."
    uv tool install "$REPO"
    success "hotslice installed"
}

# ---------------------------------------------------------------------------
# Config setup
# ---------------------------------------------------------------------------

setup_config() {
    info "Setting up user config directory..."
    mkdir -p "$THEMES_DIR"

    if [ -f "$CONFIG_FILE" ]; then
        info "Config file already exists at $CONFIG_FILE, skipping"
    else
        cat > "$CONFIG_FILE" << 'TOML'
[defaults]
theme = "light"
output = "dist/index.html"
separator = "^---$"

[metadata]
author = ""
date = ""
TOML
        success "Created config file at $CONFIG_FILE"
    fi
}

# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

verify_install() {
    if command -v hotslice >/dev/null 2>&1; then
        success "hotslice $(hotslice --version) is ready"
    else
        warn "hotslice was installed but is not on your PATH."
        warn "Add ~/.local/bin to your PATH:"
        warn ""
        warn "  For bash: echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc && source ~/.bashrc"
        warn "  For zsh:  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc && source ~/.zshrc"
    fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

main() {
    printf '\n\033[1m  hotslice installer\033[0m\n\n'

    detect_os
    ensure_uv
    install_hotslice
    setup_config
    verify_install

    printf '\n\033[1m  Installation complete!\033[0m\n\n'
    info "Binary:       ~/.local/bin/hotslice"
    info "Config:       $CONFIG_FILE"
    info "User themes:  $THEMES_DIR"
    printf '\n'
    info "Quick start:"
    info "  hotslice build slides.md"
    printf '\n'
}

main
