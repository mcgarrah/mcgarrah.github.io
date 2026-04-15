---
title:  "WSLv2 with Oh My Zsh"
layout: post
published: false
---

Why do I install **OMZ** on just about every system I use now? Because it just works out of the box and improves the command line experience without getting in the way. The other part of why is that I started using the iTerm2 (a terminal) in MacOS a good bit, and it defaults to **zsh** and not **bash**.

## What is "Oh My Zsh"

[Oh My Zsh](https://ohmyz.sh/#install)

[Plugins](https://github.com/ohmyzsh/ohmyzsh/wiki/Plugins)

apt install git -y
plugins=(git tmux vscode)

https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/git
https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/vscode
https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/tmux


https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/colorize
https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/debian
https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/tmux-cssh


## T480 Development Setup (Thomas)

The Thinkpad T480 "Thomas" runs WSLv2 with VSCode as a development environment. Setup includes:

- WSLv2 with Oh My Zsh (this article)
- [Chocolatey](/how-to-package-software-in-chocolatey/) for Windows package management
- nvidia MX150 GPU for AI/ML experimentation with Automatic1111 and ComfyUI

### WSLv2 APT Upgrade Known Issue

After `apt upgrade`, you may see:

```text
Processing triggers for libc-bin (2.35-0ubuntu3.6) ...
/sbin/ldconfig.real: /usr/lib/wsl/lib/libcuda.so.1 is not a symbolic link
```

This is a known WSLv2 issue with the CUDA library symlink and can generally be ignored.

### LXC/LXD Permissions Reference

TheTinkerDad has a useful but long video on LXC/LXD permissions with Docker:

- [LXC + Docker Containers + Storage - A Crash Course!](https://youtu.be/QT-WW4iczZ0?si=58myWL5dmqdRozjS)

Other relevant videos from [TheTinkerDad](https://www.youtube.com/@TheTinkerDad):

- [Video 1](https://youtu.be/CjY4-kozIkI?si=GJvK3LIkSdpgSvrQ)
- [Video 2](https://youtu.be/fYl5poBJtE4?si=pN0RG-hW7sL500wd)
- [Video 3](https://youtu.be/aaFLEdxfyOk?si=gzVWB_VQ2zYrROlC)

TODO: Consolidate the LXC/LXD permissions content from these videos into a concise cheatsheet.
