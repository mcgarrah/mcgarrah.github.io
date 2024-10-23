---
title:  "HP ProCurve Switch Java WebUI"
layout: post
published: false
---

> "Don't bury the lede"

A working HP ProCurve Java WebUI screenshot to showing that I got it working.

[![ProCurve WebUI](/assets/images/hp-procurve-java-web-start-jnlp-webui-in-firefox.png "ProCurve Java WebUI"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/hp-procurve-java-web-start-jnlp-webui-in-firefox.png){:target="_blank"}

My earlier post [HP ProCurve 2800 initial setup](/procurve-2800-switches/) discussed an initial configuration of a network switch and mentioned in passing that I got the ProCurve Java WebUI working in a relatively safe manner. Here is how I put that together on a modern machine running Windows 10 Professional 64-bit.

<sup><sub>_**WARNING**_: It should go without saying that you should not use the FireFox Web Browser from January 2017 that we are setting up here for the very old Java Web App supported on hardware released in 2004 and EOL in 2013 on the public internet. You will be _**hacked**_ without a doubt in seconds. These are completely unpatched versions of two _very_ **very** _**very**_ old pieces of software. You have been duly warned.</sub></sup>

<!-- excerpt-end -->

## Summary

Back in the day, the HP ProCurve switches had a convenient web interface that used [Java Webstart](https://en.wikipedia.org/wiki/Java_Web_Start) in a browser to give you an interactive method to look at your switch status and update minor settings. This WebUI was never as powerful as the full console CLI but just a nice feature when debugging a network issue. It was also very useful to hand out to support folks for a quick and easy way to verify a switch or port on a switch was functional. I like quick and easy so I wanted this functionality back.

Honestly, my first thoughts were to build a Virtual Machine using a Microsoft Windows 7 installation with that era of web-browser and java installed and use it to access the switches. After some consideration that seemed like a lot of work, was resource intensive and probably prone to issues cropping up with an incredibly old and unsupported OS. Thus entered the idea to use [PortableApps](https://portableapps.com/) to run an older isolated web browser and Java.

## History (optional)

So now for some quick related history as to why we have this problem. You can safely skip down to the [Download Software](#download-software) section to avoid learning about it without any issues.

Back in the early Internet there were a limited number of web-browsers. [Netscape](https://en.wikipedia.org/wiki/Netscape) which later became [FireFox](https://en.wikipedia.org/wiki/Firefox) was one the major players. They had a plugin system for their web-browser called [Netscape Plugin Application Programming Interface (NPAPI)](https://en.wikipedia.org/wiki/NPAPI) that you could use to enable things like [Macromedia Flash](https://en.wikipedia.org/wiki/Adobe_Flash), [Sun Java](https://en.wikipedia.org/wiki/Java_(software_platform)) (before Oracle), [Microsoft Silverlight](https://en.wikipedia.org/wiki/Microsoft_Silverlight) and other such extensions to the browser. This NPAPI capability was in most web-browsers until around 2015-2017 when it was removed due to security concerns. Other methods to handle support for custom content types evolved and became broadly supported. Thus the NPAPI was depreciated leaving folks with their java apps  abandoned.

The idea behind JWS (Java Web Start) and JNLP (Java Network Launching Protocol) was to use your web browser to download a small JNLP text file and it passes the contents of the file as argument to the locally installed Java Web Start (JWS) executable. The JWS would use those JNLP file contents, download the java application along with any dependencies and fire it up. This could fire up the java application as an Applet in the web browser or as a stand alone Java Desktop Client GUI Application. For our ProCurve case, this would be the Java Applet in the web browser.

JWS initially just launched Java GUI Applications on your local machine using a local Java Runtime. Later it added support for launching java applets in web browsers. This caused lots of confusion as to what JWS was in play at any given point. More insanity ensures when you add certificate signing and MD5 signatures to various pieces of this hodge-podge.

Early versions of JWS allowed for self-signed certificates to sign your application. This was later removed and code signing certificates which costed serious money (a couple hundred USD) became a requirements for JWS. This was not a SSL/TLS certificate for your website but a code signing certificate. Those are completely separate certificates. So you Java Applet and your Java Application would both need to be signed. For fun, read up on [JKS (Java Key Stores)](https://en.wikipedia.org/wiki/Java_KeyStore) if you have a chunk of free time. I was an expert at this at one time and blessedly no longer need to know it unless supporting very old software.

HP ProCurve switches implemented a WebUI using Java Webstart that requires the Java Runtime Engine installed in the web-browser. This is the [Java Webstart](https://en.wikipedia.org/wiki/Java_Web_Start) requirement that led me down this rabbit hole of an older web-browser and older Java Runtime that supports these switches WebUI. I picked FireFox as the web-browser due to familiarity with it and the JRE version is dictated by what supports FireFox and Java Web Start. I want the last version of each piece of software that had support to run the WebUI.

## Download Software {#download-software}

You will need to download two pieces of software. A specific version of **Firefox Portable Edition** with NPAPI support and **Java Portable** that is supported in that web-browser. I have pulled copies locally and have links to where I pulled them for your inspection.

Here is the link to [Java Portable](https://sourceforge.net/projects/portableapps/files/Java%20Portable/) general download website. You will need the 32-bit version and _not_ the 64-bit version. To match the era with support for JNLP (Java Webstart) I picked "Java 8 Update 121". Also there is an issue with MD5 signing issues with later versions of Java to contend with which also impacts the 64-bit versions.

Here is the link to [Mozilla Firefox, Portable Ed.](https://sourceforge.net/projects/portableapps/files/Mozilla%20Firefox%2C%20Portable%20Ed./) general download website and they are bundled for both 32-bit and 64-bit. The last version that supports JNLP (Java Webstart) are either Firefox 51.0 or 51.0.1. I have tested with 51.0 and 51.0.1 and both seem to work fine. You **must** enable 32-bit only or this will fail to work.

For the directly links to the versions you need:

* Direct Download Link --> [FirefoxPortable_51.0.1_English.paf.exe](https://sourceforge.net/projects/portableapps/files/Mozilla%20Firefox%2C%20Portable%20Ed./Mozilla%20Firefox%2C%20Portable%20Edition%2051.0.1/FirefoxPortable_51.0.1_English.paf.exe/download) (and [local copy](/assets/exes/FirefoxPortable_51.0.1_English.paf.exe))
* Direct Download Link --> [jPortable_8_Update_121.paf.exe](https://sourceforge.net/projects/portableapps/files/Java%20Portable/jPortable_8_Update_121.paf.exe/download) (and [local copy](/assets/exes/jPortable_8_Update_121.paf.exe))

<!-- * [FirefoxPortable_51.0_English.paf.exe](https://sourceforge.net/projects/portableapps/files/Mozilla%20Firefox%2C%20Portable%20Ed./Mozilla%20Firefox%2C%20Portable%20Edition%2051.0/FirefoxPortable_51.0_English.paf.exe/download) ([local](/assets/exes/FirefoxPortable_51.0_English.paf.exe)) -->

<!--

Firefox-ESR 52.7.3 (32-bit)
Oracle Java Version 8 Update 231

Extended Support Release (check these for support)
https://sourceforge.net/projects/portableapps/files/Mozilla%20Firefox%2C%20Portable%20Ed./Mozilla%20Firefox%20ESR%2C%20Portable%20Edition%2052.7.3/ *** likely works ***
https://sourceforge.net/projects/portableapps/files/Mozilla%20Firefox%2C%20Portable%20Ed./Mozilla%20Firefox%20ESR%2C%20Portable%20Edition%2052.7.4/
https://sourceforge.net/projects/portableapps/files/Mozilla%20Firefox%2C%20Portable%20Ed./Mozilla%20Firefox%20ESR%2C%20Portable%20Edition%2052.8.0/

https://sourceforge.net/projects/portableapps/files/Java%20Portable/jPortable_8_Update_231_online.paf.exe/download *** likely works with 52.7.3 ***
-->

Pull down copies of these two files to your local system someplace you can find them to install in the next steps.

_**Note**_: There is something called the "Extended Support Release (ESR)" of Firefox that claimed to maintain support for plugins thru "Firefox-ESR 52.7.3 (32-bit)" along with "Oracle Java Version 8 Update 231" version that might also be supportable but I have not tested them.

## Install Software

Install the Firefox web browser first then follow with the Java Portable installation. Doing this in that order configures everything correctly. The other way you will encounter issues.

### Firefox install

Using the above downloaded files, install the "Mozilla Firefox, Portable Ed. version 51.0.1" on your local Windows system. I used all defaults.

[![procurve image](/assets/images/procurve-webui-install-001.png "procurve image"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/procurve-webui-install-001.png){:target="_blank"}

[![procurve image](/assets/images/procurve-webui-install-002.png "procurve image"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/procurve-webui-install-002.png){:target="_blank"}

Notice that I changed my default install location from `"C:\Users\<username>\Downloads\Firefox_51.0.1_Portable"` to `"C:\PortableApps\FirefoxPortable"`. This is helpful later.

[![procurve image](/assets/images/procurve-webui-install-003.png "procurve image"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/procurve-webui-install-003.png){:target="_blank"}

[![procurve image](/assets/images/procurve-webui-install-004.png "procurve image"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/procurve-webui-install-004.png){:target="_blank"}

[![procurve image](/assets/images/procurve-webui-install-005.png "procurve image"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/procurve-webui-install-005.png){:target="_blank"}

This is the installed Firefox that I have setup at this point.

### Java Portable install

Using the above downloaded files, install the "Java Portable 32-bit version 8 update 121" on your local Windows system. I used all defaults.

[![procurve image](/assets/images/procurve-webui-install-011.png "procurve image"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/procurve-webui-install-011.png){:target="_blank"}

[![procurve image](/assets/images/procurve-webui-install-012.png "procurve image"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/procurve-webui-install-012.png){:target="_blank"}

[![procurve image](/assets/images/procurve-webui-install-013.png "procurve image"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/procurve-webui-install-013.png){:target="_blank"}

[![procurve image](/assets/images/procurve-webui-install-014.png "procurve image"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/procurve-webui-install-014.png){:target="_blank"}

Default if you used above will be `C:\PortableApps\CommonFiles\Java`.

[![procurve image](/assets/images/procurve-webui-install-015.png "procurve image"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/procurve-webui-install-015.png){:target="_blank"}

[![procurve image](/assets/images/procurve-webui-install-016.png "procurve image"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/procurve-webui-install-016.png){:target="_blank"}

[![procurve image](/assets/images/procurve-webui-install-017.png "procurve image"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/procurve-webui-install-017.png){:target="_blank"}

These are now installed but not a fully configured useful Java at this point.

**Note**: In my testing, using the 64-bit versions did not work for something related to MD5 signed Java deployments. Use the 32-bit configuration and versions to reproduce my results.

## Configure Software

You should have two installed PortableApps: `CommonFiles/Java` and `Firefox`. The next two sections will describe what we are doing to each and then a detailed set of steps for each.

---

To confirm the Firefox installation you should see something that looks like below.

[![procurve image](/assets/images/procurve-webui-install-005.png "procurve image"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/procurve-webui-install-005.png){:target="_blank"}

We will be adding the file `C:\PortableApps\FirefoxPortable\Other\Source\FirefoxPortable.ini` to the location `C:\PortableApps\FirefoxPortable\` next to the `FirefoxPortable.exe` file and modifying it to run only in 32-bit mode and allow multiple instances of Firefox to run.

---

To confirm the Portable Java installation you should see something like this below.

[![procurve image](/assets/images/procurve-webui-install-017.png "procurve image"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/procurve-webui-install-017.png){:target="_blank"}

You will run the Java Control Panel to configure for enabling java in the web browser and the website or IP address of switch allowed to run java applications.

---

### FirefoxPortable Configuration

<!-- 
Java plugin doesn't work in Firefox Portable
https://portableapps.com/node/57250

    I need to access a corporate application that has a web interface and a Java applet.

    I read that Firefox 52 and later don't allow the Java plugin anymore. So I installed Firefox Portable 51.0.1 into C:\users\username\Downloads\Firefox_51.0.1_Portable\FirefoxPortable. Then I copied the FirefoxPortable.ini file from the Other\Source directory and put it in the same directory as FirefoxPortable.exe. I edited the file to have the following:

```
    AllowMultipleInstances=true
    AlwaysUse32Bit=true
```

    Then I read that Java 8u131 and later don't allow MD5 signed jar files which the corporate application uses. So I installed the 32-bit version of JPortable 8u121 into C:\Users\username\Downloads\Firefox_51.0.1_Portable\CommonFiles\Java. (followed the instructions at https://portableapps.com/support/firefox_portable#plugins)

    I launched FirefoxPortable.exe, and checked the Tools->Add-ons->Plugins, and I saw that it had the Java(TM) Platform SE 8 U121 plugin. Looks like I installed everything correctly.

    But when I go to https://www.java.com/verify/ and click on "Verify Java Version" to make sure the Java plugin is working, it says "Detecting Java on your computer" and "The Java detection app will ask for permission to run. Click Run to allow the verification process to continue. Depending on your system settings, you may need to respond to prompts to allow the verification to continue."

    But it doesn't prompt me at all. After about 2 minutes, it finally says:

    "We are unable to verify if Java is currently installed and enabled in your browser."

    I also went into the Java Control Panel, to the Security tab, made sure "High" was selected, and then added "https://www.java.com/" into the Exception Site List, but that didn't help.

    EDIT: I got it working. Somehow the "Enable Java content in the browser" box wasn't checked in the Security tab of the Java Control Panel, and also I needed to have the port number along with the URL in the Exception Site List.
-->

<!--
Installing Plugins (Java, Flash, Shockwave, etc.)
https://portableapps.com/support/firefox_portable#plugins

    Installing Plugins (Java, Flash, Shockwave, etc.)
    Note that all plugins except Flash require Firefox to run in 32-bit mode, which you can force with AlwaysUse32Bit. Like many browsers, Firefox will be dropping support for all plugins except Flash by the end of 2016.

    With Firefox Portable, plugins work a bit differently than they do in regular Firefox. Here's how to do some of the most common plugins:

    Java Runtime Environment - To use Java apps with Mozilla Firefox, Portable Edition, just install jPortable alongside. If Firefox Portable is in X:\PortableApps\FirefoxPortable, jPortable should install to X:\PortableApps\CommonFiles\Java. The Firefox Portable launcher will automatically detect and configure the Java plugin for use.
    <!-- Flash Plugin - To install Flash, you can either try our easy to use Flash installer for Firefox Portable, or follow these steps:
    Flash is available as an extension. Just click the link.
    You'll probably see a yellow bar across the top of the browser (if not, skip to Step 5), on that bar, click Edit Options
    In the popup window, click Allow to add PortableApps.com to your whitelist and then click close
    Now try the link again
    You'll see a popup asking if you would like to install, click OK after the countdown and follow along the prompts
    Shockwave Plugin - To install Shockwave, follow these steps:
    Download the free Shockwave Player from the Macromedia website
    Run the installation routine and, instead of letting it install to a local browser, select to choose your browser
    Browse to X:\FirefoxPortable\App\firefox (where X is your device's driver letter) and continue with the installation
    You may need to restart Firefox Portable for the changes to take effect
    Other Plugins - Other plugin directions are coming soon...
    If the above fails, try the alternate (and more geeky) method:

    Install the plugin in a local copy of Firefox (on your hard drive)
    Locate your plugins directory (usually C:\Program Files\Mozilla Firefox\plugins\)
    Copy the plugin you need from there to your FirefoxPortable\Data\plugins directory (Some Exmaples: For Flash, copy NPSWF32.dll... for Shockwave, copy np32dsw.dll)
    Notes: It should be noted that Adobe Flash does *not* officially support running in any portable configuration. And, as it is a closed source application, we can neither modify it nor package it into a more portable-friendly installer. It should also be noted that it is illegal to redistribute either flash or shockwave without the full installer. 
-->

<!-- 
From above:
    EDIT: I got it working. Somehow the "Enable Java content in the browser" box wasn't checked in the Security tab of the Java Control Panel, and also I needed to have the port number along with the URL in the Exception Site List.

    Here is the Java Control Panel from a PortableApp Installation of JPortable
    "C:\PortableApps\CommonFiles\Java\bin\javacpl.exe"

    Open and pick the third tab "Security" then the checkbox at the top "Enable Java content in the browser (Only disabled for this user)" needs to be checked.

    I also added my URL of the switch by IP address to the Exception Site List as:
        http://10.10.10.10
-->

If your install mirrors mine with a root of `C:\PortableApps` then you can find the original file shown above in `C:\PortableApps\FirefoxPortable\Other\Source\FirefoxPortable.ini`. You will copy this file to `C:\PortableApps\FirefoxPortable` next to the `FirefoxPortable.exe` file and modify it with three changes. On lines 10 and 15, 16 modify the file to match entries to comment out `#AllowMultipleInstances=false` and add the two lines for `AllowMultipleInstances=true` and `AlwaysUse32Bit=true`.

[![FirefoxPortable Files](/assets/images/firefox-jnlp-file-location.png){:width="55%" height="55%"}](/assets/images/firefox-jnlp-file-location.png){:target="_blank"}

[![FirefoxPortable.ini](/assets/images/firefox-jnlp-ini-file.png){:width="35%" height="35%"}](/assets/images/firefox-jnlp-ini-file.png){:target="_blank"}

<details>
<summary>Click to see fully INI file</summary>
{% highlight ini linenos %}
[FirefoxPortable]
FirefoxDirectory=App\firefox
ProfileDirectory=Data\profile
SettingsDirectory=Data\settings
PluginsDirectory=Data\plugins
FirefoxExecutable=firefox.exe
AdditionalParameters=
LocalHomepage=
DisableSplashScreen=false
# AllowMultipleInstances=false
DisableIntelligentStart=false
SkipCompregFix=false
RunLocally=false

AllowMultipleInstances=true
AlwaysUse32Bit=true

# The above options are explained in the included readme.txt
# This INI file is an example only and is not used unless it is placed as described in the included readme.txt
{% endhighlight %}
</details>

<!-- With Jekyll 4.4 we have mark_lines available -->
<!--
{% highlight ini linenos mark_lines="10 15 16" %}
[FirefoxPortable]
FirefoxDirectory=App\firefox
ProfileDirectory=Data\profile
SettingsDirectory=Data\settings
PluginsDirectory=Data\plugins
FirefoxExecutable=firefox.exe
AdditionalParameters=
LocalHomepage=
DisableSplashScreen=false
# AllowMultipleInstances=false
DisableIntelligentStart=false
SkipCompregFix=false
RunLocally=false

AllowMultipleInstances=true
AlwaysUse32Bit=true

# The above options are explained in the included readme.txt
# This INI file is an example only and is not used unless it is placed as described in the included readme.txt
{% endhighlight %}
-->

### Java Portable Configuration

Again, if your install mirrors mine with a root of `C:\PortableApps` then you will find the Java Control Panel in `C:\PortableApps\CommonFiles\Java\bin` and you will open the file `javacpl.exe`.

[![Firefox Java Portable Files](/assets/images/firefox-java-cpl-location.png){:width="35%" height="35%"}](/assets/images/firefox-java-cpl-location.png){:target="_blank"}

You have to check the "Enable Java content in the browser" box in the Security tab of the Java Control Panel, and also have to add the port number along with the URL in the Exception Site List.

    Here is the Java Control Panel from a PortableApp Installation of JPortable
    "C:\PortableApps\CommonFiles\Java\bin\javacpl.exe"

    Open and pick the third tab "Security" then the checkbox at the top "Enable Java content in the browser (Only disabled for this user)" needs to be checked.

    I also added my URL of the switch by IP address to the Exception Site List as:
        http://10.10.10.10

[![Firefox Java Control Panel settings](/assets/images/firefox-java-cpl-security.png){:width="35%" height="35%"}](/assets/images/firefox-java-cpl-security.png){:target="_blank"}

Those settings are stored in the text file at ```C:\Users\<username>\AppData\LocalLow\Sun\Java\Deployment\security\exception.sites``` if you need to populate it with a longer list of IP Addresses. The star (*) format is untested. I've only tested with the "http://10.10.10.10" address entered.

## Working Interface

| ![Java WebGUI](/assets/images/hp-procurve-java-web-start-jnlp-webui-in-firefox.png) | ![Serial Console](/assets/images/hp-procurve-serial-console-putty.png) |
|:--:|:--:|
| Java WebGUI | Serial Console |

Pick your poison. I happen to like having both options available. The serial console has all the options and is easy to repeat the steps with code. The WebUI gives you a quick visual of what is happening and for some operations a quick way to make changes.

## Things I could have tried

Try a modern or open source JWS called [OpenWebStart](https://github.com/karakun/OpenWebStart). I just dodged this entirely as I could see it being a time sink. Somebody else might want to try this.

Using a Virtual Machine with an older OS and Web Browser of that era. Plenty of folks have done this in other places for applications. Heck I used this method to support a plasma injection molding system at a manufacturing job several years back. Definitely an option but more weight than I wanted.

I could also have tried using the Firefox ESR (Extended Support Release) that kept the NSAPI support longer and kept it patched up longer. As I wasn't sure of when that release dumped NSAPI support, I just avoided it in this first test.

[![HP ProCurve 2810-24 Serial Console in PuTTY](/assets/images/hp-procurve-serial-console-putty.png){:width="50%" height="50%"}](/assets/images/hp-procurve-serial-console-putty.png){:target="_blank"}

[![HP ProCurve 2810-24 Java Web Start WebUI in FireFox](/assets/images/hp-procurve-java-web-start-jnlp-webui-in-firefox.png){:width="50%" height="50%"}](/assets/images/hp-procurve-java-web-start-jnlp-webui-in-firefox.png){:target="_blank"}

## References

* [Java error with the HP ProCurve 2510-24 J9019B network switch web interface](https://superuser.com/questions/1787945/java-error-with-the-hp-procurve-2510-24-j9019b-network-switch-web-interface)
* [Managing old Java switches?](https://www.reddit.com/r/sysadmin/comments/17a6jrg/managing_old_java_switches/)
* [Accessing legacy webpages requering NPAPI Java plugin](https://github.com/jarleven/NetworkHOWTO/blob/master/Java.md)
* [ProCurve Switch J9021A needs Java](https://www.reddit.com/r/homelab/comments/11afd0p/procurve_switch_j9021a_needs_java/)
* [FireFox Portable - Installing Plugins (Java, Flash, Shockwave, etc.)](https://portableapps.com/support/firefox_portable#plugins)

*[NPAPI]: Netscape Plugin Application Programming Interface
*[JWS]: Java Web Start
*[JNLP]: Java Network Launch Protocol
*[lede]: introductory section in journalism
*[CLI]: command line interface
