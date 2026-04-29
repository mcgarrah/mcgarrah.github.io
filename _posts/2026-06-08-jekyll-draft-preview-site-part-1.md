---
title: "Building a Draft Preview Site for Jekyll — Part 1: Exploring the Options"
layout: post
categories: [jekyll, github-pages, devops]
tags: [jekyll, github-pages, staticrypt, drafts, preview, ci-cd, github-actions]
excerpt: "I wanted a way to share unfinished blog posts with reviewers before publishing. Sounds simple — but GitHub Pages has no authentication, serves one site per repo, and my drafts are already in a public repository. Here's every option I considered and why most of them didn't survive."
description: "Exploration of options for creating a password-protected Jekyll draft preview site on GitHub Pages, including Staticrypt, Netlify, Cloudflare Access, self-hosting, and project pages. Part 1 of a three-part series."
date: 2026-06-08
last_modified_at: 2026-06-08
seo:
  type: BlogPosting
  date_published: 2026-06-08
  date_modified: 2026-06-08
---

I write a lot of drafts. At any given time I have 40-50 posts in various stages of completion sitting in my `_drafts/` folder. Some are nearly done, some are research notes, and some are half-baked ideas that might never see the light of day.

The problem: I want trusted reviewers to see the *rendered* site with drafts included — not raw markdown files on GitHub. I want them to give feedback before I publish. And I want Google to stay far away from unfinished content. Three hard constraints — no authentication on GitHub Pages, a public source repository, and no search engine indexing of drafts — drove every architectural decision that follows.

<!-- excerpt-end -->

This is Part 1 of a three-part series:
- **Part 1** (this post): Exploring every option I considered
- **Part 2**: [Refining the approach — what survived and why](/jekyll-draft-preview-site-part-2/)
- **Part 3**: [The complete implementation](/jekyll-draft-preview-site-part-3/)

## The Problem

Jekyll has great built-in support for drafts (`_drafts/` folder) and future-dated posts. Running `bundle exec jekyll serve --drafts --future` locally shows everything. But "locally" doesn't help when I want someone else to review my work.

What I need:
1. A separate site that builds with `--drafts --future`
2. Not indexed by Google
3. Some form of access control — even minimal
4. Automated — I don't want to manually deploy every time I push
5. No impact on the production site at `mcgarrah.org`

What I have to work with:
- GitHub Pages (free, already hosting the production site)
- Porkbun (DNS registrar, already managing `mcgarrah.org`)
- GitHub Actions (already running CI/CD for the production build)
- A public repository (meaning the raw markdown is already visible to anyone)

That last point matters more than you'd think.

## The Security Reality Check

Before diving into options, I had to be honest about what "access control" means here. My `mcgarrah.github.io` repository is **public**. Anyone can browse to `_drafts/` on GitHub right now and read every unpublished post in raw markdown.

So what am I actually protecting? Not the content — that ship has sailed. What I want is:
- **A signal to reviewers**: "This isn't ready for public consumption"
- **A barrier to casual discovery**: Someone Googling a topic shouldn't land on my half-written draft
- **No indexing**: Search engines must not crawl the preview site

This reframes the entire problem. I don't need enterprise authentication. I need a speed bump and a `noindex` tag.

## Option 1: Netlify with Password Protection

Netlify's free tier includes site-wide password protection. The workflow would be:
- GitHub Actions builds Jekyll with `--drafts --future`
- Deploys to Netlify via CLI
- Netlify serves the site behind a shared password
- CNAME `drafts.mcgarrah.org` points to Netlify

**Pros:** Dead simple. Real server-side password. Built-in `X-Robots-Tag: noindex`. Always-on.

**Why I eliminated it:** It's a new external service. I'd need a Netlify account, API tokens, and another platform to manage. My constraint was to stay within GitHub + Porkbun — the tools I already use. Netlify is a fine service, but adding it for a draft preview site felt like overkill.

## Option 2: Cloudflare Access

Cloudflare Zero Trust (free tier, up to 50 users) can gate a subdomain behind email-based one-time-pin authentication. Real per-user auth, audit logs, the works.

**Pros:** Proper authentication. Per-user access control. Free tier is generous.

**Why I eliminated it:** Requires Cloudflare. I use Porkbun for DNS and don't want to proxy traffic through Cloudflare or move DNS management. Adding Cloudflare for one subdomain introduces a dependency I'd rather avoid. Same "new external service" problem as Netlify.

## Option 3: Self-Hosted on Proxmox

