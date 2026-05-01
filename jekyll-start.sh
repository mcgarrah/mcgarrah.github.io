#!/bin/bash
# Start Jekyll development server for mcgarrah.github.io
#
# Usage:
#   ./jekyll-start.sh          # Start with default flags (drafts, future, livereload, incremental)
#   ./jekyll-start.sh --clean  # Hard clean cache before starting (fixes macOS FSEvents staleness)
#
# Default flags: --trace --drafts --future --unpublished --livereload --incremental
# Port: 4000 (Jekyll default)
#
# Prerequisites:
#   - Ruby 3.3+ via rbenv (see .ruby-version)
#   - bundle install completed
#   - On macOS: launch VS Code from terminal, not Dock/Spotlight
#
# =============================================================================
# Setting up on macOS (Homebrew + rbenv)
# =============================================================================
#
# macOS ships system Ruby 2.6 which is too old for Jekyll 4.4.1.
# Homebrew Ruby 4.0 works but breaks --livereload.
# Use rbenv with Ruby 3.3 for full compatibility.
#
# 1. Install rbenv:
#      brew install rbenv ruby-build
#
# 2. Install Ruby 3.3 (version pinned in .ruby-version):
#      rbenv install 3.3.11
#
# 3. Add to ~/.zshrc (before 'source $ZSH/oh-my-zsh.sh'):
#      if [[ "$(uname -s)" == "Darwin" ]]; then
#        eval "$(rbenv init - zsh)"
#      fi
#
# 4. Create ~/.zshenv (for VS Code extensions / non-interactive shells):
#      if [[ "$(uname -s)" == "Darwin" && -d "$HOME/.rbenv" ]]; then
#        export PATH="$HOME/.rbenv/shims:$HOME/.rbenv/bin:$PATH"
#      fi
#
# 5. Reload shell and install gems:
#      source ~/.zshrc
#      ruby --version          # should show 3.3.x
#      gem install bundler
#      bundle install
#
# 6. IMPORTANT: On macOS, always launch VS Code from a terminal:
#      code ~/github/articles-workspace.code-workspace
#    macOS GUI apps (Dock/Spotlight) don't inherit your shell PATH,
#    so the Jekyll Run plugin would use system Ruby 2.6 and crash.
#
# =============================================================================
# Setting up on Ubuntu 22.04 LTS / 24.04 LTS (WSL2 / Linux)
# =============================================================================
#
# sudo apt -y install make build-essential ruby ruby-dev
#
# Update ~/.bashrc and ~/.zshrc with this:
#
# # Ruby Jekyll Gems
# if [ ! -d $HOME/.gems ]; then
#   mkdir $HOME/.gems
# fi
# export GEM_HOME=$HOME/.gems
# export PATH=$HOME/.gems/bin:$PATH
#
# gem install jekyll bundler
# bundle install
#
# =============================================================================
# VS Code Extension (fallback when this script is needed)
# =============================================================================
#
# Name: Jekyll Run (fork: Run Jekyll)
# Id: Dedsec727.jekyll-run
# VS Marketplace Link: https://marketplace.visualstudio.com/items?itemName=Dedsec727.jekyll-run
#
# File -> Preferences -> Settings (Ctrl+,)
#  Scroll to "Jekyll Run - Configuration"
#  Or set in .vscode/settings.json per workspace
#
# =============================================================================
# Jekyll serve flags:
#   --trace         Show full Ruby backtrace on errors
#   --drafts        Render posts in the _drafts/ folder
#   --future        Publish posts with a future date
#   --unpublished   Render posts with published: false in front matter
#   --livereload    Auto-refresh browser on file save
#   --incremental   Only rebuild changed pages (faster, but restart
#                   if edits to _includes/ or _layouts/ seem stale)
# =============================================================================

set -e

PORT=4000
CLEAN=false

for arg in "$@"; do
    case "$arg" in
        --clean)
            CLEAN=true
            ;;
        --help)
            echo "Usage: $0 [--clean] [--help]"
            echo "  --clean  Hard clean (.jekyll-cache, _site/, .jekyll-metadata) before starting"
            echo "  --help   Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Usage: $0 [--clean] [--help]"
            exit 1
            ;;
    esac
done

# Check if port is already in use
check_port() {
    local pid=""
    local process=""

    if command -v lsof &>/dev/null; then
        # macOS and most Linux
        pid=$(lsof -i :"$PORT" -sTCP:LISTEN -P -n -t 2>/dev/null | head -1)
        if [ -n "$pid" ]; then
            process=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
        fi
    elif command -v ss &>/dev/null; then
        # Linux without lsof (some minimal WSL2 installs)
        pid=$(ss -tlnp "sport = :$PORT" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1)
        if [ -n "$pid" ]; then
            process=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
        fi
    fi

    if [ -n "$pid" ]; then
        echo "ERROR: Port $PORT is already in use by $process (PID $pid)"
        echo ""
        echo "Options:"
        echo "  kill $pid              # Stop the existing process"
        echo "  kill -9 $pid           # Force stop if it won't die"
        echo "  ./jekyll-clean.sh      # If it's a stale Jekyll, clean and retry"
        exit 1
    fi
}

check_port

# Optional hard clean before starting
if [ "$CLEAN" = true ]; then
    echo "Hard cleaning before start..."
    bundle exec jekyll clean
    [ -d ".jekyll-cache" ] && rm -rf .jekyll-cache && echo "Removed .jekyll-cache"
    [ -f ".jekyll-metadata" ] && rm -f .jekyll-metadata && echo "Removed .jekyll-metadata"
    [ -d "_site" ] && rm -rf _site && echo "Removed _site/"
    echo ""
fi

echo "Starting Jekyll on port $PORT..."
echo ""
bundle exec jekyll serve --trace --drafts --future --unpublished --livereload --incremental
