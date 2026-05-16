---
title:  "Powerline Networking for the Homelabs"
image: /assets/images/og/powerline-networking.png
layout: post
categories: [technical, networking]
tags: [networking, powerline, homelab, hardware, troubleshooting]
excerpt: "Powerline networking repeatedly tripped the AFCI breakers in a modern house — turns out arc fault interrupters and powerline adapters are fundamentally incompatible."
description: "Why Netgear Powerline 500 adapters fail in modern homes with AFCI breakers. Covers the IEEE 1901 standard, how AFCI breakers detect powerline network traffic as arc faults and trip the circuit, and why this only manifests when the second adapter starts negotiating — making the root cause non-obvious."
published: true
last_modified_at: 2025-09-11
seo:
  type: BlogPosting
  date_published: 2024-10-11
  date_modified: 2025-09-11
---

I inherited, from a stack of old junk hardware, two [Netgear Powerline 500 Nano XAVB5101](https://www.netgear.com/support/product/xavb5101/) plugs. I thought I would try it out for a quick network connection between two floors in my new house using the existing power cabling.

[![Powerline NIC](/assets/images/powerline-networking-01.png "Powerline NIC"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/powerline-networking-01.png){:target="_blank"}

Wow did I learn a lesson in a combination of networking and electrical power the hard way... with a repeatedly blown breaker.

<!-- excerpt-end -->

[Powerline](https://en.wikipedia.org/wiki/Power-line_communication#Home_networking_(LAN)) was an [IEEE 1901 standard](https://en.wikipedia.org/wiki/IEEE_1901) for pushing network traffic over power cables in a household. It filters the power signals to remove electrical noise that can affect performance. The claim is that it can push gigabit ethernet over those cables. I vaguely remembered these being around but never had a need for them. The issue is that Powerline does not work in most modern houses like mine. There are two updated standards for interrupting power when something bad happens.

An **arc fault circuit interrupter** (AFCI) breaker protects against electrical fires by detecting dangerous electrical leaks, or arcing faults, in the branch circuit wiring. AFCIs sense when electricity is leaking and shut it off before it can overheat.

A **ground fault circuit interrupter** (GFCI) breaker protects against electrical shocks by shutting off electricity when it detects a ground fault. GFCIs are especially important in wet areas of the home.

So AFCI prevents fires from damaged electrical wiring along with tripping when grounding events happen and classic GFCI prevents shocking a person who is grounded like in a bathroom with a wet floor touching a live electric circuit. AFCI has become a mainstay in new construction at least in my part of the country (USA).

Why does this matter? Because AFCI breakers are sensitive to Powerline extra noise and will often trip seeing that extra line noise as an arc or break in the line. If you have older breakers with GFCI then likely Powerline networking works just fine for you.

The behavior is such that you only see the issue after you plugin the second adapter. The first adapter will run and boot up just fine. You only start getting the blown AFCI breaker when the actual network traffic negotiation begins between the two plugged in adapters. I was unsure of what was happening and thought I had a bad piece of hardware initially.

[![Powerline NIC](/assets/images/powerline-networking-02.png "Powerline NIC"){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/powerline-networking-02.png){:target="_blank"}

I found no solution for this problem. So sadly, these are just bricks for my homelab use and another odd lost technology.
