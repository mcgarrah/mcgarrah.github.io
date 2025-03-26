---
title:  "Debian 12 SystemD nightly reboots on Dell Wyse 3040s"
layout: post
published: true
---

My super lean Proxmox 8.3 testbed cluster running Ceph occasionally just decides to lockup a node based on it being incredibly limited on RAM and CPU. As much as I hate rebooting Linux/UNIX systems, this is a case where a nightly reboot of the nodes might help with reliability.

<!-- excerpt-end -->

With that in mind, these are Debian 12 based systems with SystemD. I can just drop in a quick `crontab` entry to just run a `shutdown -r now` command. Or better yet, I can add the **Nightly Reboot Service** to SystemD. I'm using this as a way to learn SystemD better and to reinforce learning the new right way to do things. So I'll end up in the final version of this post doing this with SystemD.

## Classic Crontab

First the quick & dirty way with classic `crontab`. This assumes you are running as `root` as per a usual Proxmox system.

```shell
root@pve1:~# crontab -e
```

You may be prompted for your preferred editor. I am comfortable in both `vi` and `nano`. Pick your poison.

```crontab
# minute hour dayOfMonth Month dayOfWeek commandToRun
# m  h   dom mon dow  command
1    2   *   *   *    /usr/sbin/shutdown -r now
```

You will have a reboot at 2:01AM every day. I have included two lines of comments to help understand the values for the single uncommented line. Determine if your system is using UTC or local time. My particular system is using US Eastern timezone. In a production environment, I usually use UTC consistently for log aggrevation to work.

Another lesson is to always use fully qualified paths for your commands being run by a cron job. In Debian 12, the `/usr/sbin/` is correct for this and not the classic UNIX `/sbin/`. You can always check using the `which` command as so...

```shell
root@pve1:~# which shutdown
/usr/sbin/shutdown
```

Debian 12 uses a merged root `/` and `/usr`. [The Debian /usr Merge](https://wiki.debian.org/UsrMerge) where `/lib`, `/sbin` and `/bin` are symlinks to `/usr/lib`, `/usr/sbin` and `/usr/bin`. I learned this hard way when I migrated my `/usr` to new disk earlier this year... and watched everything break badly.

Savey folks will wonder by I have not also considered using the `/etc/cron.daily/` method. This mechanism does not have sufficient timer controls to be useful for my use-case of rebooting off hours and at different times of night for each node. I do not want all three nodes down at the same time.

Now to move past legacy methods. Let's play with SystemD.

## SystemD Scheduled Service

We are creating two files for SystemD. They will create a service and a timer for the service.

This is the command to create the service file.

```shell
root@pve1:~# nano /etc/systemd/system/nightly-reboot.service
```

```ini
[Unit]
Description=Scheduled Nightly Reboot

[Service]
Type=oneshot
ExecStart=/usr/bin/systemctl --force reboot
```

To learn more about the above file use `man systemd.unit` for the generic unit file and run `man systemd.service` for details on the `service` section.

Next we are creating the timer or schedule piece for the above service.

```shell
root@pve1:~# nano /etc/systemd/system/nightly-reboot.timer
```

```ini
[Unit]
Description=Nightly Reboot Scheduling

[Timer]
OnCalendar=*-*-* 2:01:00
RandomizedDelaySec=300

[Install]
WantedBy=multi-user.target
```

To learn more about the above file use `man systemd.unit` for the generic unit file and run `man systemd.timer` for details on the `timer` section.

You are setting up a `timer` to go off after 2:01AM with a randomized delay of 5 minutes every day which runs the `nightly-reboot.service`.

## Verify the files

Run these two commands against the above files to check for syntax issues.

```shell
systemd-analyze verify /etc/systemd/system/nightly-reboot.service
systemd-analyze verify /etc/systemd/system/nightly-reboot.timer
```

The results for a Proxmox 8.3 system running Ceph returns these warnings. You can ignore them. Anything else is likely a typo or issues I missed.

```shell
root@pve1:~# systemd-analyze verify /etc/systemd/system/nightly-reboot.service 
/lib/systemd/system/ceph-volume@.service:8: Unit uses KillMode=none. This is unsafe, as it disables systemd's process lifecycle management for the service. Please update the service to use a safer KillMode=, such as 'mixed' or 'control-group'. Support for KillMode=none is deprecated and will eventually be removed.
/lib/systemd/system/ceph-volume@.service:8: Unit uses KillMode=none. This is unsafe, as it disables systemd's process lifecycle management for the service. Please update the service to use a safer KillMode=, such as 'mixed' or 'control-group'. Support for KillMode=none is deprecated and will eventually be removed.
/lib/systemd/system/ceph-volume@.service:8: Unit uses KillMode=none. This is unsafe, as it disables systemd's process lifecycle management for the service. Please update the service to use a safer KillMode=, such as 'mixed' or 'control-group'. Support for KillMode=none is deprecated and will eventually be removed.
/lib/systemd/system/ceph-volume@.service:8: Unit uses KillMode=none. This is unsafe, as it disables systemd's process lifecycle management for the service. Please update the service to use a safer KillMode=, such as 'mixed' or 'control-group'. Support for KillMode=none is deprecated and will eventually be removed.
```

```shell
root@pve1:~# systemd-analyze verify /etc/systemd/system/nightly-reboot.timer 
/lib/systemd/system/ceph-volume@.service:8: Unit uses KillMode=none. This is unsafe, as it disables systemd's process lifecycle management for the service. Please update the service to use a safer KillMode=, such as 'mixed' or 'control-group'. Support for KillMode=none is deprecated and will eventually be removed.
/lib/systemd/system/ceph-volume@.service:8: Unit uses KillMode=none. This is unsafe, as it disables systemd's process lifecycle management for the service. Please update the service to use a safer KillMode=, such as 'mixed' or 'control-group'. Support for KillMode=none is deprecated and will eventually be removed.
/lib/systemd/system/ceph-volume@.service:8: Unit uses KillMode=none. This is unsafe, as it disables systemd's process lifecycle management for the service. Please update the service to use a safer KillMode=, such as 'mixed' or 'control-group'. Support for KillMode=none is deprecated and will eventually be removed.
/lib/systemd/system/ceph-volume@.service:8: Unit uses KillMode=none. This is unsafe, as it disables systemd's process lifecycle management for the service. Please update the service to use a safer KillMode=, such as 'mixed' or 'control-group'. Support for KillMode=none is deprecated and will eventually be removed.
```

## Reload daemons

Reload daemon so new files are part of the system.

```shell
root@pve1:~# systemctl daemon-reload
```

## Enable and Start

Enable and Start the `timer` service.

```shell
root@pve1:~# systemctl enable nightly-reboot.timer
Created symlink /etc/systemd/system/multi-user.target.wants/nightly-reboot.timer → /etc/systemd/system/nightly-reboot.timer.
```

```shell
root@pve1:~# systemctl start nightly-reboot.timer
```

## Make sure Timer is running

Verify the `timer` is actually active and running.

```shell
root@pve1:~# systemctl list-timers nightly-reboot
NEXT                        LEFT          LAST PASSED UNIT                 ACTIVATES             
Wed 2025-03-26 02:04:57 EDT 4h 32min left -    -      nightly-reboot.timer nightly-reboot.service

1 timers listed.
Pass --all to see loaded but inactive timers, too.
```

## Denouement

Now to wait and see if this works tonight and then set it up on the 2nd and 3rd nodes at 3am and 4am. I believe the restarts will help with some of the memory and cpu pressures on the individual nodes and rebalance workloads. We will see but it just feels wrong to reboot a UNIX based system. :)
