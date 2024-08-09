---
title:  "Black Armor: A ToDo List - UPS and DLNA"
layout: post
categories: personal black_armor nas seagate
---

I have two new quick projects that I need for my Black Armor NAS 110 in the immediate future.

First I need the UPS functionality for this device as I'm taking power hits at my residence and my old UPS' are just way too old and not working to keep the NAS running after a power blip. I bought an APC Back-UPS ES BE550G 550 VA 330 Watts at CostCo with one of their specials. The Black Armor NAS documentation said it only works with APC UPS so I thought I was okay but with further reading in the forums they say results vary with APC devices. So time to see if my new APC UPS will work with the built-in software or if the software needs improvements. So I hope to have a smart UPS running but just the dumb UPS functionality without a shutdown mode will have to do if I cannot get it working. The smart UPS depends on apcupsd 3.12.2 according to a post.

``` shell
$ /usr/sbin/apcupsd --version
apcupsd 3.12.2 (18 January 2006) redhat
```

Next on the list is to figure out how functional the streaming media works on the device.  This will hopefully be more straight forward than the UPS. Family time will be vastly improved if I can get the DVD collection running off this device. DLNA is an interesting subject and my BlueRay player hooked to my TV may be able to play movies off the NAS. That would be optimal.
