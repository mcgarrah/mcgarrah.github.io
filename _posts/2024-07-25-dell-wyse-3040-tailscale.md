---
title:  "Tailscale on Dell Wyse 3040 with Debian 12"
layout: post
published: false
---

These have been awesome little guys for Tailscale nodes in my joint networks. Super low power and small enough to just plug and go.

## Debian 12 on Wyse 3040

You will need to read the earlier post [Debian 12 on Dell Wyse 3040s](/dell-wyse-3040-debian12/) as this is were I started out for each of the Tailscale nodes for a base Debian 12 installation. You will need to fix the power down issue and have these units network capable and updated.

I also generally in the BIOS set these up to automatically startup at 2:00am in case they shutdown.
I also configure them to always Power-On after restart.
Setting a 5-second delay on BIOS startup seems to help them as well.

## Tailscale install

[Tailscale on Debian 12 with Wyse 3040](https://docs.google.com/document/d/1hh4MRKJUzw_5WS3MmALou0zgU7uNoSleq9m0pZ3wYT8/edit#heading=h.6eaexts4fhl8)