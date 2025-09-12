---
title:  "MacOS Outlook Calendar Copy Events"
layout: post
categories: [technical, reference]
tags: [macos, outlook, calendar, productivity, microsoft]
published: true
---

The Copy/Paste of an Event in the Outlook Calendar is no longer offered and cut off without much notice. I can confirm this in Outlook on the Mac as of 4Q-2024. This appears to also impact Windows users but they have a registry workaround to re-enable it. This is not a bug but functionality that was intentionally removed by Microsoft for reasons mentioned in their post below.

[Outlook blocks copying meetings with “Copying meetings is not supported.”](https://support.microsoft.com/en-us/office/outlook-blocks-copying-meetings-with-copying-meetings-is-not-supported-4baaa023-2199-4833-b7ac-d9f0715d50f1)

This change drove me insane as I historically used calendar events to track my work and export it for hour accounting against projects. Using [Tempo with Jira](https://www.tempo.io/) integration made this even easier. Before this change, I would just copy some work event from earlier and move it to a new time that had my project code and description of the project. It was a massively convenient piece of my workflow.

So, deep breath, I finally found another method to make copies of Events that was not obvious.

<!-- excerpt-end -->

## How to Copy/Paste an Event on MacOS

[![macOS Touch ID dialog](/assets/images/macos-outlook-copy-paste-calendar-event-001.png "macOS Touch ID dialog"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/macos-outlook-copy-paste-calendar-event-001.png){:target="_blank"}

If you Ctrl-Click an Event/Meeting, you get the above popup menu. Select the "Move", then select "Copy to Folder..." and you will be prompted for which Calendar to copy the Event. You can see the popup below.

[![macOS Touch ID dialog](/assets/images/macos-outlook-copy-paste-calendar-event-002.png "macOS Touch ID dialog"){:width="35%" height="35%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/macos-outlook-copy-paste-calendar-event-002.png){:target="_blank"}

You now have an exact copy of your Event in your Calendar that is ready to be modified.

[![macOS Touch ID dialog](/assets/images/macos-outlook-copy-paste-calendar-event-003.png "macOS Touch ID dialog"){:width="35%" height="35%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/macos-outlook-copy-paste-calendar-event-003.png){:target="_blank"}

## Enable Copy/Paste for Events on Windows

I do not have a Windows machine to test this so this is provided without any review. Copy this text into a file called `EnableMeetingCopy.reg`, save it and then double click the file. This will import the change into the registry. This is supposed to work.

``` registry
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\Microsoft\Office\16.0\Outlook\Options\Calendar]
"EnableMeetingCopy"=dword:00000001
```
