---
layout: post
title: "Running Multiple Jekyll Sites Locally Under One Domain"
image: /assets/images/og/jekyll-multi-site-local-development.png
categories: [web-development, technical, jekyll]
tags: [jekyll, local-development, reverse-proxy, caddy, macos, wsl2, github-pages]
excerpt: "My blog serves from the webroot and my resume lives at /resume/ — both Jekyll sites on the same domain in production. Getting that same URL structure working locally without a heavy web server turned out to have several interesting options."
description: "Approaches for running multiple Jekyll sites locally under one domain with correct path routing, covering Caddy reverse proxy, symlink tricks, Jekyll multisite builds, and the tradeoffs of each approach for macOS and WSL2 development environments."
date: 2026-05-16
last_modified_at: 2026-05-16
published: true
seo:
  type: BlogPosting
  date_published: 2026-05-16
  date_modified: 2026-05-16
---

In production, my blog serves from the webroot (`mcgarrah.org/`) and my resume lives at `/resume/` — two separate Jekyll repositories deployed to the same GitHub Pages domain. Links between them use absolute paths: the blog's navigation links to `/resume/`, the resume's header links back to `/`. It works seamlessly in production because GitHub Pages merges both repos under one domain.

Locally, it is a different story. Each site runs its own `bundle exec jekyll serve` on its own port. The blog at `localhost:4000/` and the resume at `localhost:4000/resume/` — except they cannot both bind port 4000. So the resume runs on 4001, and suddenly every cross-site link is broken. Click "Resume" in the blog nav and you get a 404. Click the blog link in the resume header and you land on the wrong server.

I wanted to fix this without installing Nginx or Apache. Here are the options I evaluated.

<!-- excerpt-end -->

## The Problem

| Site | Production URL | Local URL | baseurl |
|------|---------------|-----------|---------|
| Blog | `mcgarrah.org/` | `localhost:4000/` | `""` (empty) |
| Resume | `mcgarrah.org/resume/` | `localhost:4001/resume/` | `"/resume"` |

Cross-site links use absolute paths (`/resume/`, `/resume/print/`). In production these resolve correctly because both sites share a domain. Locally, the blog's WEBrick server has no idea `/resume/` exists — it is a completely separate process.

## Option 1: Caddy Reverse Proxy (Recommended)

