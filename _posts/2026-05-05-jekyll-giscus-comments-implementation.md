---
title: "Adding Comments to a Static Site: Why I Chose Giscus for Jekyll"
layout: post
categories: [web-development, technical, jekyll]
tags: [jekyll, giscus, comments, github-discussions, github-pages, gdpr, engagement]
excerpt: "Jekyll has no database. So where do comments live? I evaluated six approaches — from hosted services to custom Lambda functions — before landing on Giscus. Here's the decision process and the implementation."
description: "How to add a comment system to a Jekyll blog on GitHub Pages using Giscus and GitHub Discussions. Covers the evaluation of Disqus, Isso, Utterances, GitHub Issues API, Staticman, and Giscus, with implementation details, GDPR considerations, and the advantages of keeping everything in the GitHub ecosystem."
date: 2026-05-05
last_modified_at: 2026-05-05
published: true
seo:
  type: BlogPosting
  date_published: 2026-05-05
  date_modified: 2026-05-05
---

Jekyll is a static site generator. There's no server, no database, no backend. When someone visits a page, they get pre-built HTML files served from a CDN. That's the whole point — it's fast, cheap, and secure.

But comments need state. Someone writes a comment, it has to be stored somewhere, and the next visitor needs to see it. This is the fundamental tension of adding comments to a static site: you need a data store, but you chose a platform specifically because it doesn't have one.

<!-- excerpt-end -->

## The Problem

I wanted comments on this blog for a simple reason: readers ask good questions. When someone finds a gap in a Proxmox walkthrough or catches an error in a Ceph command, that feedback is valuable — not just to me, but to the next person reading the same post. Email works for one-to-one, but comments are one-to-many.

The requirements:

1. **No self-hosted infrastructure** — I'm not running a database for blog comments
2. **Free or very cheap** — This is a hobby blog
3. **GitHub-friendly** — My readers are technical; most have GitHub accounts
4. **GDPR-compatible** — No third-party tracking cookies
5. **Persistent** — Comments survive site rebuilds and theme changes
6. **Searchable** — Ideally indexed and findable
7. **Low maintenance** — No moderation queue to babysit

## The Alternatives I Evaluated

### Disqus — The Default Choice (Rejected)

