# Ruby Environment — macOS rbenv Configuration

## The Problem

macOS ships system Ruby 2.6 at `/System/Library/Frameworks/Ruby.framework/`. This version is:
- Too old for Jekyll 4.4.1 (requires Ruby 3.0+)
- Too old for modern YAML APIs (`permitted_classes` keyword added in Ruby 3.1)
- Too old for Homebrew Ruby gems that target 3.x
- Read-only on macOS Sequoia+ (SIP-protected)

Homebrew installs Ruby 4.0 but it breaks Jekyll `--livereload` (EventMachine compatibility).

**The correct Ruby for all Jekyll work is rbenv with Ruby 3.3.11.**

## Current Setup

| Component | Path | Version |
|-----------|------|---------|
| System Ruby | `/System/Library/Frameworks/Ruby.framework/` | 2.6.10 (do not use) |
| Homebrew Ruby | `/opt/homebrew/opt/ruby/bin/ruby` | 4.x (breaks livereload) |
| rbenv Ruby | `~/.rbenv/versions/3.3.11/bin/ruby` | 3.3.11 ✅ (use this) |
| rbenv shims | `~/.rbenv/shims/ruby` | Delegates to version selected by `.ruby-version` |

### Per-Repo `.ruby-version` Files

rbenv selects the Ruby version based on `.ruby-version` in the project root. Repos that
use Ruby must have this file:

| Repo | `.ruby-version` | Status |
|------|----------------|--------|
| `mcgarrah.github.io` | `3.3.11` | ✅ Present |
| `resume` | `3.3.11` | ✅ Present |
| `jekyll-run` | — | Not needed (Node.js/TypeScript project) |

If a repo is missing `.ruby-version` and you're in a directory without one, rbenv falls
through to system Ruby 2.6. **Always check for `.ruby-version` when Ruby commands fail.**

## Platform Differences

### macOS

The hardest environment. Three compounding issues:

1. **System Ruby 2.6** is SIP-protected and too old for Jekyll 4.4.1
2. **Homebrew Ruby 4.0** works for builds but breaks `--livereload` (EventMachine)
3. **Non-interactive shells** (Amazon Q `executeBash`, VS Code tasks, cron) don't source
   `~/.zshrc`, so `eval "$(rbenv init - zsh)"` never runs and the rbenv shim resolves
   to system Ruby 2.6 even when `.ruby-version` is present
4. **GUI-launched VS Code** (Dock, Spotlight) inherits `launchd` environment, not shell
   PATH — always launch VS Code from a terminal on macOS

### WSL2 / Linux

Mostly "just works." Key differences from macOS:

- **No system Ruby conflict** — WSL2 Debian/Ubuntu don't ship a system Ruby that
  interferes. Install rbenv normally and it's the only Ruby on PATH.
- **VS Code Remote Server** runs inside a login shell that sources `~/.bashrc` or
  `~/.zshrc` — rbenv init runs automatically. The GUI app PATH problem doesn't exist.
- **Amazon Q `executeBash`** in VS Code Remote (WSL2) runs through the Remote Server's
  shell, which typically has rbenv initialized. Less likely to hit the shim resolution
  bug than macOS, but `.ruby-version` in the repo root is still the safest guarantee.
- **`--livereload` works** with Homebrew or rbenv Ruby — the EventMachine compatibility
  issue is macOS-specific.
- **File watching** for `--incremental` is more reliable on Linux (inotify) than macOS
  (FSEvents). Fewer stale cache issues.

### Windows (native, not WSL2)

Not a supported development environment for this project. All Windows work goes through
WSL2. If Ruby commands are needed on native Windows, use the WSL2 terminal.

## The Shell Environment Problem (macOS-specific)

Amazon Q's `executeBash` tool runs non-interactive shells that do **not** source `~/.zshrc`.
This means `eval "$(rbenv init - zsh)"` never runs, and the rbenv shim at
`~/.rbenv/shims/ruby` resolves to system Ruby 2.6 instead of 3.3.11.

The `~/.zshenv` file (which non-interactive shells do source) adds rbenv to PATH:
```bash
if [[ "$(uname -s)" == "Darwin" && -d "$HOME/.rbenv" ]]; then
  export PATH="$HOME/.rbenv/shims:$HOME/.rbenv/bin:$PATH"
fi
```

But this only puts the shim on PATH — it doesn't run `rbenv init`, so the shim may still
resolve incorrectly without a `.ruby-version` file in the current directory.

### Workarounds for Amazon Q / Non-Interactive Shells

**Option 1 (preferred): Ensure `.ruby-version` exists in the repo root.**
The rbenv shim reads this file and selects the correct version even without `rbenv init`.
This works on both macOS and WSL2.

**Option 2: Use the rbenv Ruby binary directly.**
```bash
$HOME/.rbenv/versions/3.3.11/bin/ruby -e "puts RUBY_VERSION"
$HOME/.rbenv/versions/3.3.11/bin/gem install bundler
$HOME/.rbenv/versions/3.3.11/bin/bundle install
```
This bypasses the shim entirely. Works on both macOS and WSL2.

**Option 3: Source rbenv init inline (macOS only, fragile).**
```bash
eval "$(rbenv init - bash)" && ruby --version
```

## When Running Ruby Commands

### Do
- Check for `.ruby-version` in the repo root before running Ruby commands
- Use `$HOME/.rbenv/versions/3.3.11/bin/ruby` if the shim isn't resolving correctly
- Run `ruby --version` first to verify you're on 3.3.x before proceeding
- Use `bundle exec` for all Jekyll and gem commands

### Do NOT
- Use system Ruby (`/usr/bin/ruby`) — it's 2.6 on macOS and will fail on modern gems
- Install gems with `sudo gem install` — use rbenv's gem instead
- Assume `ruby` on PATH is the right version — always verify
- Use Homebrew Ruby for Jekyll work on macOS — it breaks `--livereload`

## YAML Validation

System Ruby 2.6 does not support `permitted_classes` in `YAML.load_file`. When validating
YAML files that contain Date objects (like resume `data.yml`), use:

```bash
# Correct — uses rbenv Ruby 3.3 (works on macOS and WSL2)
$HOME/.rbenv/versions/3.3.11/bin/ruby -e "
  require 'yaml'; require 'date'
  YAML.load_file('_data/data.yml', permitted_classes: [Date])
  puts 'YAML is valid'
"

# Wrong — system Ruby 2.6 on macOS, will error on permitted_classes
ruby -e "require 'yaml'; YAML.load_file('_data/data.yml')"
```

## New Repo Setup

When creating a new repo that uses Ruby:

```bash
cd new-repo
rbenv local 3.3.11    # creates .ruby-version
gem install bundler
bundle install
```

Add `.ruby-version` to the repo (do NOT gitignore it — it's intentional configuration).

## VS Code Integration

macOS GUI apps (Dock, Spotlight) don't inherit shell PATH. **Always launch VS Code from
a terminal** where rbenv is initialized:

```bash
code ~/Personal/Github-mcgarrah/articles-workspace.code-workspace
```

WSL2 and Linux are not affected — VS Code Remote Server runs inside a login shell that
sources `~/.zshrc`.

See `jekyll-run-plugin-fix.md` for the full VS Code + rbenv integration details.
