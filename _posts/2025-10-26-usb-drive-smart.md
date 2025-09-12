---
title: "Enabling SMART Monitoring on Seagate USB Drives"
layout: post
categories: [technical, hardware]
tags: [seagate, usb, smart, monitoring, storage, linux, proxmox, homelab]
published: true
---

USB drives are notorious for hiding their SMART data behind finicky USB-to-SATA bridges. If you've ever tried to check the health of a Seagate USB drive and gotten frustrated with "unsupported field in scsi command" errors, you're not alone.

After wrestling with several Seagate drives in my homelab, I finally figured out the magic incantations needed to get SMART data working. Here's how to do it properly.

**Note**: The decision to not allow this in Linux as a default was done for a good reasons. You are playing with fire as some drives behave erratically. I have not experienced this with recently purchased USB Drives, but older ones did have quirks and issues. So buyer beware.

<!-- excerpt-end -->

## The Problem

Modern USB drives use UAS (USB Attached SCSI) which should make SMART data accessible, but many Seagate drives have quirky implementations that break standard SMART commands:

```bash
# This is what you'll see initially - frustrating!
root@poe:~# smartctl -d sat -T permissive -a /dev/sdd
Read Device Identity failed: scsi error unsupported field in scsi command

Device Model:     [No Information Found]
Serial Number:    [No Information Found]
SMART support is: Ambiguous
A mandatory SMART command failed: exiting.
```

Sound familiar? The issue is that these drives need special USB storage quirks to work properly.

## Step 1: Identify Your Seagate Drive

First, find your drive's USB vendor and product IDs:

```bash
# Check current quirks (probably empty)
cat /sys/module/usb_storage/parameters/quirks

# Find your Seagate drive IDs
lsusb -tv | grep "ID 0bc2"
```

In my case, I found several Seagate models across my cluster:
- `0bc2:ac2b` - BUP Portable drives
- `0bc2:ac41` - One Touch HDD drives  
- `0bc2:2344` - Older Expansion drives

## Step 2: Apply USB Storage Quirks

The solution is to disable UAS for these specific drives and force them to use the older USB Mass Storage protocol. Here are three methods:

### Method 1: Runtime Quirks (Temporary)

For immediate testing:

```bash
# Apply quirks immediately (lost on reboot)
echo "0bc2:ac2b:,0bc2:ac41:,0bc2:2344:" > /sys/module/usb_storage/parameters/quirks

# Verify it worked
cat /sys/module/usb_storage/parameters/quirks
```

### Method 2: Modprobe Configuration (Persistent)

For permanent changes that survive reboots:

```bash
# Create modprobe configuration
echo 'options usb-storage quirks=0bc2:ac2b:,0bc2:ac41:,0bc2:2344:' > /etc/modprobe.d/usbstorage-quirks.conf

# Rebuild initramfs
update-initramfs -u
```

### Method 3: GRUB Boot Parameters (Most Reliable)

This method works even if the modprobe approach fails:

```bash
# Create GRUB configuration
cat > /etc/default/grub.d/usb-quirks.cfg << EOF
# Override quirks for Seagate USB drives
GRUB_CMDLINE_LINUX="\$GRUB_CMDLINE_LINUX usb_storage.quirks=0bc2:ac2b:,0bc2:2344:,0bc2:ac41:"
EOF

# Update GRUB and reboot
update-grub
reboot
```

## Step 3: Verify the Fix

After applying quirks and reconnecting your drive:

```bash
# Check that quirks are active
cat /sys/module/usb_storage/parameters/quirks
# Should show: 0bc2:ac2b:,0bc2:2344:,0bc2:ac41:

# Verify drive is using usb-storage instead of uas
lsscsi -H
# Look for your drive - should show usb-storage, not uas

# Now try SMART commands
smartctl -d sat -a /dev/sdX
```

## Success! SMART Data Available

With the quirks in place, you should now see proper SMART data:

```bash
# Basic SMART info
smartctl -d sat -i /dev/sdX

# Full SMART report
smartctl -d sat -a /dev/sdX

# Health check
smartctl -d sat -H /dev/sdX
```

## Common Seagate USB Drive IDs

Here are the most common Seagate USB drive IDs that need quirks:

- `0bc2:ac2b` - BUP Portable series
- `0bc2:ac41` - One Touch HDD series
- `0bc2:2344` - Expansion Portable (older)
- `0bc2:ac25` - Some Backup Plus models

If you have a different model, use `lsusb` to find your specific vendor:product ID.

## My Multi-Node Setup

Across my Proxmox cluster, I found these Seagate drives:

- **harlan**: `0bc2:ac41` (One Touch HDD)
- **kovacs**: Multiple drives including `0bc2:ac41`, `0bc2:ac2b`, and `0bc2:2344`
- **poe**: `0bc2:ac2b` (BUP Portable)

Using the GRUB method, all nodes now have working SMART monitoring on their USB drives.

## Understanding Quirk Flags

The quirk string format is `vendor:product:flags`. Common flags:
- `u` - Ignore UAS (USB Attached SCSI)
- `t` - Ignore TRIM commands  
- Empty (`:`) - Disable UAS completely

For SMART access, we typically want empty flags to force USB Mass Storage mode.

## Troubleshooting Tips

1. **Still getting errors?** Try unplugging and reconnecting the drive after applying quirks
2. **Multiple methods not working?** Some drives need the `-T permissive` flag: `smartctl -d sat -T permissive -a /dev/sdX`
3. **Performance concerns?** USB Mass Storage is slower than UAS, but the difference is minimal for monitoring
4. **Persistent issues?** Check `dmesg` for USB errors after connecting the drive

## Why This Matters

USB drives fail without warning. Having SMART data means you can:

- Monitor drive health proactively
- Set up alerts for failing drives
- Plan replacements before catastrophic failure
- Include USB drives in your monitoring stack

In my homelab, I use these drives for backup storage and media serving. Being able to monitor their health is crucial for maintaining data integrity.

## References

- [Karssen's blog post](https://blog.karssen.org/2022/05/19/getting-smart-information-from-a-seagate-expansion-portable-drive/) - Original inspiration
- [smartmontools wiki](https://www.smartmontools.org/wiki/SAT-with-UAS-Linux) - Technical details
- [r/DataHoarder discussion](https://www.reddit.com/r/DataHoarder/comments/nc392f/how_can_i_read_the_smart_data_of_a_16_tb_seagate/) - Community solutions

Now go forth and monitor those USB drives properly! Your future self will thank you when you catch a failing drive before it takes your data with it.