[Caddy](https://caddyserver.com/) is a single static binary with automatic HTTPS and a dead-simple config format. It is the lightest "real" reverse proxy available — no package manager dependencies, no config directories, no daemon management.

### Setup

```bash
# macOS
brew install caddy

# Ubuntu/WSL2
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install caddy
```

### Caddyfile

Create a `Caddyfile` in your workspace root (or home directory):

```caddyfile
:8080 {
    # Resume site at /resume/
    handle_path /resume/* {
        reverse_proxy localhost:4001
    }
    # Exact /resume (no trailing slash) — redirect to /resume/
    handle /resume {
        redir /resume/ permanent
    }

    # Blog (everything else)
    handle {
        reverse_proxy localhost:4000
    }
}
```

### Running

Terminal 1 — Blog:
```bash
cd ~/github/mcgarrah.github.io
bundle exec jekyll serve --port 4000
```

Terminal 2 — Resume:
```bash
cd ~/github/resume
bundle exec jekyll serve --port 4001
```

Terminal 3 — Caddy:
```bash
caddy run --config Caddyfile
```

Browse to `http://localhost:8080/` — blog at root, resume at `/resume/`, all cross-site links work.

### Pros
- Single binary, zero config complexity
- Works identically on macOS and WSL2
- Handles path rewriting correctly (strips `/resume` prefix before proxying)
- Can add HTTPS with `localhost` directive if needed for testing service workers
- Already familiar if you use Caddy for other homelab proxying

### Cons
- Third process to manage (Caddy itself)
- Port 8080 is the "real" URL — you test there, not on 4000/4001 directly
- Requires Caddy installation (though it is a single binary)

## Option 2: Symlink the Resume _site into the Blog _site

The simplest zero-dependency approach: build both sites, then symlink the resume's output into the blog's output directory.

### Setup

```bash
# Build both sites
cd ~/github/mcgarrah.github.io && bundle exec jekyll build
cd ~/github/resume && bundle exec jekyll build

# Symlink resume output into blog output
ln -sf ~/github/resume/_site ~/github/mcgarrah.github.io/_site/resume

# Serve the blog (which now includes /resume/)
cd ~/github/mcgarrah.github.io
bundle exec jekyll serve --skip-initial-build
```

### Pros
- Zero additional tools — just `ln` and Jekyll
- Single port, single server, correct URL structure
- Works on macOS and WSL2

### Cons
- **Fragile** — `jekyll build` or `jekyll serve` wipes `_site/` and breaks the symlink
- No livereload for the resume (must rebuild manually)
- Must rebuild resume separately and re-symlink after changes
- `--skip-initial-build` is required or Jekyll destroys the symlink on start
- Incremental builds on the blog side will also break it

### Variant: Post-build script

A wrapper script that builds both, symlinks, and serves with `--skip-initial-build` makes this more practical for one-off testing but not for active development on both sites simultaneously.

## Option 3: Python http.server with a Merged Build

Similar to the symlink approach but using Python's built-in HTTP server instead of Jekyll serve:

```bash
# Build both
cd ~/github/mcgarrah.github.io && bundle exec jekyll build
cd ~/github/resume && bundle exec jekyll build

# Copy resume output into blog output
cp -r ~/github/resume/_site ~/github/mcgarrah.github.io/_site/resume

# Serve with Python
cd ~/github/mcgarrah.github.io/_site
python3 -m http.server 8080
```

### Pros
- Zero dependencies beyond Python (already installed everywhere)
- Correct URL structure
- Simple mental model

### Cons
- No livereload, no incremental builds
- Must rebuild and re-copy after every change
- Only useful for final verification, not active development

## Option 4: Jekyll Multisite Config (Single Build)

Jekyll can technically build both sites from one invocation if you structure the source correctly. The blog would include the resume as a subdirectory or Git submodule:

```
mcgarrah.github.io/
├── _config.yml          # Blog config
├── resume/
│   ├── _config.yml      # Resume config (ignored — uses blog's)
│   ├── _data/data.yml
│   ├── index.html
│   └── ...
└── ...
```

### Why This Does Not Work Well

- The resume has its own `_config.yml`, `Gemfile`, plugins, and Sass — merging configs is fragile
- Plugin conflicts (the resume uses `jekyll-pandoc-exports` which the blog does not)
- Different Sass entry points and variable namespaces
- Git submodules add complexity to the CI pipeline
- Defeats the purpose of separate repositories with independent deploy cycles

This is the approach I explicitly rejected in the [site merger analysis](/merging-two-jekyll-websites-architectural-analysis/). The sites are intentionally separate.

## Option 5: Traefik or mitmproxy (Overkill)

Both are capable reverse proxies but bring significantly more complexity than Caddy for this use case. Traefik wants Docker labels or a YAML config with routers/services/middlewares. mitmproxy is designed for traffic inspection, not static routing. Neither is worth the setup cost for "route two Jekyll sites by path prefix."

## My Choice: Caddy

Caddy wins because:

1. **Single binary** — `brew install caddy` or download from the website. No runtime dependencies.
2. **Four-line config** — The Caddyfile above is the entire configuration.
3. **I already use it** — Caddy proxies my [Proxmox Web UI](/caddy-reverse-proxy-proxmox-web-ui/) and [Ceph Dashboard](/caddy-reverse-proxy-ceph-dashboard/) in the homelab. Same tool, same mental model.
4. **Cross-platform** — Identical behavior on macOS and WSL2/Ubuntu.
5. **Extensible** — If I later add a third site (documentation, API docs), it is one more `handle_path` block.

The symlink approach is fine for quick one-off verification ("does this link actually work?") but falls apart for active development where you want livereload on both sites.

## Wrapper Script

For convenience, a script that starts all three processes:

```bash
#!/bin/bash
# dev-serve.sh — Start blog + resume + Caddy for integrated local development
#
# Prerequisites: caddy, ruby/bundler in both repos
# Browse: http://localhost:8080/

BLOG_DIR=~/github/mcgarrah.github.io
RESUME_DIR=~/github/resume
CADDY_PORT=8080

echo "Starting blog on :4000..."
(cd "$BLOG_DIR" && bundle exec jekyll serve --port 4000 --livereload) &
BLOG_PID=$!

echo "Starting resume on :4001..."
(cd "$RESUME_DIR" && bundle exec jekyll serve --port 4001 --livereload --incremental) &
RESUME_PID=$!

# Wait for Jekyll servers to start
sleep 3

echo "Starting Caddy on :$CADDY_PORT..."
caddy run --config "$BLOG_DIR/Caddyfile" &
CADDY_PID=$!

echo ""
echo "  Blog:   http://localhost:$CADDY_PORT/"
echo "  Resume: http://localhost:$CADDY_PORT/resume/"
echo "  Print:  http://localhost:$CADDY_PORT/resume/print/"
echo ""
echo "Press Ctrl+C to stop all servers."

# Cleanup on exit
trap "kill $BLOG_PID $RESUME_PID $CADDY_PID 2>/dev/null; exit" INT TERM
wait
```

## The `handle_path` vs `handle` Distinction

One subtlety worth noting: Caddy's `handle_path` strips the matched prefix before forwarding. This is critical because the resume's Jekyll server already serves at `/resume/` (via `baseurl: "/resume"`). If Caddy forwarded `/resume/print/` as-is, the resume server would look for `/resume/resume/print/` — a double prefix.

With `handle_path /resume/*`, Caddy strips `/resume` and forwards `/print/` to the resume server, which then prepends its own `baseurl` internally. The request arrives correctly.

If your resume's `baseurl` were empty (serving at root on its own port), you would use `handle` instead and let the full path through. The choice depends on how the downstream Jekyll site is configured.

## Open Questions

- Should the Caddyfile live in the blog repo, the resume repo, or a shared dotfiles location?
- Is there value in a `docker-compose.yml` that runs both Jekyll servers plus Caddy for truly reproducible environments?
- Could the [Run Jekyll](/run-jekyll-bug-fixes-and-code-review/) VS Code extension be taught to start both servers and the proxy automatically?

## Related Posts

- [Caddy Reverse Proxy for Proxmox Web UI](/caddy-reverse-proxy-proxmox-web-ui/) — Same tool, different use case
- [Merging Two Jekyll Websites — Architectural Analysis](/merging-two-jekyll-websites-architectural-analysis/) — Why these sites stay separate
- [Managing Multiple Jekyll Sites and Sitemap Challenges](/managing-multiple-jekyll-sites-sitemap-challenges/) — The production side of multi-site
