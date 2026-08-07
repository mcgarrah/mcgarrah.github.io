#!/bin/bash
# jekyll-checks.sh — Shared local pre-flight checks for jekyll-start.sh and jekyll-caddy.sh
#
# Not meant to be run directly — sourced by the scripts above:
#   source ./jekyll-checks.sh
#   run_local_checks
#
# These mirror the checks .github/workflows/jekyll.yml runs before deploy,
# plus one CI doesn't run: a tag-slug collision check across _posts/ AND
# _drafts/ together. CI's own lint step only scans _posts/ (jekyll.yml:
# `python3 scripts/lint-frontmatter.py _posts/`), and the production build
# never includes _drafts/ (`jekyll build` — no --drafts flag). So a tag that
# collides only inside a draft, or between a draft and a published post, is
# invisible to CI right up until that draft gets promoted — at which point
# _plugins/tag_category_generator.rb silently overwrites one tag page with
# the other. Local `--drafts` builds are the only place this ever shows up.
#
# All checks here are informational (non-blocking) — they warn, they don't
# stop the dev server from starting. If a check would fail CI, it says so.

check_jekyll_doctor() {
    echo "-- jekyll doctor --"
    if ! bundle exec jekyll doctor; then
        echo "⚠ jekyll doctor reported issues above — this will also fail CI"
    fi
    echo ""
}

check_frontmatter_lint() {
    echo "-- Front matter lint (_posts/, same scope as CI) --"
    if ! python3 scripts/lint-frontmatter.py _posts/; then
        echo "⚠ Front matter errors in _posts/ above — this WILL fail CI"
    fi
    echo ""
}

check_tag_collisions_all() {
    echo "-- Tag slug collisions (_posts/ + _drafts/, CI only checks _posts/) --"
    if ! python3 scripts/lint-frontmatter.py --tags-only; then
        echo "⚠ Tag slug collision above — will silently overwrite a tag page once that draft is promoted"
    fi
    echo ""
}

check_og_images() {
    local missing=0
    local missing_files=""

    for post in _posts/*.md; do
        local img=$(grep -m1 "^image:" "$post" | sed 's/^image: *//' | tr -d '"' | tr -d "'")
        if [ -z "$img" ]; then
            continue
        fi

        # Strip leading slash — paths are relative to repo root
        local file="${img#/}"
        if [ ! -f "$file" ]; then
            missing=$((missing + 1))
            missing_files="$missing_files\n  • $post → $file"
        fi
    done

    if [ "$missing" -gt 0 ]; then
        echo "-- OG images --"
        echo "⚠ Missing OG images ($missing posts):"
        echo -e "$missing_files"
        echo ""
        echo "  Generate with: python3 bin/generate-og-images.py"
        echo ""
    fi
}

run_local_checks() {
    echo "═══════════════════════════════════════════════════════════"
    echo "  Local pre-flight checks (blog)"
    echo "═══════════════════════════════════════════════════════════"
    check_jekyll_doctor
    check_frontmatter_lint
    check_tag_collisions_all
    check_og_images
}
