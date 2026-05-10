---
layout: post
title: "Running Multiple Jekyll Sites Locally Under One Domain"
image: /assets/images/og/jekyll-multi-site-local-development.png
categories: [web-development, technical, jekyll]
tags: [jekyll, local-development, reverse-proxy, caddy, macos, wsl2, github-pages]
excerpt: "My blog serves from the webroot and my resume lives at /resume/ — both Jekyll sites on the same domain in production. Replicating that URL structure locally without a heavy web server required a lightweight reverse proxy and some Jekyll livereload lore."
description: "How to run multiple Jekyll sites locally under one domain with correct path routing using Caddy reverse proxy, including livereload through the proxy, handle vs handle_path path-ownership semantics, and the architectural principles behind development-production parity."
date: 2026-05-16
last_modified_at: 2026-05-16
published: true
seo:
  type: BlogPosting
  date_published: 2026-05-16
  date_modified: 2026-05-16
---

In production, my blog serves from the webroot (`mcgarrah.org/`) and my resume lives at `mcgarrah.org/resume/` — two separate Jekyll repositories deployed to the same GitHub Pages domain. Links between them use absolute paths: the blog's navigation links to `/resume/`, the resume's header links back to `/`. GitHub Pages merges both repos under one domain and the routing is invisible.

Locally, that routing does not exist. Each site runs its own `bundle exec jekyll serve` on its own port — and suddenly every cross-site link is broken. Click "Resume" in the blog nav and you get a 404. Click the blog link in the resume header and you land on the wrong server.

This is the same class of problem you encounter in any microservices architecture: services that communicate via path-based routing in production need that same routing replicated in development, or integration testing becomes impossible. The question is how lightweight you can make that routing layer without sacrificing developer experience — specifically, livereload.

<!-- excerpt-end -->

## The Problem

| Site | Production URL | Local URL | baseurl |
|------|---------------|-----------|---------|
| Blog | `mcgarrah.org/` | `localhost:4001/` | `""` (empty) |
| Resume | `mcgarrah.org/resume/` | `localhost:4002/resume/` | `"/resume"` |

Cross-site links use absolute paths (`/resume/`, `/resume/print/`). In production these resolve correctly because both sites share a domain. Locally, the blog's WEBrick server has no idea `/resume/` exists — it is a completely separate process. The routing layer that GitHub Pages provides for free must be replicated locally.

## Options Evaluated

| Approach | Livereload? | Cross-platform? | Complexity | Verdict |
|----------|-------------|-----------------|------------|---------|
| **Caddy reverse proxy** | ✅ Both sites | ✅ macOS + WSL2 | Single binary, 4-line config | **Selected** |
| Symlink `_site/` | ❌ Blog only | ✅ | Zero deps, fragile | One-off verification only |
| Python `http.server` | ❌ | ✅ | Zero deps | Final link checking only |
| Jekyll multisite build | ✅ | ✅ | High (config merge) | [Explicitly rejected](/merging-two-jekyll-websites-architectural-analysis/) |
| Traefik / mitmproxy | ✅ | ✅ | Overkill | Not justified |

### Why Caddy

