# Project notes for AI agents

## drafts.mcgarrah.org is a deploy artifact — do not treat as source

`drafts.mcgarrah.org` (sibling repo `mcgarrah/drafts.mcgarrah.org`) is **not** a source
repository. It is a **build/deploy target** generated entirely from **this** repo
(`mcgarrah.github.io`) to preview draft/unpublished articles on a separate webpage.

How it works:

- `.github/workflows/deploy-drafts.yml` builds the Jekyll site with drafts + future posts
  (`jekyll build --drafts --future --config _config.yml,_config_drafts.yml`), then publishes
  the rendered `_site/` to `https://drafts.mcgarrah.org` (password-protected via the
  `DRAFTS_PASSWORD` secret).
- The deploy step clones `mcgarrah/drafts.mcgarrah.org`, replaces its contents with the
  built site, squashes to a **single orphan commit**, and **force-pushes**
  (`git push origin deploy:main --force`).

Consequences:

- **Never edit `drafts.mcgarrah.org` directly** — it is overwritten on every deploy. All
  real content lives here (`_drafts/`, `_posts/`).
- Its history is intentionally disposable (one commit per deploy), so a local clone will
  routinely look "diverged". To sync it, use `git reset --hard origin/main` — do not merge
  or rebase.

This note is mirrored in `.kiro/steering/drafts-deployment.md` for kiro-cli.
