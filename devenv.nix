{ pkgs, lib, config, inputs, ... }:

let
  setupCommands = [
    "install-deps"
  ];
in
{
  packages = with pkgs; [
    uv
    ruff
    git
  ];

  languages.python = {
    enable = true;
    package = pkgs.python314;
    uv.enable = true;
  };

  scripts = {
    setup.exec = lib.concatStringsSep " && " setupCommands;
    install-deps.exec = "uv sync";

    dev.exec = "uv run hotslice build examples/demo.md && open demo.html";

    dev-start.exec = ''
      mkdir -p .devenv/logs .devenv/pids
      nohup uv run hotslice build examples/demo.md > .devenv/logs/dev.log 2>&1 &
      echo $! > .devenv/pids/dev.pid
      echo "✓ Built presentation"
      open demo.html
    '';
    dev-stop.exec = "echo 'hotslice is a build tool, no long-running process to stop'";
    dev-status.exec = "echo 'hotslice is a build tool -- check PWD for output'";
    dev-logs.exec = "tail -50 .devenv/logs/dev.log 2>/dev/null || echo 'No dev logs found'";

    lint.exec = "ruff check .";
    lint-fix.exec = "ruff check . --fix";
    format.exec = "ruff format .";
    test.exec = "uv run pytest";

    build.exec = "uv run hotslice build examples/demo.md";
  };

  enterShell = ''
    echo "🍕 hotslice Development Environment"
    echo ""
    echo "Python: $(python --version)"
    echo "uv: $(uv --version)"
    echo ""
    echo "Setup:"
    echo "  setup            - Initialize repo (runs: ${lib.concatStringsSep ", " setupCommands})"
    echo ""
    echo "Commands:"
    echo "  dev              - Build demo deck and open in browser"
    echo "  build            - Build demo deck to demo.html"
    echo ""
    echo "Quality commands:"
    echo "  lint             - Run ruff linter"
    echo "  lint-fix         - Run ruff with auto-fix"
    echo "  format           - Run ruff formatter"
    echo "  test             - Run pytest"
    echo ""
    echo "Other commands:"
    echo "  install-deps     - Install dependencies with uv"
    echo ""
  '';
}
