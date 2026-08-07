#!/bin/bash
# =============================================================================
# jekyll-caddy.sh — Integrated local development for blog + resume
# =============================================================================
#
# Starts both Jekyll sites and a Caddy reverse proxy to replicate the
# production URL structure (blog at webroot, resume at /resume/) under
# a single local port.
#
# Usage:
#   ./jekyll-caddy.sh          # Start all three services
#   ./jekyll-caddy.sh --help   # Show this help
#
# Architecture:
#   ┌─────────────────────────────────────────────────────────┐
#   │  http://localhost:8080  (Caddy reverse proxy)           │
#   │                                                         │
#   │  /          → localhost:4001  (Blog - Jekyll)           │
#   │  /resume/*  → localhost:4002  (Resume - Jekyll)         │
#   └─────────────────────────────────────────────────────────┘
#
# This solves the cross-site linking problem: navigation links between
# the blog and resume use absolute paths (/resume/, /resume/print/).
# In production, GitHub Pages merges both repos under one domain.
# Locally, each site runs its own Jekyll server on a separate port —
# breaking every cross-site link. Caddy routes by path prefix so both
# sites are reachable at the same origin, matching production behavior.
#
# Note on handle vs handle_path:
#   The resume server is configured with baseurl: "/resume" — it expects
#   requests to arrive WITH the /resume prefix. We use Caddy's `handle`
#   (not `handle_path`) so the prefix is preserved. Using handle_path
#   would strip /resume and the resume server would 404.
#
# Prerequisites:
#   - caddy (brew install caddy / apt install caddy)
#   - Ruby 3.3+ via rbenv with bundle install in both repos
#   - This script must be run from the blog repo root (mcgarrah.github.io)
#   - Resume repo expected at ../resume (sibling directory)
#   - Both sites must be pre-built (bundle exec jekyll build)
#
# After prerequisites pass, runs jekyll-checks.sh against the blog repo:
# jekyll doctor, front matter lint (_posts/, same as CI), a tag-slug
# collision check across _posts/+_drafts/ (CI only checks _posts/), and
# missing-OG-image detection. Informational only — doesn't block startup.
#
# Ports:
#   4001 — Blog (Jekyll serve — avoids 4000 used by jekyll-start.sh)
#   4002 — Resume (Jekyll serve)
#   8080 — Caddy proxy (the URL you browse)
#   35729 — Blog livereload WebSocket
#   35730 — Resume livereload WebSocket
#
# =============================================================================

BLOG_PORT=4001
RESUME_PORT=4002
CADDY_PORT=8080
RESUME_DIR="../resume"
PIDS=()

# =============================================================================
# Help
# =============================================================================

if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: $0 [--help]"
    echo ""
    echo "Starts blog + resume Jekyll servers and Caddy reverse proxy."
    echo ""
    echo "  Blog:    http://localhost:$CADDY_PORT/"
    echo "  Resume:  http://localhost:$CADDY_PORT/resume/"
    echo "  Print:   http://localhost:$CADDY_PORT/resume/print/"
    echo "  Machine: http://localhost:$CADDY_PORT/resume/machine/"
    echo ""
    echo "Prerequisites:"
    echo "  - caddy installed (brew install caddy)"
    echo "  - Run from blog repo root (mcgarrah.github.io)"
    echo "  - Resume repo at ../resume"
    echo "  - Both sites pre-built (bundle exec jekyll build)"
    exit 0
fi

# =============================================================================
# Validation
# =============================================================================

echo "Checking prerequisites..."
echo ""

ERRORS=0

# --- Verify we're in the blog repo ---
if [ ! -f "_config.yml" ]; then
    echo "  ✗ _config.yml not found. Run this script from the blog repo root."
    ERRORS=$((ERRORS + 1))
else
    # Confirm this is actually mcgarrah.github.io (not the resume or another Jekyll site)
    REPO_NAME=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null)
    if [ "$REPO_NAME" != "mcgarrah.github.io" ]; then
        echo "  ✗ Expected mcgarrah.github.io repo, found: ${REPO_NAME:-not a git repo}"
        ERRORS=$((ERRORS + 1))
    else
        echo "  ✓ Blog repo (mcgarrah.github.io)"
    fi
fi

# --- Verify Caddyfile ---
if [ ! -f "Caddyfile" ]; then
    echo "  ✗ Caddyfile not found in $(pwd)"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✓ Caddyfile"
fi

# --- Verify resume repo ---
if [ ! -d "$RESUME_DIR" ]; then
    echo "  ✗ Resume directory not found at $RESUME_DIR"
    ERRORS=$((ERRORS + 1))
