---
title:  "MacOS Touch ID for Sudo with TMUX and DisplayLink"
layout: post
published: true
---

This is an out of place post but I figured if setting up **Touch ID** with `sudo` on my MacBook Pro stumped me that it would cause others issues and worth a quick write up. Also worth having around when I get a new MacBook Pro in the future.

So to start, I use a MacBook Pro M2 Pro for my daily driver machine at work. It is the closest I can get to a Linux machine in the office. I end up using `sudo` frequently enough that I liked the idea of **Touch ID** rather than type a password in a dialog. I encountered a couple of hiccups along the way with `tmux`, *iTerm2* and **DisplayLink** that had to be fixed.

<!-- excerpt-end -->

## How to setup

I am copying the intent from both the *sixcolors* and Stackoverflow posts for the MacOS Sonoma. So read those posts below for more details.

``` shell
cd /etc/pam.d
sed "s/^#auth/auth/" /etc/pam.d/sudo_local.template | sudo tee /etc/pam.d/sudo_local
```

How to test and drop the cached permissions. The `-k` resets the `sudo` permissions so you are prompted for your authorization again.

```console
sudo ls
sudo -k
sudo ls
```

You should see the Touch ID then you are set.

[![macOS Touch ID dialog](/assets/images/macos-touchid-sudo.png "macOS Touch ID dialog"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/macos-touchid-sudo.png){:target="_blank"}

If you see this dialog with only a Password option then check below for more things you can do.

[![macOS Password dialog](/assets/images/macos-password-sudo.png "macOS Password dialog"){:width="25%" height="25%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/macos-password-sudo.png){:target="_blank"}

### DisplayLink

If you are using **DisplayLink** then you will need to enable permissions or you will not see the Touch ID option.

``` shell
defaults write com.apple.security.authorization ignoreArd -bool TRUE
```

### tmux

If you are using `tmux` then you need to add [pam_reattach](https://github.com/fabianishere/pam_reattach) for sessions to automatically work. The [README.md](https://github.com/fabianishere/pam_reattach/blob/master/README.md) is excellent. Using `brew` and the Apple M1 or M2 requires some additional steps they mention.

``` shell
brew install pam-reattach
```

### iTerm2

[Touch ID on Mac in iTerm](https://apple.stackexchange.com/questions/259093/can-touch-id-on-mac-authenticate-sudo-in-terminal/355880#355880) has some configuration settings that you will need to change. 
**iTerm2 -> Preferences -> Advanced -> (Goto the Session heading) -> Allow sessions** and change from "Yes" to "No".

[![macOS iTerm2 dialog](/assets/images/macos-iterm2-sudo.png "macOS iTerm2 dialog"){:width="55%" height="55%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/macos-iterm2-sudo.png){:target="_blank"}

## Reference

The excellent posts from *sixcolors* by Dan Moren

- [In macOS Sonoma, Touch ID for sudo can survive updates](https://sixcolors.com/post/2023/08/in-macos-sonoma-touch-id-for-sudo-can-survive-updates/) for macOS Sonoma and later.
- [Quick Tip: Enable Touch ID for sudo](https://sixcolors.com/post/2020/11/quick-tip-enable-touch-id-for-sudo/) before macOS Sonoma.

[Touch ID on Mac in iTerm](https://apple.stackexchange.com/a/355880) had useful information needed.

