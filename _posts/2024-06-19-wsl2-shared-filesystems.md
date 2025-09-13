---
title:  "Sharing file systems between WSLv2 instances"
layout: post
categories: [technical, development]
tags: [wsl, windows, linux, filesystems, development, technical, troubleshooting]
published: true
---

*[WSLv2]: Windows Subsystem for Linux

I have a significant investment in my [WSLv2](https://learn.microsoft.com/en-us/windows/wsl/about) [Ubuntu 22.04.3 LTS](https://www.microsoft.com/store/productId/9PN20MSR04DW?ocid=pdpshare) installation. It has my Nvidia GPU setup nicely integrated and several machine learning demos and tests I've built and use for keeping current on machine learning.  With [Ubuntu 24.04 LTS](https://www.microsoft.com/store/productId/9NZ3KLHXDJP5?ocid=pdpshare) released, I now want to play around in the newer version but don't want to move or worse copy my entire set of models and repositories across. I have well over 500Gb of content and absolutely don't want two copies of those floating around. I'm looking for a solution to this and figure others have encountered it.

[![Explorer WSL Filesystems](/assets/images/wsl2-windows-explorer.png){:width="30%" height="30%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/wsl2-windows-explorer.png){:target="_blank"}

<!-- excerpt-end -->

The first option is that you can use Windows Explorer to copy between the two WSLv2 instances. I did a bit of that while moving some small custom bits between the two linux instances. It was super easy to do but misses the direct sharing that I'd like to do between them especially for larger files and repos.

[![Explorer WSL Filesystems](/assets/images/wsl2-windows-explorer-two-views.png){:width="50%" height="50%"}](/assets/images/wsl2-windows-explorer-two-views.png){:target="_blank"}

Enter a nifty SuperUser Stack Overflow question "[Is there a way to access files from one WSL 2 distro/image in another one?](https://superuser.com/q/1659218/247426)" and the interesting set of answers that took a couple of tries for me to get right.

Run this in both your WSL instances from the command line.

``` shell
echo "/ /mnt/wsl/instances/$WSL_DISTRO_NAME none defaults,bind,X-mount.mkdir 0 0" | sudo tee -a /etc/fstab
sudo mkdir -p /mnt/wsl/instances/$WSL_DISTRO_NAME
```

Update your ```wsl.conf``` file to delay mounting from ```/etc/fstab``` entries until ```/mnt/wsl``` is ready for the sub-mount point to occur.

``` shell
nano /etc/wsl.conf
```

``` config
[automount]
mountFsTab = false

[boot]
command = sleep 5; mount -a
systemd=true
```

At this point, you have to stop both the WSLv2 instances completely.

You can do this from a Command or Powershell console using the following command.

``` shell
C:\> wsl --shutdown
```

I personally use the [easyWSL](https://www.microsoft.com/store/productId/9NHBTMKS47RB?ocid=pdpshare) utility from the Microsoft Store to do this with a Windowed GUI. You can also retrieve it from [Github easyWSL](https://github.com/redcode-labs/easyWSL) as well. I'm super surprised it wasn't on Chocolatey. You also have to install the .NET Desktop Runtimes 6.0.3+ x64 which are a dependency of easyWSL and I did that using Chocolatey.

``` shell
C:\> choco install dotnet-6.0-desktopruntime
```

[![EasyWSL Utility](/assets/images/wsl2-windows-easywsl.png){:width="50%" height="50%"}](/assets/images/wsl2-windows-easywsl.png){:target="_blank"}

Restart the distro using the easyWSL "Stop distro" for each one and you should see both the file systems between the instances of WSLv2 after restarting them.

After restarting the WSLv2 instances, you can access across the two Ubuntu instances via the ```/mnt/wsl/instances/``` and the instance name.

``` shell
➜  ~ ls -al /mnt/wsl/instances
total 8
drwxr-xr-x  4 root root   80 Jun 21 16:42 .
drwxrwxrwt  3 root root   80 Jun 20 23:31 ..
drwxr-xr-x 19 root root 4096 Jun 21 19:06 Ubuntu-22.04
drwxr-xr-x 22 root root 4096 Jun 20 23:31 Ubuntu-24.04
```

One of the first issues you will hit is the home directory may have different UID and GID values between the two installs. So you will have to use ```sudo``` or root access to see into the file system. You can see this issue below in my two installs of Ubuntu.

``` shell
➜  ~ sudo grep mcgarrah /mnt/wsl/instances/Ubuntu-22.04/etc/passwd
mcgarrah:x:1000:1000:,,,:/home/mcgarrah:/usr/bin/zsh
➜  ~ sudo grep mcgarrah /mnt/wsl/instances/Ubuntu-24.04/etc/passwd
mcgarrah:x:1002:1002:,,,:/home/mcgarrah:/usr/bin/zsh
```

I was able to work around this for a simple check like a ```diff``` between two repositories with this command.

``` shell
➜  ~ sudo diff -r /mnt/wsl/instances/Ubuntu-22.04/home/mcgarrah/github/mcgarrah.github.io/  /mnt/wsl/instances/Ubuntu-24.04/home/mcgarrah/github/mcgarrah.github.io
```

This is not a perfect solution but it gets me closer to what I wanted. I can share the machine learning models between the two instances with decent performance. I'll likely work on getting the UID and GID synchronized between the different instances to make this work more easily.

I hope this helps someone else in my same boat as they upgrade WSLv2 instances.