elif [ ! -f "$RESUME_DIR/_config.yml" ]; then
    echo "  ✗ $RESUME_DIR/_config.yml not found — not a Jekyll site"
    ERRORS=$((ERRORS + 1))
else
    RESUME_REPO_NAME=$(basename "$(git -C "$RESUME_DIR" rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null)
    if [ "$RESUME_REPO_NAME" != "resume" ]; then
        echo "  ✗ Expected resume repo at $RESUME_DIR, found: ${RESUME_REPO_NAME:-not a git repo}"
        ERRORS=$((ERRORS + 1))
    else
        echo "  ✓ Resume repo ($RESUME_DIR)"
    fi
fi

# --- Verify Caddy ---
if ! command -v caddy &>/dev/null; then
    echo "  ✗ caddy not found"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "    Install: brew install caddy"
    else
        echo "    Install: sudo apt install caddy"
    fi
    ERRORS=$((ERRORS + 1))
else
    echo "  ✓ caddy $(caddy version 2>/dev/null | head -1)"
fi

# --- Verify Ruby/bundler ---
if ! command -v ruby &>/dev/null; then
    echo "  ✗ ruby not found (install via rbenv)"
    ERRORS=$((ERRORS + 1))
else
    RUBY_VERSION=$(ruby -e "puts RUBY_VERSION")
    RUBY_MAJOR=$(echo "$RUBY_VERSION" | cut -d. -f1)
    RUBY_MINOR=$(echo "$RUBY_VERSION" | cut -d. -f2)
    if [ "$RUBY_MAJOR" -lt 3 ] || { [ "$RUBY_MAJOR" -eq 3 ] && [ "$RUBY_MINOR" -lt 2 ]; }; then
        echo "  ✗ Ruby >= 3.2 required (found $RUBY_VERSION)"
        echo "    Ruby 3.2 removed Object#tainted? — Jekyll < 4.3.2 crashes without it"
        ERRORS=$((ERRORS + 1))
    else
        echo "  ✓ ruby $RUBY_VERSION"
    fi
fi

if ! command -v bundle &>/dev/null; then
    echo "  ✗ bundler not found (gem install bundler)"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✓ bundler $(bundle --version | awk '{print $NF}')"
fi

# --- Verify Jekyll version ---
if command -v bundle &>/dev/null && [ -f "Gemfile" ]; then
    JEKYLL_VERSION=$(bundle exec jekyll --version 2>/dev/null | awk '{print $NF}')
    if [ -n "$JEKYLL_VERSION" ]; then
        JEKYLL_MAJOR=$(echo "$JEKYLL_VERSION" | cut -d. -f1)
        JEKYLL_MINOR=$(echo "$JEKYLL_VERSION" | cut -d. -f2)
        JEKYLL_PATCH=$(echo "$JEKYLL_VERSION" | cut -d. -f3)
        if [ "$JEKYLL_MAJOR" -lt 4 ] || { [ "$JEKYLL_MAJOR" -eq 4 ] && [ "$JEKYLL_MINOR" -lt 3 ]; } || \
           { [ "$JEKYLL_MAJOR" -eq 4 ] && [ "$JEKYLL_MINOR" -eq 3 ] && [ "$JEKYLL_PATCH" -lt 2 ]; }; then
            echo "  ✗ Jekyll >= 4.3.2 required (found $JEKYLL_VERSION)"
            echo "    Older versions crash on Ruby 3.2+ (Liquid tainted? method removed)"
            ERRORS=$((ERRORS + 1))
        else
            echo "  ✓ jekyll $JEKYLL_VERSION"
        fi
    fi
fi

# --- Verify Gemfile.lock exists in both repos (bundle install completed) ---
if [ ! -f "Gemfile.lock" ] && [ ! -f "Gemfile" ]; then
    echo "  ✗ Blog: no Gemfile found"
    ERRORS=$((ERRORS + 1))
elif [ -f "Gemfile" ] && ! bundle check --no-color >/dev/null 2>&1; then
    echo "  ✗ Blog: gems not installed (run: bundle install)"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✓ Blog gems installed"
fi

if [ -d "$RESUME_DIR" ] && [ -f "$RESUME_DIR/Gemfile" ]; then
    if ! (cd "$RESUME_DIR" && bundle check --no-color >/dev/null 2>&1); then
        echo "  ✗ Resume: gems not installed (run: cd $RESUME_DIR && bundle install)"
        ERRORS=$((ERRORS + 1))
    else
        echo "  ✓ Resume gems installed"
    fi
fi

# --- Verify _site/ exists (pre-built) ---
if [ ! -d "_site" ]; then
    echo "  ⚠ Blog: _site/ not found — will build before serving"
    BLOG_NEEDS_BUILD=true
else
    echo "  ✓ Blog _site/ exists"
    BLOG_NEEDS_BUILD=false
fi

if [ -d "$RESUME_DIR" ] && [ ! -d "$RESUME_DIR/_site" ]; then
    echo "  ⚠ Resume: _site/ not found — will build before serving"
    RESUME_NEEDS_BUILD=true
else
    echo "  ✓ Resume _site/ exists"
    RESUME_NEEDS_BUILD=false
fi

echo ""

# --- Abort if any hard errors ---
if [ "$ERRORS" -gt 0 ]; then
    echo "ERROR: $ERRORS prerequisite(s) failed. Fix the issues above and retry."
    exit 1
fi

# =============================================================================
# Local pre-flight checks (jekyll doctor, front matter lint, tag collisions,
# missing OG images) — blog only, informational, doesn't block startup.
# See jekyll-checks.sh for what each one covers.
# =============================================================================

source "$(dirname "${BASH_SOURCE[0]}")/jekyll-checks.sh"
run_local_checks

# =============================================================================
# Port checks
# =============================================================================

check_port() {
    local port=$1
    local label=$2
    local pid=""

    if command -v lsof &>/dev/null; then
        pid=$(lsof -i :"$port" -sTCP:LISTEN -P -n -t 2>/dev/null | head -1)
    elif command -v ss &>/dev/null; then
        pid=$(ss -tlnp "sport = :$port" 2>/dev/null | grep -oP 'pid=\K[0-9]+' | head -1)
    fi

    if [ -n "$pid" ]; then
        local process=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
        echo "ERROR: Port $port ($label) is already in use by $process (PID $pid)"
        echo "  Fix: kill $pid"
        exit 1
    fi
}

check_port $BLOG_PORT "Blog"
check_port $RESUME_PORT "Resume"
check_port $CADDY_PORT "Caddy"

# =============================================================================
# Build if needed
# =============================================================================

if [ "$BLOG_NEEDS_BUILD" = true ]; then
    echo "Building blog..."
    bundle exec jekyll build --drafts --future --unpublished --quiet
    echo "  ✓ Blog built"
fi

if [ "$RESUME_NEEDS_BUILD" = true ]; then
    echo "Building resume..."
    (cd "$RESUME_DIR" && bundle exec jekyll build --quiet)
    echo "  ✓ Resume built"
fi

# =============================================================================
# Cleanup on exit — kill all background processes
# =============================================================================

cleanup() {
    echo ""
    echo "Shutting down..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null
        wait "$pid" 2>/dev/null
    done
    exit 0
}

trap cleanup INT TERM

# =============================================================================
# Start services
# =============================================================================

echo "Starting Blog on :$BLOG_PORT..."
bundle exec jekyll serve --trace --port $BLOG_PORT --skip-initial-build \
    --drafts --future --unpublished --incremental \
    --livereload --livereload-port 35729 2>&1 | sed 's/^/  [blog] /' &
PIDS+=($!)

echo "Starting Resume on :$RESUME_PORT..."
(cd "$RESUME_DIR" && bundle exec jekyll serve --trace --port $RESUME_PORT \
    --skip-initial-build --incremental \
    --livereload --livereload-port 35730 2>&1 | sed 's/^/  [resume] /') &
PIDS+=($!)

# Give Jekyll servers a moment to bind their ports
sleep 3

echo "Starting Caddy on :$CADDY_PORT..."
caddy run --config Caddyfile 2>&1 | sed 's/^/  [caddy] /' &
PIDS+=($!)

sleep 1

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Local development environment ready"
echo ""
echo "  Blog:      http://localhost:$CADDY_PORT/"
echo "  Resume:    http://localhost:$CADDY_PORT/resume/"
echo "  Print:     http://localhost:$CADDY_PORT/resume/print/"
echo "  Machine:   http://localhost:$CADDY_PORT/resume/machine/"
echo ""
echo "  Direct (bypass proxy):"
echo "    Blog:    http://localhost:$BLOG_PORT/"
echo "    Resume:  http://localhost:$RESUME_PORT/resume/"
echo ""
echo "  Press Ctrl+C to stop all services."
echo "═══════════════════════════════════════════════════════════"
echo ""

# Wait for any child to exit (or Ctrl+C)
wait
