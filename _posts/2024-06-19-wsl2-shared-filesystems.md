---
title:  "How to share file systems betwen multiple WSL2 instances"
layout: post
published: false
---

I have a huge amount of investment in my WSLv2 [Ubuntu 22.04.3 LTS](https://www.microsoft.com/store/productId/9PN20MSR04DW?ocid=pdpshare) installation. It has my nvidia GPU setup nicely and several machine learning demos and tests I've built and use for learning.  With [Ubuntu 24.04 LTS](https://www.microsoft.com/store/productId/9NZ3KLHXDJP5?ocid=pdpshare) released, I now want to play around in the newer version but don't want to move my entire set of models and repositories across. I have well over 500Gb of content and don't want two copies.

You can use Windows Explorer to copy between the two WSLv2 instances and I did a bit of that while moving some small custom bits between the two linux instances. It was super easy to do but misses the direct sharing that I'd like to do between them especially for larger files and repos.

[PICTURE]

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

I personally use the [easyWSL](https://www.microsoft.com/store/productId/9NHBTMKS47RB?ocid=pdpshare) utility from the Microsoft Store to do this with a Windowed GUI. You can also retrieve it from [Github easyWSL](https://github.com/redcode-labs/easyWSL) as well. I'm surprised it isn't on Chocolatey. You also have to install the .NET Desktop Runtimes 6.0.3+ x64 which are a dependency of easyWSL and I did that using Chocolatey.

``` shell
C:\> choco install dotnet-6.0-desktopruntime
```

[PICTURE]

Restart the distro using the easyWSL "Stop distro" for each one and you should see both the file systems between the instances of WSLv2 after restarting them.
