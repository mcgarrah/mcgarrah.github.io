# Building in Public: Preview Sites, Domain Migrations, and the Google Tax

**Subtitle:** Infrastructure for writing, the registrar migration saga, and why Google makes simple things hard

**Author:** McGarrah

**Planned:** July 13, 2026 (Monday)

**URL:** TBD

**Tags:** Software Engineering, Web Development, Infrastructure, Open Source, DNS, Google, Jekyll

---

My previous newsletters covered [infrastructure](https://mcgarrah.substack.com/p/from-homelabs-to-machine-learning), [the blog platform](https://mcgarrah.substack.com/p/from-markdown-to-production), [storage failures](https://mcgarrah.substack.com/p/when-storage-breaks), and [reviving a VS Code extension](TBD). This one covers the meta-work of running a technical blog — the infrastructure you build to support the writing itself, and the external dependencies that fight you every step of the way.

Three threads this month: building a password-protected draft preview site so reviewers can see unpublished content, migrating 16 domains away from SquareSpace's walled garden, and the ongoing battle with Google's service sprawl.

*Thanks for reading! Subscribe for free to receive new posts and support my work.*

## Building a Draft Preview Site

I write 30-40 drafts at a time. I wanted trusted reviewers to see the *rendered* site — not raw markdown on GitHub — before I publish. Sounds simple. GitHub Pages has no authentication. My repo is public. And I didn't want to add Netlify, Cloudflare, or any new external service.

The solution: a separate GitHub repo at `drafts.mcgarrah.org`, built automatically via GitHub Actions with `--drafts --future`, selectively encrypted with Staticrypt, and deployed on every push to main. Three articles cover the full journey from "what are my options?" to "it's live and working."

- [Building a Draft Preview Site — Part 1: Exploring the Options](https://mcgarrah.org/jekyll-draft-preview-site-part-1/) — Seven options evaluated, most eliminated. Netlify (new dependency), Cloudflare (new dependency), self-hosted (not ready), project page (shared robots.txt problem). Two survivors: Staticrypt on a subdomain, or no auth at all.

- [Building a Draft Preview Site — Part 2: Refining the Design](https://mcgarrah.org/jekyll-draft-preview-site-part-2/) — The config overlay approach, Giscus feedback on a separate repo, Staticrypt navigation quirks, and the DNS routing trick that lets multiple GitHub repos serve different custom domains.

- [Building a Draft Preview Site — Part 3: The Implementation](https://mcgarrah.org/jekyll-draft-preview-site-part-3/) — The real workflow with all the edge cases. Staticrypt's `-o` flag doesn't exist. Directory output flattens paths. Full-site encryption is wasteful. Hash-based verification catches silent failures. Eight issues hit during implementation, all documented with fixes.

The system is live at `drafts.mcgarrah.org` and deploys automatically. Reviewers enter a shared password, see the full site with drafts and future posts visible, and can leave feedback via Giscus comments that stay separate from production.

## Migrating 16 Domains from SquareSpace to Porkbun

Google Domains was great. Then Google sold it to SquareSpace. SquareSpace is expensive, has no API, and locks you into their ecosystem. For a homelab that needs programmatic DNS management (Technitium, PowerDNS, automation), that's a dealbreaker.

- [Migrating 16 Domains from SquareSpace to Porkbun](https://mcgarrah.org/name-service-registrars/) — The multi-week process of transferring domains in batches, managing costs ($182 total for renewals), dealing with SquareSpace's 5-day transfer holds, and the critical lesson: **SquareSpace deletes all DNS records after transfer with no export option.** You must back up records before initiating transfer. 9 of 16 domains complete (56%).

The most complex domain — mcgarrah.org with 25+ DNS records across GitHub Pages, Mailgun email, DigitalOcean apps, and multiple subdomains — is deliberately last. Every other domain is practice for the big one.

## The Google Services Tax

Running a technical blog shouldn't require managing six interconnected Google services, each with its own dashboard, approval process, and opaque requirements. And yet.

- [The Google Services Tax on a Simple Blog](https://mcgarrah.org/google-service-sprawl/) — Analytics, Search Console, Custom Search, AdSense, Tag Manager, PageSpeed Insights — each exists in its own silo with its own integration complexity. The most maddening part: Google's own services don't integrate seamlessly with each other.

The article also documents months of work trying to get AdSense approved — GDPR compliance, E-E-A-T improvements, sitemap fixes, crawler access debugging — and still getting rejected with vague "your site isn't ready" feedback. The battle continues.

## The Caddy Reverse Proxy Addition

A quick infrastructure win that solved a daily annoyance:

- [Caddy Reverse Proxy for Ceph Dashboard](https://mcgarrah.org/caddy-reverse-proxy-ceph-dashboard/) — The Ceph Dashboard runs on whichever node is the active ceph-mgr, which changes on failover. Adding it to the existing Caddy proxy with health checks gives a single stable URL that automatically routes to the active node. Five minutes of config, permanent fix.

## What These Have in Common

All of these are meta-work — infrastructure that supports the actual creative output rather than being the output itself. The draft preview site makes writing better. The domain migration enables future automation. The Google services (theoretically) help readers find the content. The Caddy proxy makes monitoring easier.

The trap is spending all your time on meta-work and never writing the actual content. The escape is recognizing when the infrastructure is "good enough" and shipping imperfect articles rather than perfecting the pipeline.

I'm still working on that balance.

## What's Next

- **Game development** — Returning to an old passion with StarVoyager (C++ modernization) and a Godot tower defense game
- **Jekyll GDPR plugin** — Extracting my custom GDPR implementation into a reusable Ruby gem
- **Dark mode toggle** — The site respects OS dark mode but has no manual override. Time to add a switch.
- **Kubernetes on Proxmox** — The k8s-proxmox project is ready for its first real workloads

## About Me

I'm Michael McGarrah — a cloud architect and data scientist with 25+ years in enterprise infrastructure. I hold an M.S. in Computer Science (AI/ML) from Georgia Tech, a B.S. in Computer Science from NC State, and I'm currently pursuing an Executive MBA at UNC Wilmington.

You can find more of my writing at [mcgarrah.org](https://mcgarrah.org), my detailed resume at [mcgarrah.org/resume](https://mcgarrah.org/resume), and my profiles on [LinkedIn](https://www.linkedin.com/in/michaelmcgarrah/), [GitHub](https://github.com/mcgarrah), and [Google Scholar](https://scholar.google.com/citations?user=Lt7T2SwAAAAJ).
