#!/bin/bash

# Setting up on Ubuntu 22.04 LTS / 24.04 LTS
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
