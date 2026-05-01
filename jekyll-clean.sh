#!/bin/bash
# Clean Jekyll build artifacts and caches
#
# Usage:
#   ./jekyll-clean.sh          # Soft clean: bundle exec jekyll clean (_site/ and .jekyll-metadata)
#   ./jekyll-clean.sh -h       # Hard clean: also removes .jekyll-cache directory
#   ./jekyll-clean.sh --hard   # Same as -h
#
# The hard clean fixes incremental build staleness on macOS where FSEvents
# file watching occasionally misses changes, leaving .jekyll-cache in a
# stale state that causes new drafts/posts to not appear after restart.
#
# Note: bundle exec jekyll clean removes _site/ and .jekyll-metadata
#       but does NOT remove .jekyll-cache — that requires explicit removal.

set -e

HARD=false
for arg in "$@"; do
    case "$arg" in
        -h|--hard)
            HARD=true
            ;;
        *)
            echo "Usage: $0 [-h|--hard]"
            echo "  -h, --hard  Also remove .jekyll-cache directory"
            exit 1
            ;;
    esac
done

echo "Running: bundle exec jekyll clean"
bundle exec jekyll clean

if [ "$HARD" = true ]; then
    if [ -d ".jekyll-cache" ]; then
        echo "Removing .jekyll-cache..."
        rm -rf .jekyll-cache
        echo "Done."
    else
        echo ".jekyll-cache not found, skipping."
    fi

    if [ -f ".jekyll-metadata" ]; then
        echo "Removing .jekyll-metadata..."
        rm -f .jekyll-metadata
        echo "Done."
    else
        echo ".jekyll-metadata not found, skipping."
    fi

    if [ -d "_site" ]; then
        echo "Removing _site/..."
        rm -rf _site
        echo "Done."
    else
        echo "_site/ not found, skipping."
    fi

    echo "Hard clean complete."
else
    echo "Soft clean complete. Use -h or --hard to also remove .jekyll-cache."
fi