[Disqus](https://disqus.com/) is the most common comment system for static sites. It's easy to embed and has a large user base.

Why I rejected it:

- **Ads on the free tier** — Disqus injects ads into your comment section unless you pay
- **Tracking and privacy** — Disqus loads significant third-party JavaScript and tracks users across sites. This is a GDPR nightmare for a blog that already went through [extensive GDPR compliance work](/implementing-gdpr-compliance-jekyll-adsense/)
- **Data ownership** — Comments live on Disqus's servers. If they shut down or change terms, your comments are gone
- **Heavy JavaScript** — The embed script is large and slows page load

The original Jekyll theme I forked (Contrast) actually had Disqus support built in. The dead code is still in my `post.html` layout — a `disqus_thread` div that never renders because `site.comments.disqus_shortname` is never set.

### Isso — Self-Hosted Alternative (Rejected)

[Isso](https://isso-comments.de/) is a self-hosted, lightweight commenting server. It stores comments in a SQLite database and has a clean, minimal interface.

Why I rejected it:

- **Requires a server** — You need to run the Isso daemon somewhere. That's infrastructure I don't want to maintain for blog comments
- **SQLite on a server** — Backups, uptime, security patches — all for a comment system

The theme also had Isso support built in. Same dead code situation — `isso_domain` is never configured.

### GitHub Issues API — Custom Lambda (Evaluated Deeply)

This approach uses GitHub Issues as the comment store. Each blog post maps to a GitHub Issue. Comments on the Issue appear as comments on the post. [Aleksandr Hovhannisyan's implementation](https://www.aleksandrhovhannisyan.com/blog/jekyll-comment-system-github-issues/) is the best-known version.

I went deep on this one — deep enough to have [ChatGPT convert the original Netlify serverless function to a Python Lambda](https://chatgpt.com/c/67804dbd-2d38-8010-8074-f43b50bee567). The full prototype:

```python
def get_comments_for_post(event, context):
    """
    Lambda function to fetch comments for a GitHub issue dynamically.
    """

    try:
        # Extract query parameters
        query_params = event.get("queryStringParameters", {})
        issue_number = query_params.get("id")
        github_url = query_params.get("url")

        if not issue_number or not issue_number.isdigit():
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "You must specify a valid issue ID."}),
            }

        # Determine owner and repo
        if github_url:
            owner, repo = extract_owner_and_repo(github_url)
        else:
            owner = query_params.get("owner")
            repo = query_params.get("repo")

        if not owner or not repo:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "You must specify 'owner' and 'repo' or provide a valid GitHub URL."}),
            }

        issue_number = int(issue_number)

        # Check API rate limit
        rate_limit = octokit.request("GET /rate_limit")["rate"]
        remaining_requests = rate_limit["remaining"]
        print(f"GitHub API requests remaining: {remaining_requests}")
        if remaining_requests == 0:
            return {
                "statusCode": 503,
                "body": json.dumps({"error": "API rate limit exceeded."}),
            }

        # Fetch comments for the given issue
        comments_response = octokit.paginate(
            "GET /repos/{owner}/{repo}/issues/{issue_number}/comments",
            {"owner": owner, "repo": repo, "issue_number": issue_number},
        )

        # Process comments
        response = []
        for comment in comments_response:
            response.append({
                "user": {
                    "avatarUrl": comment["user"]["avatar_url"],
                    "name": escape(comment["user"]["login"]),
                    "isAuthor": comment["author_association"] == "OWNER",
                },
                "dateTime": comment["created_at"],
                "dateRelative": str((datetime.now() - datetime.fromisoformat(
                    comment["created_at"].replace("Z", ""))).days) + " days ago",
                "isEdited": comment["created_at"] != comment["updated_at"],
                "body": escape(markdown(comment["body"])),
            })

        return {
            "statusCode": 200,
            "body": json.dumps({"data": response}),
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Unable to fetch comments for this post."}),
        }
```

This prototype handled input validation, GitHub API rate limiting, pagination, relative date formatting, edit detection, and Markdown rendering. It worked — but it was a lot of moving parts for blog comments.

Why I ultimately rejected it:

- **Requires a serverless function** — Whether it's Netlify Functions, AWS Lambda, or Cloudflare Workers, you need a backend to proxy the GitHub API (to avoid exposing tokens client-side)
- **GitHub Issues aren't designed for comments** — Issues have a flat structure. No threading, no reactions on individual comments (only on the issue itself)
- **Manual issue creation** — You have to create a GitHub Issue for each post and link them. That's a maintenance burden
- **API rate limits** — The GitHub API has rate limits that could be hit on popular posts

### Utterances — GitHub Issues, Client-Side (Close Second)

[Utterances](https://github.com/utterance/utterances) solves the serverless function problem by using a GitHub App to authenticate directly from the client. It still uses GitHub Issues as the backend but doesn't need a proxy.

Why I almost chose it:

- No server needed — just a `<script>` tag
- Clean, minimal UI
- GitHub authentication (my audience has GitHub accounts)
- Open source

Why I chose Giscus instead:

- Utterances uses **Issues**, Giscus uses **Discussions** — Discussions have threading, categories, and reactions
- Utterances was less actively maintained at the time I evaluated it
- Giscus is essentially "Utterances but better" — same concept, newer implementation, more features

### Staticman — Git-Based Comments (Rejected)

[Staticman](https://staticman.net/) takes a different approach: comments are submitted via a form, processed by a bot, and committed to your repository as data files (YAML/JSON). Jekyll then renders them at build time.

Why I rejected it:

- **Build required for every comment** — Each comment triggers a site rebuild. That's slow and burns CI minutes
- **Moderation via pull requests** — Clever, but adds friction
- **Self-hosted bot or shared instance** — The shared instance has availability issues; self-hosting is more infrastructure

### GDPR-Compliant Approaches

The [Jekyll Codex GDPR-compliant comments](https://jekyllcodex.org/blog/gdpr-compliant-comment/) guide was useful for understanding the privacy landscape. Any solution that loads third-party JavaScript or sends user data to external servers needs consent management.

## Why Giscus Won

[Giscus](https://giscus.app/) uses **GitHub Discussions** as the comment backend. It's a single `<script>` tag that embeds a widget powered by the GitHub Discussions API via a GitHub App.

The key insight: **everything stays in the GitHub ecosystem**. The blog source is on GitHub. The build runs on GitHub Actions. The site deploys to GitHub Pages. Comments live in GitHub Discussions. There's no external service, no separate database, no additional account.

What sealed the decision:

- **Threaded replies** — Discussions support nested replies, Issues don't
- **Reactions** — Readers can react to individual comments, not just the top-level post
- **Categories** — Comments go into the "Announcements" category, keeping them organized
- **Automatic mapping** — `pathname` mapping means Giscus creates a Discussion for each post URL automatically. No manual issue creation
- **Lazy loading** — The widget loads only when scrolled into view (`loading: lazy`)
- **Theme matching** — `preferred_color_scheme` follows the reader's dark/light mode preference
- **Searchable** — GitHub Discussions are fully searchable, both on GitHub and via search engines
- **No server** — Just a `<script>` tag and a `_config.yml` entry
- **GDPR-friendly** — Giscus loads from `giscus.app` (a GitHub App), not a third-party ad network. No tracking cookies. The [self-hosting option](https://github.com/giscus/giscus/blob/main/SELF-HOSTING.md) exists if you want full control

## Implementation

### Step 1: Enable GitHub Discussions

In the repository settings (`mcgarrah/mcgarrah.github.io`), enable the Discussions feature and create an "Announcements" category.

### Step 2: Install the Giscus GitHub App

Go to [giscus.app](https://giscus.app/), select your repository, and configure the options. It generates the `<script>` tag and gives you the `repo_id` and `category_id` values.

### Step 3: Add Configuration to `_config.yml`

```yaml
giscus:
  repo: mcgarrah/mcgarrah.github.io
  repo_id: R_kgDOKBKIdw
  category: Announcements
  category_id: DIC_kwDOKBKId84Cq3DK
  mapping: pathname
  strict: 0
  reactions_enabled: 1
  emit_metadata: 0
  input_position: bottom
  theme: preferred_color_scheme
  lang: en
  loading: lazy
```

Key configuration choices:

- **`mapping: pathname`** — Maps posts to Discussions by URL path. This means `/proxmox-ceph-nearfull/` gets its own Discussion automatically
- **`strict: 0`** — Fuzzy matching on the pathname. Tolerates minor URL changes
- **`input_position: bottom`** — Comment box below existing comments (natural reading order)
- **`loading: lazy`** — Don't load the iframe until the reader scrolls to the comments section. Improves initial page load performance
- **`theme: preferred_color_scheme`** — Matches the reader's OS dark/light mode setting

### Step 4: Add the Widget to the Post Layout

In `_layouts/post.html`:

```html
{% raw %}{%- if site.giscus -%}
<section class="page__comments">
  <script src="https://giscus.app/client.js"
          data-repo="{{ site.giscus.repo }}"
          data-repo-id="{{ site.giscus.repo_id }}"
          data-category="{{ site.giscus.category }}"
          data-category-id="{{ site.giscus.category_id }}"
          data-mapping="{{ site.giscus.mapping }}"
          data-strict="{{ site.giscus.strict }}"
          data-reactions-enabled="{{ site.giscus.reactions_enabled }}"
          data-emit-metadata="{{ site.giscus.emit_metadata }}"
          data-input-position="{{ site.giscus.input_position }}"
          data-theme="{{ site.giscus.theme }}"
          data-lang="{{ site.giscus.lang }}"
          data-loading="{{ site.giscus.loading }}"
          crossorigin="anonymous"
          async>
  </script>
</section>
{%- endif -%}{% endraw %}
```

Every `_config.yml` value is templated via Liquid — no hardcoded values in the layout. The {% raw %}`{%- if site.giscus -%}`{% endraw %} guard means the widget only renders if Giscus is configured, so the theme works without it.

### Legacy Dead Code

The post layout still contains the original theme's Isso and Disqus support:

```html
{% raw %}{% if page.comments != false and site.comments.isso or site.comments.disqus %}
  {% if site.comments.isso_domain %}<div id="isso-thread"></div>{% endif %}
  {% if site.comments.disqus_shortname %}<div id="disqus_thread"></div>{% endif %}
{% endif %}{% endraw %}
```

This never renders because neither `site.comments.isso_domain` nor `site.comments.disqus_shortname` is set in `_config.yml`. It's harmless dead code from the Contrast theme fork. I've left it in case someone forks this blog and wants to use those systems instead.

## The GitHub Ecosystem Advantage

What I find elegant about this setup is how the pieces reinforce each other:

| Component | Service | Data Location |
|-----------|---------|---------------|
| Source code | GitHub repository | `mcgarrah/mcgarrah.github.io` |
| Build & deploy | GitHub Actions | `.github/workflows/jekyll.yml` |
| Hosting | GitHub Pages | `mcgarrah.org` via CNAME |
| Comments | GitHub Discussions | Same repository |
| Security scanning | GitHub CodeQL | `.github/workflows/codeql.yml` |
| Dependency updates | GitHub Dependabot | `.github/dependabot.yml` |

Everything is in one place. One login, one set of permissions, one backup strategy (the git repository itself). If GitHub goes down, the whole blog is down anyway — there's no additional point of failure from the comment system.

Comments are also version-controlled in a sense — GitHub Discussions have full edit history, and they're tied to the repository. If I ever migrate the blog, the Discussions come with the repo.

## What I'd Do Differently

- **Clean up the dead Isso/Disqus code** — It's been there since the fork. Time to remove it
- **Add a `comments: false` front matter option** — The Isso/Disqus code checks `page.comments != false`, but the Giscus block doesn't. Some posts (like the privacy policy) shouldn't have comments
- **Consider self-hosting Giscus** — The [self-hosting guide](https://github.com/giscus/giscus/blob/main/SELF-HOSTING.md) would eliminate the dependency on `giscus.app`. Low priority since the service has been reliable

## Related Posts

- [Building This Blog: Jekyll on GitHub Pages](/setting-up-jekyll-blog-github-pages/) — Setup guide with brief Giscus section
- [How the Sausage Is Made](/jekyll-markdown-feature-reference/) — Feature inventory including comments
- [Implementing GDPR Compliance for Jekyll with AdSense](/implementing-gdpr-compliance-jekyll-adsense/) — The GDPR work that informed comment system requirements
- [The CI/CD Pipeline Behind This Jekyll Blog](/jekyll-github-actions-cicd-pipeline/) — How GitHub Actions ties into the ecosystem
