---
title:  "Google Documents - copy an image"
layout: post
categories: [technical, reference]
tags: [google-docs, images, productivity, web-development]
published: true
---

Google Docs uses a URL based clipboard method to copy/cut and paste images and other media. That happens to works great between Google Docs but it completely fails when I try to take images from Google Docs to my Jekyll Posts when I need an actual image file. This is a small things but took some digging to figure it out for both Windows and MacOS.

<!-- excerpt-end -->

## Here are the step

You are forcing Google Docs to provide direct access to the image object in the web browser. I've done this with Chrome on both Windows 10 and macOS Sonoma successfully.

1. Open the Google Document with the image.

2. Double-Click the image until you get the marks on the corners and edges like this:
[![gdoc image](/assets/images/gdoc-image-copy-001.png "gdoc image"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/gdoc-image-copy-001.png){:target="_blank"}

3. Press the shift key and right-click on the image. You should get a pop-up menu like this:
[![gdoc popup](/assets/images/gdoc-image-copy-002.png "gdoc popup"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/gdoc-image-copy-002.png){:target="_blank"}
Note: For macOS press Ctrl-Shift and click on the image for the same pop-up menu.

4. Select from the pop-up menu either the "Save image as..." or the "Open in new tab".

From here, you have options on how to save the image back to the operating system file system. Be aware that the other options for "Copy image" and "Copy image address" just get the URL of the image not the actual image to the clipboard.

## Alternate way to show steps

```text
open google document
    double-click the image
        press shift + right-click the image
            "open in new tab" then save image using browser
            or
            "save image as..." to save image
```

## Fin

Hope this helps someone else in the future or me when I forget how to do this in six months.
