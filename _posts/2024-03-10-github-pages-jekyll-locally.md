---
title:  "Running Github Pages locally"
layout: post
published: true
---

How to run Github Pages locally in my Microsoft Windows 10 Pro [WSLv2](https://learn.microsoft.com/en-us/windows/wsl/about) [Ubuntu 22.04 LTS](https://ubuntu.com/desktop/wsl) environment and using [Visual Studio Code](https://code.visualstudio.com/) to modify the contents. I'm not a [Ruby](https://www.ruby-lang.org/) or [Jekyll](https://jekyllrb.com/) expert by any means but just wanted a quick guide on running my Github Pages website locally to review them before pushing to [this website](https://mcgarrah.org). Seemed like an easy enough thing but there were a couple of hiccups to sort out so thought I'd write them down for future me when I try this again.

This should also lets me test out new plugins, new versions and changes to templates without breaking the public website. I'm still sorting out how to do the abstracts and formatting of the archive pages correctly.

<!-- excerpt-end -->

### Get Ruby

```console
➜  mcgarrah.github.io git:(feature/jekyll-plugins) ✗ sudo apt install ruby-full
```

### Install Bundler

```console
➜  mcgarrah.github.io git:(feature/jekyll-plugins) ✗ sudo gem install bundler   
```

### Install GHP dependencies locally rather than into global OS libraries

```console
➜  mcgarrah.github.io git:(feature/jekyll-plugins) ✗ bundler install --binstubs --path vendor  
```

This creates a ```./vendor``` and ```./bin``` in the local directory rather than install them into the OS libraries. It also had to be run twice to get it to work correctly in one environment. Looks like a newer bundler version resolves the issue for the second run.

I've not used RVM [Ruby Version Manager](https://rvm.io/) to manage the Ruby version which I'll leave for a later. I'm a fan of Python3 VirtualEnv and would like to see the Ruby equivalent.

### Run local Server (and fail)

```console
➜  mcgarrah.github.io git:(feature/jekyll-plugins) ✗ bundle exec jekyll serve
```

FAILED with non-specific error.

### Run local server with debug tracing

So I turned on more detailed debug tracing

```console
➜  mcgarrah.github.io git:(feature/jekyll-plugins) ✗ bundle exec jekyll serve --trace
...
/home/mcgarrah/Github/mcgarrah.github.io/vendor/ruby/3.0.0/gems/jekyll-4.2.2/lib/jekyll/commands/serve/servlet.rb:3:in `require': cannot load such file -- webrick (LoadError)
...
```

### Add missing library

Found a note in the MacOS Homebrew section about a missing library which is the same one *webrick*. So if you are on Ruby 3.0 or higher be aware it does not come with Webrick by default... so I had to install it.

```console
➜  mcgarrah.github.io git:(feature/jekyll-plugins) ✗ bundler add webrick
```

### Run local server

Try running it again

```console
➜  mcgarrah.github.io git:(feature/jekyll-plugins) ✗ bundle exec jekyll serve
```

### Success

Now I see the website on localhost port 4000 ```http://127.0.0.1:4000/```. It updates when I change files as well.

My local machine has a copy of my [Github Pages repository](https://github.com/mcgarrah/mcgarrah.github.io) and I'm using VS Code to modify the raw Markdown files and manage the git check-ins.

Running the server with "```--trace```" gave some insight into some out of date gem libraries as a bonus. I hope to use this to improve the website incrementally and adding a local copy makes it possible without public embarassments.

I'd call this a win.

## Reference

* [Testing your GitHub Pages site locally with Jekyll](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/testing-your-github-pages-site-locally-with-jekyll?platform=linux)
* [GitHub Pages documentation](https://docs.github.com/en/pages)

Cheers from the Beach
