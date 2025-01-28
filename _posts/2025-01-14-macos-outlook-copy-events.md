---
title:  "MacOS Outlook Calendar Copy Events"
layout: post
tags: technical macos outlook calendar
published: false
---

The direct Copy/Paste of an event is no longer offered in Outlook on the Mac. This may also impact Windows users but I don’t have access to test it out.

This functionality was intentionally removed by Microsoft for reasons mentioned in their post.

https://support.microsoft.com/en-us/office/outlook-blocks-copying-meetings-with-copying-meetings-is-not-supported-4baaa023-2199-4833-b7ac-d9f0715d50f1

There is another method that was not obvious that does the same thing.

"\assets\images\macos-outlook-copy-paste-calendar-event-001.png"
"\assets\images\macos-outlook-copy-paste-calendar-event-003.png"
"\assets\images\macos-outlook-copy-paste-calendar-event-002.png"

<!-- excerpt-end -->

## How to

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
