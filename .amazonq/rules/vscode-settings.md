# .vscode/settings.json — Intentionally Tracked

## Why This File Is Committed

The `.vscode/settings.json` file is intentionally tracked in this repository. It contains
the Jekyll Run plugin configuration needed to serve the site locally with the correct flags:

- `--config _config.yml,_config_drafts.yml` — loads the drafts overlay config
- `--drafts --future --unpublished` — renders draft and future-dated posts locally
- `--livereload --incremental` — enables live reload and incremental builds
- `--trace` — verbose error output for debugging

These settings are project-specific (not personal preference) and ensure anyone cloning
the repo can use the Jekyll Run VS Code extension with the correct arguments immediately.

## Do Not Remove From Git

If `.vscode/` appears in `.gitignore`, this file should be excluded from that pattern
or the gitignore entry should not be added. The settings are part of the development
workflow documented in `jekyll-run-plugin-fix.md`.
