#!/bin/bash
# Clean Jekyll build artifacts and caches
# Run this when new drafts or files don't appear after restarting Jekyll serve
bundle exec jekyll clean

# jekyll clean removes _site/ and .jekyll-metadata but NOT .jekyll-cache
# Remove .jekyll-cache explicitly to fix incremental build staleness on macOS
if [ -d ".jekyll-cache" ]; then
    echo "Removing .jekyll-cache..."
    rm -rf .jekyll-cache
    echo "Done."
else
    echo ".jekyll-cache not found, skipping."
fi
