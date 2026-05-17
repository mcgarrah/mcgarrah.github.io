---
published: false
---

# LinkedIn Post Archive

Archived copies of LinkedIn posts for version control and reference.

The `_linkedin/` prefix ensures Jekyll ignores this directory during builds — content here is not published on the blog.

## Purpose

Each LinkedIn post is a short-form hook (300-800 words) that distills the key insight from a Substack article and links to the full piece. LinkedIn drives traffic from the professional network (500+ connections) to the long-form content on Substack.

## Publication Flow

```
Substack article (long-form, canonical version)
    ↓
LinkedIn post (short hook + link to Substack)
```

## Naming Convention

Files follow the same date-prefix pattern as blog posts and Substack articles:

```
YYYY-MM-DD-short-title.md
```

## File Format

Each file includes:
- **Title** — The LinkedIn post headline
- **Substack URL** — Link to the full article this post promotes
- **LinkedIn URL** — Link to the published LinkedIn post (added after publication)
- **Tags/Topics** — For reference
- **Body** — The full text of the LinkedIn post as published

## Publication Schedule

| Date | File | Title | LinkedIn URL |
|------|------|-------|-------------|
| 2024-11-18 | `2024-11-18-isc2-cybersecurity-cert.md` | ISC2 Cybersecurity Certification | [Published](https://www.linkedin.com/pulse/isc2-cybersecurity-certification-michael-mcgarrah-ermfe/) |
| 2026-05-18 | `2026-05-18-five-stages-ds-platform.md` | Your Data Scientists Are Training on Garbage Data | TBD |
| 2026-06-15 | `2026-06-15-data-science-is-not-software-development.md` | If You Manage Data Scientists Like Software Engineers... | TBD |

## Cross-References

- **Substack archive:** `_substack/` — Long-form articles these posts link to
- **SVP positioning plan:** `_drafts/PERSONA-SVP.md` — Strategy and schedule
- **Draft tracker:** `_drafts/DRAFTS.md`
