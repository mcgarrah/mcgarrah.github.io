---
title:  "Cygwin Ports by way of binary files"
layout: post
categories: personal cygport cygwin programming reverse_engineering
---

## Binary Files

I wanted to do some work on an undocumented binary file format. The free [HexEdit](http://www.catch22.net/software/hexedit) tool for Windows from [Catch22 Software](http://www.catch22.net/) is a pretty good for mapping data structures to the raw binary/hex data in a file.  It uses the C format struct to format the data structures into a human readable format.  It could use some additional docs on how to use the typedef format but was relatively easy to figure out.

What was frustrating was finding a tool that would allow for doing binary diffs with a decent interface.  There are several methods for doing binary diffs on files.  The unix 'od' command, 'bvi' and others presented themselves but were not as interactive as I would like when looking at large numbers of files visually for iterative small changes. Editors and Binary Editors fall into an area of preferences. I could be entering a flame-war picking a tool but would love to hear some feedback on tools people have used.

What I found that seemed to fit the bill for me was Chris' excellent tool called **vBinDiff** found at his [website](http://www.cjmweb.net/vbindiff/). Since I wanted to use UNIX tools for scripted automation but still be on a Windows system, I installed Cygwin.  Getting vbindiff to work on Cygwin was a testament to Chris' excellent code base.  After finishing up and getting it working, I thought it might be nice to package it for the Cygwin project.

## Cygports

Thus started my journey into [Cygport](http://cygwinports.blogspot.com/).  I found myself frustrated with the documentation for the assumption that I knew a lot about the Cygwin packaging which is what I was trying to avoid by using the tool. This is not a bashing session for cygport which does an amazing job of wrapping up lots of the trivia that is Cygwin packaging.  What was missing is a basic "HowTo Package ABC" for Cygwin.  The cygport documents while good are written for someone who had done the manual process of packaging at some point.  The documentation failed to meet my expectations as a competent developer who has done lots of porting work to quickly introduce me to this new means of packaging for their platform.  There is not quick guide on the simple cases with a couple of interesting example.  The other lack was how to get these example applications of varied type out of Cygwin easily.  I figured it out and afterwards felt silly for not having seen it.  All that said, I have come the realization that I have to put some time aside and try to write an HowTo guide on packaging for Cygwin.

I've got two packages done so far.  vBinDiff is the first and I am still polishing that install as I learn more along the way. vbindiff is currently working great as a package on my local system. Wy60 is another tool from years back when I worked on UniData/Universe systems and needed access to their Wyse 60 PICK interfaces. This makes for two packages and I have used several features to make these work.  I'll have to learn how to submit a request for inclusion into the main Cygwin package group.  There is a mailing list and a set of questions to answer.  I'll just need to put some time aside for it. :)

## Interests 

So those are my current interests in the world of technology.  I keep playing around with the BlackArmor NAS devices occasionally and would like to find the time to get the USB to serial interface setup on my second unit. The ARM gcc tool-chain languishes for lack of time as well. The DLNA server ended up being too much of a pain without a decent tool-chain so I knuckled under and installed Microsoft Media Center on an old laptop to feed my digital media to my xbox360. I really want to revisit that particular issue and get a low-power digital media server working.  Maybe I'll find the time and pick those back up.
