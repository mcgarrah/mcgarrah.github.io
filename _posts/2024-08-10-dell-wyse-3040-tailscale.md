---
title:  "Tailscale on Dell Wyse 3040 with Debian 12"
layout: post
published: true
---

I have been using the [Dell Wyse 3040](https://www.parkytowers.me.uk/thin/wyse/3040/) as awesome little systems for my [Tailscale](https://tailscale.com/) nodes in my multiple joint homelab networks. These systems are super low power consuming and physically small enough to just plug and go. Truly, deploying a WireGuard®-based VPN solution could not be any easier. I have four of these units connecting my homelab networks across three geographically diverse locations.

<!-- excerpt-end -->

## Debian 12 on Dell Wyse 3040

For this install I will assume you have read the earlier post [Debian 12 on Dell Wyse 3040s](/dell-wyse-3040-debian12/) as this is were I started out for each of the Tailscale nodes for a base Debian 12 installation. You will need to fix the power down issue and have these units network capable and updated.

- I also in the BIOS set these up to automatically startup every night at 2:00am in case they shutdown.
- I also in the BIOS configure them to always Power-On after restart.
- I have also found that setting a 5-second delay in the BIOS bootup seems to help them as well.

I would recommend you also update your CMOS battery maybe using the post [Dell Wyse 3040 CMOS CR2032 Battery Replacement](/dell-wyse-3040-cmos-battery/) to make sure the units stay up and running.

## Tailscale Account

You will need to setup a [Tailscale login](*https://login.tailscale.com/) for your Tailnet. This will be important later when connecting your newly installed system to your account. The steps are not terribly difficult.

## Tailscale Install

Most of this is from [Tailscale Download & Install](https://tailscale.com/download/linux) and the Tailscale excellent documention. I've included my experience and leaving you how I setup my systems.

### Update Debian

First make sure you are current on your Debian installation.

```console
sudo apt update && sudo apt dist-upgrade
```

After the update and upgrade, you should reboot your system so everything is current.

Install your dependencies

```console
sudo apt install curl vim -y
```

### Install Tailscale

Install Tailscale client

```console
curl -fsSL https://tailscale.com/install.sh | sh
```

You will need the `sudo` password.

Start the service up and register it with your Tailscale Account.

```console
sudo tailscale up
```

You will see a URL

```console
mcgarrah@wyse3040-ral~$ sudo tailscale up

To authenticate, visit:

        https://login.tailscale.com/a/20b0b2c502ab03

```

Web browser authentication and connection of new node to your Tailnet account.

[![tailscale authenticate](/assets/images/tailscale-001.png "tailscale authenticate"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/tailscale-001.png){:target="_blank"}

[![tailscale authenticate](/assets/images/tailscale-002.png "tailscale authenticate"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/tailscale-002.png){:target="_blank"}

[![tailscale authenticate](/assets/images/tailscale-003.png "tailscale authenticate"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/tailscale-003.png){:target="_blank"}

After connecting the console will show "Success." and the new node Tailnet IP address and DNS entry.

```console
mcgarrah@wyse3040-ral~$ sudo tailscale up

To authenticate, visit:

        https://login.tailscale.com/a/20b0b2c502ab03

Success.

My new node is:
wyse3040-ral.tailca1b2.ts.net
100.118.211.111

```
## Configure Tailscale

These are some steps post-installation that I've standardized for my systems that might be useful for you.

### Setup automatic updates and immediately update

```console
sudo tailscale set --auto-update
sudo tailscale update --yes
```

### Configure Tailscale Subnet Router

Enabled the Debian networking features to allow for using Tailscale relay nodes and exit nodes. Even if you don't use these options in Tailscale, it does not hurt to have this enabled.

#### Enable IP Forwarding

```console
echo 'net.ipv4.ip_forward = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf
```

#### Verify no Firewall or UFW

If you configured your system per my post [Debian 12 on Dell Wyse 3040s](/dell-wyse-3040-debian12/), then you should have no firewalls enabled. Otherwise you should check [Connect to Tailscale as a subnet router
](https://tailscale.com/kb/1019/subnets#connect-to-tailscale-as-a-subnet-router) for details on how to test and setup Firewall services.

#### Advertise Subnets

Here is an example of advertising my private subnet networks in two test locations using the command line. Your subnets will be different depending on your network configuration.

```console
sudo tailscale up --advertise-routes=192.168.1.0/24
sudo tailscale set --accept-routes

sudo tailscale up --advertise-routes=192.168.2.0/24
sudo tailscale set --accept-routes
```

#### Key Expiry

> If the device you added is a server or remotely-accessed device, you may want to consider disabling key expiry to prevent the need to periodically re-authenticate.

[KB - Key Expiry](https://tailscale.com/kb/1028/key-expiry) has details on the keys that expire periodically. I would recommend you disable the key expiration or have a scheduled rotation so you don't look access to a remote location. I every so often will rotate the keys when I have physical access to the location with the node in case something goes wrong on the rotation.

There is no command line method to update or manage the keys that I can find. This requires the WebUI in Tailscale on a per machine basis.

Default rotation is 180 days on a new Tailnet so I was caught flat-footed and had to cycle each one after they went offline.

## Considerations

The Dell Wyse 3040 has a built in 1Gbps NIC port. If that is limiting and you are fortunate enough to have an ISP service faster than 1Gbps, you can use the single USB3.0 port to provide a 2.5Gbps USB NIC.

So far the Intel Atom 2-core CPU has not been a limiting factor even under heavy network loads.

The 2Gb of RAM also not been a factor but I'm not doing anything but Tailscale on the units.

I am not exploiting all the features or capabilities of the Tailscale software so YMMV as you use more features. So far so good for me however.

## References

I highly recommend the [Official Tailscale Youtube Channel](https://www.youtube.com/@Tailscale) to learn more. It is an excellent resource for more advanced features.

*[ISP]: Internet Service Provider which is a company that provides customers access to the internet.
*[Gbps]: Gigabits per second is a unit of measurement for data transfer rate. Typically used to describe internet speed or the capacity of network connections.
*[BIOS]: Basic Input/Output System, is a type of firmware that is embedded in a computer motherboard and is responsible for starting up the system.
*[CMOS]: Complementary Metal-Oxide-Semiconductor - A CMOS chip stores the settings like date & time, fan speed, booting sequence.
*[NIC]: Network Interface Card is a component of a computer that connects it to the network.
