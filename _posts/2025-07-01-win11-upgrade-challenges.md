---
title: "Windows 11 Upgrade Challenges on ThinkPad T480"
layout: post
categories: [technical, hardware]
tags: [thinkpad, t480, windows11, webcam, performance]
published: true
---

Upgrading to Windows 11 on my ThinkPad T480 laptops turned into a performance nightmare with some unexpected solutions.

<!-- excerpt-end -->

## The Setup

I maintain two (2) ThinkPad T480 laptops as my daily drivers - a redundancy strategy born from experience and healthy paranoia. You can read about my [ThinkPad](/tags/thinkpad/) journey in previous posts. Having multiple mostly identical systems lets me test major changes on one before committing to the others. My wife also has a third T480 that she just wants to work.

For the Windows 11 upgrade, I started with the first laptop (Thomas) which seemed fine after a few days of light usage. Encouraged by this success, I upgraded the second laptop (Dresden) which has more demanding usage - video conferencing with a Logitech C930e webcam, more complex development tool configuration, and heavier multitasking.

## The Performance Disaster

Dresden's performance after the Windows 11 upgrade was catastrophically bad:

- Basic operations had painful lag and stuttering
- MS Teams, VSCode, and Google Docs became unusably slow
- System wide stuttering with constant micro-hangs
- Logitech C930e microphone completely non-functional
- Intermittent Webcam initialization failures in MS Teams
- Logitech Webcam hanging video for a few seconds

Interestingly, Thomas didn't exhibit these same severe issues, suggesting hardware-specific or configuration-dependent problems.

## Solutions Found

### Webcam and Microphone Issues

The Logitech C930e problems required multiple steps:

1. **Uninstall and reinstall Logi Tune software** - This fixed the microphone issue but video performance remained poor
2. **Update webcam firmware and drivers** - Minimal improvement
3. **MS Teams compatibility issues persist** - Video and audio performance in Teams remains suboptimal

*Note 1*: After the below changes to "Balanced", the webcam video is still not fully usable but significantly better. The  integrated camera and microphone work fine if the Logitech is unplugged.

*Note 2*: Removing the [Amazon Basics powered USB 3.0 hub](https://www.amazon.com/dp/B00DQFGH80) seems to have fixed the last of the video performance issues.

### Snipping Tool Performance

Windows 11's new Snipping Tool defaults cause significant slowdowns. The fix:

1. Open Snipping Tool settings
2. **Disable** "Automatically save screenshots"
3. **Enable** "Ask to save edited screenshots"

This prevents the tool from automatically processing and saving every screenshot, dramatically improving responsiveness.

Reference: [Microsoft Community discussion](https://answers.microsoft.com/en-us/windows/forum/all/snipping-tool-slowness-after-upgrading-to-win-11/274bcb53-d4b4-44dc-8b10-137c678e5310)

This made taking screenshots from lagging and hanging to workable again. This issue is likely exacerbated by the fact Dresden is hooked up to two external 4k monitors driving 4096x2160 x 2 pixels. This wasn't a problem under Windows 10 Pro but likely involved in the different between Thomas and Dresden laptops.

### Power Management Counterintuitive Fix

The most surprising discovery was with Windows 11's power settings:

**Path:** `Settings > System > Power & Battery > Power Mode`

CounterIntuitively, **"Best Performance" mode performed worse than "Balanced" mode** on the T480. Switching to "Balanced" provided significant performance improvements across all applications.

This suggests Windows 11's "Best Performance" mode may be poorly optimized for older hardware or creates thermal throttling issues on the T480's thermal design. I have not dug into this issue deeply just benefitted from finding it.

## Lessons Learned

- Windows 11 performance varies significantly between identical hardware configurations
- Default settings in Windows 11 are not always optimal, even for performance-focused modes
- Peripheral software (like Logi Tune) may need complete reinstallation rather than updates
- The new Snipping Tool's auto-save feature creates unnecessary system load
- Perfectly find USB 3.0 hub fails under Windows 11

## Current Status

After implementing these fixes, Dresden is usable but still not as smooth as it was on Windows 10. The webcam situation is resolved. I'm somewhat flummoxed but this seems like something that I'll just keep digging until I fix it all. Thomas is still a bit more snappy but the different is less horrible.

Hope this helps someone else if you are dealing with Logitech hardware, or the screenshot tool lag causes you issues, or you find yourself wondering why "Balanced" is better.
