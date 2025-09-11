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

# File -> Perferences -> Settings (Ctrl+,)
#  Scroll to "Jekyll Run - Configuration"
#  Add "--trace" for more detailed error message on build
#  Add "--drafts" to see the "_drafts" folder posts
#  Add "--future" to publishes posts with a future date

# bundle exec jekyll serve

# For Debug and Drafts

bundle exec jekyll serve --trace --drafts --future
