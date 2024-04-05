---
title:  "HP ProCurve Switch Java WebUI"
layout: post
published: false
---

The earlier post [HP ProCurve 2800 initial setup](/procurve-2800-switches/) discussed an initial setup of a network switch and mentioned in passing that I got the Java WebUI working in a relatively safe manner.

Basically, the HP ProCurve switches had a convenient web interface that used [Java Webstart](https://en.wikipedia.org/wiki/Java_Web_Start) in a browser to give you an interactive method to look at your switch status and update minor settings. The webui was never as powerful as the full console CLI but just a nice feature when debugging a network issue.

My first thoughts were to build a Windows 7 Virtual Machine with that era of web browser and java installed and use it to access the switches. That seemed like a lot of work, was resource intensive and prone to issues cropping up with an old unsupported OS. Thus entered the [PortableApps](https://portableapps.com/) idea to run a isolated local Web-browser and Java.



## History

So now for some related history. Back in the early Internet there were a limited number of webbrowsers.  Netscape which later became FireFox was one the major players. They had a plugin system for their web-browser called [Netscape Plugin Application Programming Interface (NPAPI)](https://en.wikipedia.org/wiki/NPAPI) that you could use to enable things like [Macromedia Flash](https://en.wikipedia.org/wiki/Adobe_Flash), [Sun Java](https://en.wikipedia.org/wiki/Java_(software_platform)) before Oracle, [Microsoft Silverlight](https://en.wikipedia.org/wiki/Microsoft_Silverlight) and other such extensions to the browser. This NSAPI capability was in most web-browsers until around 2015-2017 when it was removed due to security concerns. Other methods to handle support for custom content types evolved and became broadly supported.

HP ProCurve switches implemented a webui using Java Webstart that requires the Java Runtime Engine in the web-browser. This is the [Java Webstart](https://en.wikipedia.org/wiki/Java_Web_Start) requirement that led us down this rabbit hole of an older web-browser and older Java Runtime that supports these switches webui. I have picked FireFox as the web-browser due to familiarity with it and the JRE version is dictated by what supports FireFox and Java Web Start. I want the last version of each piece of software that had support to run the webui.

**WARNING**: It should go without saying that you should not use the FireFox Web Browser we are setting up here for the very old Java Web App on the public internet. You will be <ins>***hacked***</ins> without a doubt in seconds.

## Download Software

[Java Portable](https://sourceforge.net/projects/portableapps/files/Java%20Portable/) and make sure to get the 32-bit version not the 64-bit version. To match the era with support for JNLP (Java Webstart) I picked Java 8 Update 121. Also picked due to MD5 signing issues with later versions.

[Mozilla Firefox, Portable Ed.](https://sourceforge.net/projects/portableapps/files/Mozilla%20Firefox%2C%20Portable%20Ed./) and they are bundled for both 32-bit and 64-bit. The last version that supports JNLP (Java Webstart) are either Firefox 51.0 or 51.0.1. I have only tested with 51.0 so far. You must enable 32-bit only.

* [FirefoxPortable_51.0.1_English.paf.exe](https://sourceforge.net/projects/portableapps/files/Mozilla%20Firefox%2C%20Portable%20Ed./Mozilla%20Firefox%2C%20Portable%20Edition%2051.0.1/FirefoxPortable_51.0.1_English.paf.exe/download) ([local](/assets/exes/FirefoxPortable_51.0.1_English.paf.exe))
* [FirefoxPortable_51.0_English.paf.exe](https://sourceforge.net/projects/portableapps/files/Mozilla%20Firefox%2C%20Portable%20Ed./Mozilla%20Firefox%2C%20Portable%20Edition%2051.0/FirefoxPortable_51.0_English.paf.exe/download) ([local](/assets/exes/FirefoxPortable_51.0_English.paf.exe))
* [jPortable_8_Update_121.paf.exe](https://sourceforge.net/projects/portableapps/files/Java%20Portable/jPortable_8_Update_121.paf.exe/download) ([local](/assets/exes/jPortable_8_Update_121.paf.exe))

## Setup




Getting the WebUI up and running is a very nice to have feature if I can get a web browser capable of Java Web Start (NPAPI) JNLP... And this [Web Browsers supporting NPAPI plugins like JAVA](https://www.reddit.com/r/homelab/comments/11afd0p/comment/k5j47cr/?utm_source=share&utm_medium=web2x&context=3) link seems to be a good starting point.




My first thoughts ran along the lines of a Windows 7 Pro virtual machine to run a really old version of the web browser but this seemed like a pile of work and prone to issues coming up. So I thought about PortableApps and remembered they had both Java and FireFox as supported applications. With that in mind, I started down the road to figuring out if this would work or not. Surprise, it worked but had a number of hurdles along the way that need documentation for future folks.



https://portableapps.com/node/58831
    If security is not an issue, and I recall correctly, some older versions were distributed complete and not as online installers. So you might be able to find what you want in the older files:
    https://sourceforge.net/projects/portableapps/files/


PortableApps FireFox 51.0 NSAPI enabled version...
    https://sourceforge.net/projects/portableapps/files/Mozilla%20Firefox%2C%20Portable%20Ed./

Get the 32-bit versions as I pulled the 64-bit for both FireFox and JPortable which will not work.
Note, there is only a 32/64 version of FireFox and you have to set a flag to only use the 32-bit version.
Java on the other hand is 32 or 64-bit downloads

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
    Notes: It should be noted that Adobe Flash does *not* officially support running in any portable configuration. And, as it is a closed source application, we can neither modify it nor package it into a more portable-friendly installer. It should also be noted that it is illegal to redistribute either flash or shockwave without the full installer. -->


<!-- From above:
    EDIT: I got it working. Somehow the "Enable Java content in the browser" box wasn't checked in the Security tab of the Java Control Panel, and also I needed to have the port number along with the URL in the Exception Site List.

    Here is the Java Control Panel from a PortableApp Installation of JPortable
    "C:\PortableApps\CommonFiles\Java\bin\javacpl.exe"

    Open and pick the third tab "Security" then the checkbox at the top "Enable Java content in the browser (Only disabled for this user)" needs to be checked.

    I also added my URL of the switch by IP address to the Exception Site List as:
        http://10.10.10.10 -->

[![HP ProCurve 2810-24 Serial Console in PuTTY](/assets/images/hp-procurve-serial-console-putty.png){:width="50%" height="50%"}](/assets/images/hp-procurve-serial-console-putty.png){:target="_blank"}

[![HP ProCurve 2810-24 Java Web Start WebUI in FireFox](/assets/images/hp-procurve-java-web-start-jnlp-webui-in-firefox.png){:width="50%" height="50%"}](/assets/images/hp-procurve-java-web-start-jnlp-webui-in-firefox.png){:target="_blank"}

[![FirefoxPortable.ini](/assets/images/firefox-jnlp-ini-file.png){:width="35%" height="35%"}](/assets/images/firefox-jnlp-ini-file.png){:target="_blank"}

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

Lines 10 and 15,16 are the lines to be changed in the file. This file was placed in my ```C:\PortableApps\FirefoxPortable``` directory next to the ```FirefoxPortable.exe``` file. I installed all my PortableApps into ```C:\PortableApps```

[![FirefoxPortable Files](/assets/images/firefox-jnlp-file-location.png){:width="35%" height="35%"}](/assets/images/firefox-jnlp-file-location.png){:target="_blank"}

You will need to run the Java Control Panel to enable
```C:\PortableApps\CommonFiles\Java\bin```

[![Firefox Java Portable Files](/assets/images/firefox-java-cpl-location.png){:width="35%" height="35%"}](/assets/images/firefox-java-cpl-location.png){:target="_blank"}

You have to check the "Enable Java content in the browser" box in the Security tab of the Java Control Panel, and also have to add the port number along with the URL in the Exception Site List.

    Here is the Java Control Panel from a PortableApp Installation of JPortable
    "C:\PortableApps\CommonFiles\Java\bin\javacpl.exe"

    Open and pick the third tab "Security" then the checkbox at the top "Enable Java content in the browser (Only disabled for this user)" needs to be checked.

    I also added my URL of the switch by IP address to the Exception Site List as:
        http://10.10.10.10


[![Firefox Java Control Panel settings](/assets/images/firefox-java-cpl-security.png){:width="35%" height="35%"}](/assets/images/firefox-java-cpl-security.png){:target="_blank"}

Those settings are stored in the text file at ```C:\Users\<username>\AppData\LocalLow\Sun\Java\Deployment\security\exception.sites``` if you need to populate it with a longer list of IP Addresses. The star (*) format is untested. I've only tested with the "http://10.10.10.10" address entered.

# References

* [Java error with the HP ProCurve 2510-24 J9019B network switch web interface](https://superuser.com/questions/1787945/java-error-with-the-hp-procurve-2510-24-j9019b-network-switch-web-interface)
* [Managing old Java switches?](https://www.reddit.com/r/sysadmin/comments/17a6jrg/managing_old_java_switches/)
* [Accessing legacy webpages requering NPAPI Java plugin](https://github.com/jarleven/NetworkHOWTO/blob/master/Java.md)
* [ProCurve Switch J9021A needs Java](https://www.reddit.com/r/homelab/comments/11afd0p/procurve_switch_j9021a_needs_java/)

