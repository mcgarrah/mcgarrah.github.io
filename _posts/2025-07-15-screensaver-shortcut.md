---
title: "Start the Windows screensaver with a Shortcut"
layout: post
categories: [technical]
tags: [windows, screensaver]
published: true
---

After my Windows 11 upgrade, I have a need for a quick way to start my screensaver but not lock my computer. So the Windows-L (lock) is not a desired options for this use-case. I want to quickly get back to my screen without logging back in.

I remember an old Windows NT tool and built-in MacOS feature called "Hot Corners" that let me do this by shoving my cursor to a corner of the screen. But I don't want to load another tool for this. I'm using Power Toys "Mouse without Border" to link up a couple machines with virtual KVMs so the hot corners isn't an option because of that.

So how do I solve this?

<!-- excerpt-end -->

## Creating a Desktop Shortcut for Screensaver

1. **Locate a screensaver file**: Screensavers are usually in `C:\Windows\System32`. Navigate there with your file explorer. You can pick any ScreenSaver with an SCR extension. I picked `C:\Windows\System32\scrnsave.scr` so it just blanks my screen. You pick any SCR directly such as `Bubbles.scr`, `PhotoScreensaver.scr`, `Mystify.scr`, `Ribbons.scr`, or `ssText3d.scr`.
2. **Create a shortcut**: Right-click the screensaver file you picked above, and select "Send to > Desktop (create shortcut)". You may have to click "Show more options" to find the "Send to >" option.
3. **Assign a shortcut**: Right-click the shortcut on your desktop, select "Properties", go to the "Shortcut" tab and click the "Shortcut key" field. Press your desired key combo (e.g., Ctrl-Alt-S).
4. **Optional**: "Change Icon" button to change your icon to something memorable and change the "Run" option to "Minimized" to keep it from flashing.

This serves my purposes of quickly blanking my screens but as quickly come back with a mouse bump. If I wait too long, system lock timeout will engage and then I have to log back in.

Posting just in case somebody could use this.
