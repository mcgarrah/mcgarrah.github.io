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
./start-jekyll.sh
```

## References

- Blog post: [Jekyll Run Plugin: Local Development Settings That Actually Work](/jekyll-run-vscode-plugin-local-development/)
- Blog post: [Jekyll Run Plugin: Fixing the Multi-Root Workspace Crash](/jekyll-run-plugin-multiroot-workspace-bug/)
- Plugin source: https://github.com/Kanna727/jekyll-run
