---
title:  "PhotoSynth Export and Visualizer"
layout: post
categories: technical
---

I have developed something interesting for my graduate class in Computations Photography for the final project. 
As background, for the class we had an assignment in which we used the [Microsoft Photosynth](https://en.wikipedia.org/wiki/Photosynth) service to generate a 3D walkthru of an area by uploading several hundred photographs.
On the back-end the Photosynth web service does feature extraction on all the photos and then related the photos in three dimensions to each other and the feature points. This generated a point cloud of related points between the photos.

![PhotoSynth](/assets/images/PhotoSynthPointCloud.png){:width="50%" height="50%"}

What I found most interesting was the 3D data in one of the views they offered shown above. So working with this 3D data is what I picked for my final project in the class.

{% include embed.html url="https://www.youtube.com/embed/WZPtuNnaqVc" width="50%" height="50%" %}

Above is the demonstration of the working project code against two of the Photosynth projects. I fully extract the data from the web service and put it into a common format then introduce that data into an interactive visualization environment. Extracting the raw binary data from the web service, then decoding the binary data and putting it into a standard useful format was a challenge.

Here is the link to my online slideshow presentation for the [Final Project](https://github.com/mcgarrah/PyPhotoSynthExport/blob/master/McGarrah_JMichael_Portfolio.pdf).

The python code for the project is available at my GitHub [PyPhotoSynthExport](https://github.com/mcgarrah/PyPhotoSynthExport) project for those interested.

The project stretched me in several ways with decoding binary files, learning some strange SOAP and JSON interfaces, digging into some visualization library code and basically learning about 3D space.

I’m glad we had a final project and that I picked the one that I did.
