---
title:  "HP ProCurve 2800 initial setup"
layout: post
published: true
---

## Get access to switch console

You will need a console serial cable to get into your HP ProCurve 2800 switch.

[![HP ProCurve 2810-24 Console Cable](/assets/images/ProCurve-2810-24G-console-cable.jpg){:width="35%" height="35%"}](/assets/images/ProCurve-2810-24G-console-cable.jpg){:target="_blank"}

Here is the one I bought from Amazon [OIKWAN - USB Cisco Console Cable, USB to RJ45 Console Cable](https://www.amazon.com/dp/B07RFLKJ54?&_encoding=UTF8&tag=mcgarrah-20&linkCode=ur2&linkId=f6db60a50d79fb1d22c8e3190d1e4d80&camp=1789&creative=9325) which has been useful on some other project as well. I have a break out for the RJ45 to let me use this on an old BlackArmor NAS and to interface with some robotics equipment. You mileage may vary but this one works great for me.

This is the ProCurve 2810-24 that is all 1Gbps ports with four SFP (not SFP+) ports that you can use with fiber or DACs. I bought three of these so I have a SAN and two home networks... then I picked up another one as a spare because it was less than $25 on eBay. So I'm all in on this switch for my home networks.

[![HP ProCurve 2810-24 Front View](/assets/images/ProCurve-2810-24G-front-view.jpg){:width="50%" height="50%"}](/assets/images/ProCurve-2810-24G-front-view.jpg){:target="_blank"}




Getting plugged in and accessing the console requires some patience.

[![HP ProCurve 2810-24 Power on with Cable](/assets/images/ProCurve-2810-24G-power-on-console.jpg){:width="50%" height="50%"}](/assets/images/ProCurve-2810-24G-power-on-console.jpg){:target="_blank"}

The FTDI Driver is built into Microsoft Windows 10 if you do a Windows Update or go into Device Manager and select upgrade driver. This took a reboot for it to take effect for my Windows 10 Pro 64-bit install. You then have to wait a bit and it will show up.  Find the COM port number... mine was COM8.

PuTTY is your friend on Windows once you get the COM port up. I've used it for years and it seems to handle anything you push at it.

[![PuTTY Serial Console](/assets/images/ProCurve-PuTTY-Serial-Console.png){:width="50%" height="50%"}](/assets/images/ProCurve-PuTTY-Serial-Console.png){:target="_blank"}

Setting the COM port to 115200 baud rather than 9600... makes thing just go faster. The console can detect 9600 or the 115200 but will not automatically switch once it starts a session.

To do a hard reset of the switch and clear the passwords. Just a reset does not clear the management password to enter "enable" mode.  Dual paper clips are necessary to do the password clearing. In the above picture with the paperclips, click the image, to see a larger version with a hole or "reset" and "clear" that both have to be depressed at the same time during a startup. Below is a link to the documenation for this process.

[Reset ProCurve 2800 Password](https://community.hpe.com/t5/aruba-provision-based/default-password-hp-procurve-switch-2824/m-p/4237025/highlight/true#M7628)

After the clear/reset you should have a console session that has both passwords cleared and you have full access to the switch. All five of my switches still had their enabled passwords set and had to be cleared this way.

## Basic setup of switch
```
NO default password is set when the switch is new.

The default configuration is quit simple:

One default Vlan (Vlan1) with IP DHCP enabled on this Vlan, and it has 2 users built in: Manager & Operator with NO password set but you can configure other user names (Optional).

If you have a password already set on this switch, and you have physical access to the switch,
press and hold the Clear button (on the front of the switch) for a minimum of one second to clear all password protection.

You can also use the Reset button together with the Clear button (Reset+Clear) to restore the factory default configuration for the switch. To do this:
1. Press and hold the Reset button.
2. While holding the Reset button, press and hold the Clear button.
3. Release the Reset button and wait for about one second for the Self-Test LED to start flashing.
4. When the Self-Test LED begins flashing, release the Clear button

This process restores the switch configuration to the factory default settings.
```

Press enter twice on the serial terminal to get the automatic serial detect to engage...

NOTE: I set in Windows Device Manager the COM8 port to be 115200 baud rather than the default 9600 to make it snappier.  Dunno if that can be made automatic or if the COM port is hard wired during setup.

```
ProCurve J9021A Switch 2810-24G
Software revision N.11.15

Copyright (C) 1991-2008 Hewlett-Packard Co.  All Rights Reserved.

                           RESTRICTED RIGHTS LEGEND

 Use, duplication, or disclosure by the Government is subject to restrictions
 as set forth in subdivision (b) (3) (ii) of the Rights in Technical Data and
 Computer Software clause at 52.227-7013.

         HEWLETT-PACKARD COMPANY, 3000 Hanover St., Palo Alto, CA 94303

We'd like to keep you up to date about:
  * Software feature updates
  * New product announcements
  * Special events

Please register your products now at:  www.ProCurve.com




Press any key to continue
```

So that has me on the serial console and able to get to the __enabled__ mode so I can set DHCP or manually set the IP address of the switch. I'm also digging around for the firmware to see about upgrading the most current options available.

```
SAN Procurve 2810-24G                                       1-Jan-1990   2:20:28
==========================- CONSOLE - MANAGER MODE -============================
                                  Switch Setup

  System Name : SAN Procurve 2810-24G
  System Contact : Michael McGarrah mcgarrah@gmail.com
  Manager Password : ********           Confirm Password : ********
  Logon Default : CLI                   Time Zone [0] : 0
  Community Name : public               Spanning Tree Enabled [No] : No

  Default Gateway :
  Time Sync Method [None] : TIMEP
  TimeP Mode [Disabled] : Disabled

  IP Config [DHCP/Bootp] : Manual
  IP Address  : 10.10.10.10
  Subnet Mask : 255.255.254.0


 Actions->   Cancel     Edit     Save     Help

Enter System Name - up to 25 characters.
Use arrow keys to change field selection, <Space> to toggle field choices,
and <Enter> to go to Actions.
```

Setting the time/date from CLI
```
SAN Procurve 2810-24G   > enable
Password: ********
SAN Procurve 2810-24G   # configure
SAN Procurve 2810-24G   (config)# time
Mon Jan  1 02:30:32 1990
SAN Procurve 2810-24G   (config)# exit
SAN Procurve 2810-24G   # show time
Fri Feb  9 15:21:23 2024
SAN Procurve 2810-24G   # exit
SAN Procurve 2810-24G   >
```

Setting up SNTP

```
SAN Procurve 2810-24G   > enable
Password: ********
SAN Procurve 2810-24G   # setup
SAN Procurve 2810-24G                                       1-Jan-1990   2:26:48
==========================- CONSOLE - MANAGER MODE -============================
                                  Switch Setup

  System Name : SAN Procurve 2810-24G
  System Contact : Michael McGarrah mcgarrah@gmail.com
  Manager Password : ********           Confirm Password : ********
  Logon Default : CLI                   Time Zone [0] : 0
  Community Name : public               Spanning Tree Enabled [No] : No

  Default Gateway :
  Time Sync Method [None] : SNTP
  SNTP Mode [Disabled] : Unicast        Server Address : 10.10.10.11
  Poll Interval (sec) [720] : 720       Server Version [3] : 3
  IP Config [DHCP/Bootp] : Manual
  IP Address  : 10.10.10.10
  Subnet Mask : 255.255.254.0


 Actions->   Cancel     Edit     Save     Help

SAN Procurve 2810-24G   # show sntp

 SNTP Configuration

  Time Sync Mode: Sntp
  SNTP Mode : Unicast
  Poll Interval (sec) [720] : 720


  IP Address       Protocol Version
  --------------   ----------------
  10.10.10.11      3
```

## Things left to do

I still need to set up SSH for remote access which I'll likely dig into this article [Configure SSH on HP ProCurve Switches](https://community.spiceworks.com/how_to/2403-configure-ssh-on-hp-procurve-switches) to get this done.

Updating the firmware to the latest requires getting access to the firmware SWI/BIN files. That can be done if you have an HP Enterprise account with [this link](https://h10145.www1.hpe.com/downloads/SoftwareReleases.aspx?ProductNumber=J9021A) or [this link](https://asp.arubanetworks.com/downloads;search=J9021A). I was unable to get either working so far even with setting up a linkage to Aruba Networks.

I have some copies of older router/switch firmwares that I'm looking into hosting and verifying on one of my switches in a future post.

I also want to get the Java WebUI working but this is locked out because of Java Webstart being deprecated in almost every browser in existence. I found a method to do this relatively safely that I'll post on later.

## Documentation

For my ProCurve 2810 switches I have a list of PDFs documentation well worth grabbing and keeping around as references as these are extremely complex and powerful devices.
* [Quick Installation Guide](https://ftp.hp.com/pub/networking/software/2810-QIG-June2006-59913844.pdf)
* [Installation and Getting Started Guide](https://ftp.hp.com/pub/networking/software/2810-Install-May2006-59913843.pdf)
* [Management and Configuration Guide](https://ftp.hp.com/pub/networking/software/2810-MgmtCfg-July2007-59914732.pdf)
* [Advanced Traffic Management Guide](https://ftp.hp.com/pub/networking/software/2810-AdvTrafficMgmt-July2007-59914733.pdf)
* [Access Security Guide](https://ftp.hp.com/pub/networking/software/2810-Security-July2007-59914734.pdf)
* [Release Notes: Version N.11.04 Software](https://ftp.hp.com/pub/networking/software/2810-RelNotes-N1104-59916273.pdf) (thru N.11.04 release)

## Reference

* [HP ProCurve switches](https://github.com/jarleven/NetworkHOWTO/blob/master/Switch/HPProCurve.md)
