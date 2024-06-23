---
title:  "Rsync on Black Armor NAS 110"
layout: post
categories: personal black_armor hack nas rsync seagate
---

I figured out something simple but neat on the Black Armor NAS 110 (BA-NAS110) device.  It has ```rsync``` a powerful file-system replication tool from UNIX.

Caveats are that in order to do this you must have root on the device and a ssh connection with the command line. I'll write a friendly doc on how to get 'root' later. (Just search for Hajo Noerenberg's work on the subject sans the friendly write up if you want to do it now.)

So, the BA-NAS110 is capable of using ```rsync``` from the command line to replicate its data to another NAS or Linux system if you have root on the system. Getting it setup was simple enough but knowing that the ```rsync``` daemon and client were on the systems was the trick.

You have to create a rsyncd.conf file since there isn't one pre-built. Syntax is common to the typical rsync 3.0.4 version.

<!-- excerpt-end -->

Hosting system
```
$ id
(root)
$ cat /root/rsyncd.conf

pid file = /var/run/rsyncd.pid


[rsyncftp]
path = /shares/Public
comment = rsyncftp

$ rsync --daemon --config=/root/rsyncd.conf
```

Client system (could be another BA-NAS110 or Linux)
```
$ id
(root)
$ rsync --progress --stats -v -t -r rsync://admin@/rsyncftp/* /shares/Public
```
  ... watch the good times roll ...

*Note*: Add the "-n" option to rsync on the client side for the initial test connection to put it in test mode without data copy.  Remove "-n" when you actually want to copy data.

The transfer speed between two BA-NAS110 devices across a dedicated switch is about 6-8MB/s. I've read some comments about performance on these devices being dogs and that there tweaks that might help.

I don't have my toolchain setup for compiling native apps yet but getting all my data copied out of my old device to my new one was a pretty important step to playing around with the older one.  So I figured someone else might benefit from this bit of lore.
