# Setting up on Ubuntu 22.04 LTS
#
# sudo apt -y install make build-essential ruby ruby-dev
# echo "" >> $HOME/.bashrc
# echo "# Ruby Jekyll Gems" >> $HOME/.bashrc
# echo "if [ ! -d $HOME/gems ]; then" >> $HOME/.bashrc
# echo "  mkdir $HOME/gems" >> $HOME/.bashrc"
# echo "fi" >> $HOME/.bashrc"
# echo "export GEM_HOME=$HOME/gems" >> $HOME/.bashrc
# echo "export PATH=$HOME/gems/bin:$PATH" >> $HOME/.bashrc
# source $HOME/.bashrc
# gem install jekyll bundler

# VS Code Extension
#
# Name: Jekyll Run
# Id: Dedsec727.jekyll-run
# Description: Build and Run your Jekyll static website
# Version: 1.7.0
# Publisher: Dedsec727
# VS Marketplace Link: https://marketplace.visualstudio.com/items?itemName=Dedsec727.jekyll-run

bundle exec jekyll serve
