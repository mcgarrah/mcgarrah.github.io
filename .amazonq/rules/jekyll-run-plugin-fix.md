# Jekyll Run VS Code Plugin — Multi-Root Workspace Fix

## Known Bug: TypeError in Multi-Root Workspaces

The Jekyll Run extension (Dedsec727.jekyll-run v1.7.0) crashes with `TypeError: Cannot read properties of null (reading 'toString')` in multi-root workspaces. The plugin's `Config.get()` uses an unscoped `getConfiguration().get('jekyll-run')` call that returns `null` in multi-root contexts, even when `.code-workspace` and `.vscode/settings.json` have correct values.

**Root cause:** macOS GUI apps (Dock, Spotlight) don't inherit shell PATH, so the plugin uses system Ruby 2.6 which fails. The plugin's error handler then crashes on `null`, producing the misleading TypeError.

**Fix:** Use rbenv with Ruby 3.3, launch VS Code from a terminal, and optionally patch the plugin.

## Primary Fix: rbenv + Launch from Terminal

### Ruby Version Management (rbenv)

macOS ships system Ruby 2.6 (too old for Jekyll 4.4.1). Homebrew Ruby 4.0 works but breaks `--livereload`. Use `rbenv` with Ruby 3.3 for full compatibility.

```bash
brew install rbenv ruby-build
rbenv install 3.3.11
cd mcgarrah.github.io
rbenv local 3.3.11    # creates .ruby-version
gem install bundler
bundle install
```

### Shell Configuration

Add to `~/.zshrc` (before `source $ZSH/oh-my-zsh.sh`):

```bash
# rbenv Ruby version manager (macOS only)
if [[ "$(uname -s)" == "Darwin" ]]; then
  eval "$(rbenv init - zsh)"
fi
```

Create `~/.zshenv` for non-interactive shells (VS Code extensions):

```bash
if [[ "$(uname -s)" == "Darwin" && -d "$HOME/.rbenv" ]]; then
  export PATH="$HOME/.rbenv/shims:$HOME/.rbenv/bin:$PATH"
fi
```

### Launch VS Code from Terminal

macOS GUI apps inherit their environment from `launchd`, not `~/.zshrc`. **Always launch VS Code from a terminal** where rbenv Ruby is on PATH:

```bash
code ~/Personal/Github-mcgarrah/articles-workspace.code-workspace
```

WSL2 and Linux are not affected — VS Code Remote Server runs inside a login shell that sources `~/.zshrc`.

## New System Setup Checklist

1. Install rbenv: `brew install rbenv ruby-build`
2. Install Ruby 3.3: `rbenv install 3.3.11`
3. Set project Ruby: `cd mcgarrah.github.io && rbenv local 3.3.11`
4. Add rbenv init to `~/.zshrc` and `~/.zshenv` (see above)
5. `source ~/.zshrc && ruby --version` — verify Ruby 3.3
6. `gem install bundler && bundle install`
7. Install Jekyll Run extension in VS Code
8. Add `jekyll-run` settings to VS Code User settings (see above)
9. **Launch VS Code from terminal**: `code articles-workspace.code-workspace`
10. Click Jekyll Run button — verify it starts without TypeError

## Fallback

If the plugin still misbehaves, use the bash script:

```bash
./jekyll-start.sh
```

## Incremental Mode Staleness on macOS (Occasional)

When using `--incremental` on macOS, Jekyll can occasionally get into a stale state where new drafts/future posts do not appear even after a plugin restart.

### Symptom

- Jekyll Run starts without errors
- Existing pages render normally
- New draft/future articles are missing from local output

### Keep Incremental, But Use This Recovery Sequence

1. Use **Jekyll Stop** in VS Code
2. Run a one-time cleanup in the repo root:

```bash
rm -rf .jekyll-cache .jekyll-metadata _site
```

3. Start Jekyll again with the normal arguments (including `--incremental`)

### Notes

- This is an occasional recovery step, not a reason to disable `--incremental`
- WSL2/Linux setups are typically more stable with incremental file detection
- If staleness repeats on macOS, do a full stop/start instead of restart and re-run the cleanup above

## Jekyll Cache and Clean Facts

- `.jekyll-cache` is a **directory** (not a file). Use `[ -d ".jekyll-cache" ]` to check for it in shell scripts.
- `bundle exec jekyll clean` removes `_site/` and `.jekyll-metadata` **but does NOT remove `.jekyll-cache`**.
- To fully clear all incremental build state, remove all three explicitly:

```bash
bundle exec jekyll clean
if [ -d ".jekyll-cache" ]; then
    rm -rf .jekyll-cache
fi
```

- The `jekyll-clean.sh` script in `mcgarrah.github.io/` does exactly this — it runs `jekyll clean` then conditionally removes `.jekyll-cache` if it exists.
- For the planned `jekyll-run.Clean` VS Code command, `bundle exec jekyll clean` alone is **insufficient** for fixing incremental staleness — the command must also remove `.jekyll-cache`.

## References

- Blog post: [Jekyll Run Plugin: Local Development Settings That Actually Work](/jekyll-run-vscode-plugin-local-development/)
- Blog post: [Jekyll Run Plugin: Fixing the Multi-Root Workspace Crash](/jekyll-run-plugin-multiroot-workspace-bug/)
- Plugin source: https://github.com/Kanna727/jekyll-run