I run a six-node Proxmox cluster with Ceph storage. I could serve the drafts site from Caddy with HTTP Basic Auth, or eventually from Kubernetes with ingress-nginx.

**Pros:** Full control. Real authentication. Uses existing infrastructure.

**Why I eliminated it:** My homelab isn't ready for external-facing services yet. The Kubernetes cluster is still in the infrastructure build-out phase. Even if it were ready, tying reviewer access to my home internet uptime is a bad idea. And honestly, running a web server for a blog preview site is like using a sledgehammer to hang a picture frame.

I'll revisit this when K8s is production-ready, but that's months away.

## Option 4: Separate Branch in the Same Repo

Create a `drafts` branch, build with `--drafts --future`, deploy to a different GitHub Pages site.

**Why it doesn't work:** GitHub Pages deploys one branch to one domain per repo. You can't have `main` → `mcgarrah.org` and `drafts` → `drafts.mcgarrah.org` from the same repository. A separate branch helps with content management but doesn't solve the hosting problem.

## Option 5: Project Page at `mcgarrah.org/drafts/`

GitHub Pages project sites serve at `<username>.github.io/<repo-name>/`. My resume already works this way — the `resume` repo serves at `mcgarrah.org/resume/`. A repo named `drafts` would serve at `mcgarrah.org/drafts/`.

**Pros:** No DNS changes. Familiar pattern. Works immediately.

**Why I deprioritized it:** The `robots.txt` problem. The file lives at the domain root (`mcgarrah.org/robots.txt`) and is served by the main site. To block crawlers from `/drafts/`, I'd need to add `Disallow: /drafts/` to the *production* site's `robots.txt` — which violates my constraint of not modifying the production site. The `noindex` meta tag on each page still works, but `robots.txt` is the first line of defense and I'd be giving that up.

Also, the path is guessable. Anyone who knows the main site exists might try `/drafts/` out of curiosity.

## Option 6: Staticrypt on GitHub Pages

[Staticrypt](https://github.com/robinmoisson/staticrypt) encrypts HTML files with AES-256-GCM using a password-derived key. Each page is replaced with a password prompt that decrypts the content in-browser. No server-side auth needed.

**Pros:** Works on any static host including GitHub Pages. No external services. Password prompt signals "private preview."

**Cons:** Security through obscurity — but we already established that the source is public. The password is a UX signal, not a lock. Each page is encrypted independently, so navigation requires `--remember` to avoid re-prompting on every click.

**This one survived.** Combined with a separate GitHub repo and automated deployment, it checks every box.

## Option 7: Separate GitHub Repo WITHOUT Any Auth

Same as Option 6 but skip Staticrypt entirely. The drafts site is publicly accessible but:
- `robots.txt` blocks crawlers
- `<meta name="robots" content="noindex, nofollow">` on every page
- No links from the production site
- No Google Analytics, no sitemap, no RSS feed

**This also survived.** Given that the source markdown is already public, this is a defensible starting point. The password from Staticrypt is a nice-to-have, not a must-have.

## What About `drafts.github.io`?

I briefly wondered if I could use `drafts.github.io` as the domain. Short answer: no. GitHub Pages `*.github.io` domains are tied to GitHub usernames. `drafts.github.io` would belong to whoever owns the `drafts` GitHub account. You get exactly one: `<username>.github.io`.

## Where I Landed

Two options survived the elimination process:

1. **Separate GitHub repo + Staticrypt** — password-protected, fully automated, zero external services
2. **Separate GitHub repo, no auth** — even simpler, relies on `noindex` and obscurity

Both use:
- A new repo (`drafts.mcgarrah.org`) with GitHub Pages enabled
- GitHub Actions in the main repo to build and push
- A `_config_drafts.yml` overlay to change the URL, disable analytics, and redirect Giscus comments
- DNS CNAME in Porkbun pointing `drafts.mcgarrah.org` to GitHub Pages

The subdomain approach (`drafts.mcgarrah.org`) won over the project page (`mcgarrah.org/drafts/`) because it gets its own `robots.txt`, its own cookie scope, and doesn't require modifying the production site.

In [Part 2](/jekyll-draft-preview-site-part-2/), I'll walk through the refined design — the config overlay, the GitHub Actions workflow, the Giscus feedback setup, and the gaps I found when I started thinking through the implementation details.

---

*This is Part 1 of a three-part series on building a Jekyll draft preview site:*
- **Part 1** (this post): Exploring every option I considered
- **Part 2**: [Refining the approach — what survived and why](/jekyll-draft-preview-site-part-2/)
- **Part 3**: [The complete implementation](/jekyll-draft-preview-site-part-3/)