[Caddy](https://caddyserver.com/) won on five criteria: single binary (no runtime dependencies), four-line config, cross-platform behavior (identical on macOS and WSL2), already in my toolchain for [Proxmox](/caddy-reverse-proxy-proxmox-web-ui/) and [Ceph](/caddy-reverse-proxy-ceph-dashboard/) proxying, and extensible — adding a third site is one more `handle` block.

The rejected alternatives each fail on developer experience. The symlink approach breaks on every `jekyll build` and offers no livereload for the resume. Python's `http.server` is static — no incremental rebuilds. The multisite config merges two independent Gemfiles, plugin sets, and Sass namespaces into one build, creating coupling that defeats the purpose of separate repositories. The architectural boundary between the sites is intentional.

## Implementation

### The Caddyfile

Lives in the blog repo root (since the blog owns the webroot):

```caddyfile
:8080 {
    # Only log errors — keeps terminal quiet during normal use,
    # but surfaces routing problems (502s, timeouts) immediately
    log {
        output stdout
        format console
        level ERROR
    }

    # Gzip responses — Jekyll's WEBrick does not compress, so
    # Caddy adds it. Useful for testing real-world page weights
    # and catching bloated assets during development.
    encode gzip

    handle /resume/* {
        reverse_proxy localhost:4002
    }

    handle /resume {
        redir /resume/ permanent
    }

    handle {
        reverse_proxy localhost:4001
    }
}
```

### Path Ownership: `handle` vs `handle_path`

One subtlety that bit me initially: Caddy's `handle_path` strips the matched prefix before forwarding. That sounds helpful — but the resume's Jekyll server is configured with `baseurl: "/resume"`, meaning it *expects* requests to arrive with the `/resume` prefix. If Caddy strips it, the resume server receives `/print/` when it expects `/resume/print/` — and returns a 404.

The fix is `handle` (not `handle_path`), which forwards the full path including `/resume` to the resume server. The server already knows how to route requests under its own baseurl.

The rule of thumb:

- **`handle_path`** — downstream serves at root, doesn't know about the prefix (strip it)
- **`handle`** — downstream is configured with the prefix (preserve it)

Getting this wrong produces 404s that *look* like the proxy is working — you see the resume's styled 404 page, not Caddy's error — which makes the bug confusing to diagnose. This is the same path-ownership question you encounter in Kubernetes Ingress controllers, AWS ALB path-based routing, and API gateway configurations. Documenting which layer owns the prefix prevents a class of routing bugs that are notoriously difficult to debug in production.

### Livereload Through the Proxy

My initial assumption was that livereload would break through Caddy. It does not — and understanding why reveals useful Jekyll internals.

Jekyll's `--livereload` injects a `<script>` tag into every served page. That script opens a WebSocket connection to `ws://localhost:35729/livereload`. The critical detail: **this is a direct connection to the Jekyll server's livereload port, not a request through the HTTP port that Caddy proxies.** The browser makes two independent connections:

1. `localhost:8080` → Caddy → Jekyll (page content via HTTP)
2. `localhost:35729` → Jekyll directly (reload notifications via WebSocket)

Caddy never sees the WebSocket traffic. Livereload works transparently with zero proxy configuration.

The only constraint when running two Jekyll servers simultaneously: each needs its own livereload port. Jekyll defaults to 35729, so the second server must use `--livereload-port 35730`. Without this, the second server fails to bind and livereload silently stops working for one site — no error message, just no refresh.

```bash
# Blog: default livereload port
bundle exec jekyll serve --livereload --livereload-port 35729

# Resume: offset to avoid collision
bundle exec jekyll serve --livereload --livereload-port 35730
```

The `--livereload-port` flag is poorly documented Jekyll lore. It exists specifically for multi-server scenarios but is rarely mentioned because most people run one Jekyll server at a time.

I verified the full stack: both sites return 200 through Caddy, both inject their respective livereload scripts (`port=35729` and `port=35730`), both WebSocket ports accept connections, and touching a file in either repo triggers an independent incremental rebuild with automatic browser refresh. The developer experience is identical to standalone `jekyll serve` — with correct cross-site linking.

### The Startup Script

Rather than managing three terminal windows, `jekyll-caddy.sh` orchestrates all services:

```bash
./jekyll-caddy.sh
```

The script validates prerequisites before starting anything:

- Git repo identity (confirms `mcgarrah.github.io` and `resume` by name)
- Ruby >= 3.2, Jekyll >= 4.3.2, bundler, Caddy binary
- Gems installed in both repos (`bundle check`)
- Ports 4001, 4002, 8080 available
- Builds `_site/` automatically if missing

Then starts all three processes with the same flags as `jekyll-start.sh` (`--trace --drafts --future --unpublished --incremental --livereload`), using ports 4001/4002 to avoid colliding with a standalone `jekyll-start.sh` on the default 4000.

```text
═══════════════════════════════════════════════════════════════
  Local development environment ready

  Blog:      http://localhost:8080/
  Resume:    http://localhost:8080/resume/
  Print:     http://localhost:8080/resume/print/
  Machine:   http://localhost:8080/resume/machine/

  Direct (bypass proxy):
    Blog:    http://localhost:4001/
    Resume:  http://localhost:4002/resume/

  Press Ctrl+C to stop all services.
═══════════════════════════════════════════════════════════════
```

## The Architectural Principle

The pattern here is general: any multi-repo deployment that shares a domain in production needs local routing parity for integration testing. The specific tools (Jekyll, Caddy) are incidental — the principle is:

1. **Each service owns its own build and deploy lifecycle** — separate repos, separate CI, independent release cadence
2. **A routing layer merges them under one origin** — GitHub Pages in production, Caddy locally
3. **Cross-service links use absolute paths** — not relative, not port-specific, not environment-aware
4. **The routing layer is the thinnest possible** — 4 lines of config, not a full web server
5. **Development mirrors production topology** — otherwise you are testing something different from what you deploy

This is the same separation of concerns you apply to microservices behind an API gateway, static assets behind a CDN, or multiple applications behind a load balancer. The development environment should replicate the production routing contract. When it does not, integration bugs hide until deploy — the most expensive place to find them.

## Closing Thought

Back in April I wrote about the [sitemap challenges](/managing-multiple-jekyll-sites-sitemap-challenges/) of running two Jekyll sites under one domain, then followed up with an [architectural analysis](/merging-two-jekyll-websites-architectural-analysis/) of whether to merge them. The conclusion was clear: keep them separate. Separate repos, separate CI, separate deploy cycles, separate concerns. The resume has a Jinja2/XeLaTeX pipeline, a Pandoc plugin, and structured data requirements that have no business in the blog's Gemfile.

What those articles did not solve was the developer experience gap. I had made the correct architectural decision — independent services with a shared domain — but had not invested in the local tooling to make that architecture comfortable to work in. Every time I updated a cross-site link, I had to deploy to production to verify it worked. That is the kind of friction that accumulates into avoidance: you stop making cross-site improvements because testing them is annoying.

This Caddy setup closes that gap. One script, three services, full livereload, correct routing. I can now iterate on both sites simultaneously with the same feedback loop I get from a single `jekyll serve`. The architectural decision to keep the sites separate no longer carries a developer experience tax.

That is the broader lesson: good architecture decisions sometimes need tooling investment to remain good decisions. Without the local proxy, the separation would eventually become painful enough to reconsider — and the merger would be the wrong answer to the wrong problem. The right answer was always "keep the architecture, fix the tooling."

## Related Posts

- [Managing Multiple Jekyll Sites Under One Domain: Sitemap Challenges](/managing-multiple-jekyll-sites-sitemap-challenges/) — The production-side problems that motivated this work
- [Merging Two Jekyll Websites: Architectural Analysis](/merging-two-jekyll-websites-architectural-analysis/) — Why these sites stay separate (and why that decision needs local tooling)
- [Caddy Reverse Proxy for Proxmox Web UI](/caddy-reverse-proxy-proxmox-web-ui/) — Same tool, different use case
- [Caddy Reverse Proxy for Ceph Dashboard](/caddy-reverse-proxy-ceph-dashboard/) — Pattern reuse across the homelab
- [Rebuilding My Resume Site From the Ground Up](/resume-site-ground-up-rebuild/) — The rebuild that motivated this tooling

