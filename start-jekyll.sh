#!/bin/bash

# =============================================================================
# Setting up on macOS (Homebrew + rbenv)
# =============================================================================
#
# macOS ships system Ruby 2.6 which is too old for Jekyll 4.4.1.
# Homebrew Ruby 4.0 works but breaks --livereload.
# Use rbenv with Ruby 3.3 for full compatibility.
#
# 1. Install rbenv:
#      brew install rbenv ruby-build
#
# 2. Install Ruby 3.3 (version pinned in .ruby-version):
#      rbenv install 3.3.11
#
# 3. Add to ~/.zshrc (before 'source $ZSH/oh-my-zsh.sh'):
#      if [[ "$(uname -s)" == "Darwin" ]]; then
#        eval "$(rbenv init - zsh)"
#      fi
#
# 4. Create ~/.zshenv (for VS Code extensions / non-interactive shells):
#      if [[ "$(uname -s)" == "Darwin" && -d "$HOME/.rbenv" ]]; then
#        export PATH="$HOME/.rbenv/shims:$HOME/.rbenv/bin:$PATH"
#      fi
#
# 5. Reload shell and install gems:
#      source ~/.zshrc
#      ruby --version          # should show 3.3.x
#      gem install bundler
#      bundle install
#
# 6. IMPORTANT: On macOS, always launch VS Code from a terminal:
#      code ~/github/articles-workspace.code-workspace
#    macOS GUI apps (Dock/Spotlight) don't inherit your shell PATH,
#    so the Jekyll Run plugin would use system Ruby 2.6 and crash.
#
# =============================================================================
# Setting up on Ubuntu 22.04 LTS / 24.04 LTS (WSL2 / Linux)
# =============================================================================
#
# sudo apt -y install make build-essential ruby ruby-dev

# Update ~/.bashrc and ~/.zshrc with this:
#
# # Ruby Jekyll Gems
# if [ ! -d $HOME/.gems ]; then
#   mkdir $HOME/.gems
# fi
# export GEM_HOME=$HOME/.gems
# export PATH=$HOME/.gems/bin:$PATH

# gem install jekyll bundler
# bundle install

# VS Code Extension
#
# Name: Jekyll Run
# Id: Dedsec727.jekyll-run
# Description: Build and Run your Jekyll static website
# Version: 1.7.0
# Publisher: Dedsec727
# VS Marketplace Link: https://marketplace.visualstudio.com/items?itemName=Dedsec727.jekyll-run
#
# File -> Preferences -> Settings (Ctrl+,)
#  Scroll to "Jekyll Run - Configuration"
#  Or set in .vscode/settings.json per workspace

# Jekyll serve flags:
#   --trace         Show full Ruby backtrace on errors
#   --drafts        Render posts in the _drafts/ folder
#   --future        Publish posts with a future date
#   --unpublished   Render posts with published: false in front matter
#   --livereload    Auto-refresh browser on file save
#   --incremental   Only rebuild changed pages (faster, but restart
#                   if edits to _includes/ or _layouts/ seem stale)

bundle exec jekyll serve --trace --drafts --future --unpublished --livereload --incremental
