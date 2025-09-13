---
title: "Upcoming Articles Roadmap: September - December 2025"
layout: post
categories: [organization, writing]
tags: [planning, roadmap, homelab, proxmox, ceph, jekyll, development, writing]
published: true
---

I've got a pile of articles I want to get out before the end of 2025, and I'm trying to stick to at least one post per week. That's roughly 16 more articles between now and December, which sounds doable if I don't get distracted by shiny new projects.

<!-- excerpt-end -->

## The Plan (Such As It Is)

I'm shooting for **weekly posts** through the end of the year. The topics are all over the place but generally fall into my usual obsessions: homelab stuff, web development, and the inevitable "oh crap, how do I fix this" system administration moments.

I want to **dump all the Proxmox and Ceph content first** while it's still fresh in my brain and the systems are actually running. Some of the meatier topics might get chopped into Part 1/Part 2 posts released in the same week because nobody wants to read a 5,000-word essay about Ceph performance tuning in one sitting.

## Proxmox & Ceph Deep Dives

**Coming First (September-October)**:

- Adding Ceph Dashboard to Your Proxmox Cluster  
- Proxmox 8 Lessons Learned in the Homelab  
- Hybrid Ceph Storage: SSD WAL/DB with USB Drive Data  
- Managing Ceph Nearfull Warnings in Proxmox Homelab  
- Optimizing Ceph Performance in Proxmox Homelab  

This is basically everything I've learned from months of beating my head against Proxmox and Ceph. From "why won't this install" to "holy crap, it's actually working now," these posts will cover the real-world pain and occasional victories of running a Ceph cluster on a bunch of Dell Wyse 3040s that were never meant for this.

I'm doing these first because the lessons are still fresh and the cluster is actually running (knock on wood). Plus, if I wait too long, I'll forget all the weird workarounds I had to figure out. Some of the bigger topics might get split up because nobody needs a novel-length post about storage optimization.

## Hardware & System Administration

**Mixed Throughout (September-November)**:

- Windows Sandbox for Safe Testing  
- Dell Wyse 3040 eMMC Storage Health Monitoring  
- Enabling SMART Monitoring on Seagate USB Drives  
- Essential CLI Tools for Linux System Management  
- Debian Linux Oh-Crap Moment in the Homelab  

This is the grab bag of "stuff I figured out while trying to keep my homelab from catching fire." Hardware monitoring, random Windows tricks, and the inevitable "oh crap, I think I just broke everything" moments that make homelabbing so much fun. That last one is going to be particularly entertaining - let's just say I learned some things about Linux boot processes the hard way.

## Development & Automation

**Early Fall**:

- Github Actions pip-audit PR  
- Generate Git Timesheet from Commit Logs  

A couple of Python tools I built because I got tired of doing repetitive stuff manually. The timesheet generator has been a lifesaver for tracking how much time I actually spend on different projects (spoiler: it's always more than I think).

## Jekyll & Web Development

**Late Fall (November-December)**:

- Jekyll Website Optimization for GitHub Pages - Part 1
- Jekyll Website Optimization for GitHub Pages - Part 2  
- Adding Google Custom Search to Jekyll Website  
- SASS Circular Dependency Nightmare: Lessons from Jekyll Architecture  

This is me documenting all the ways I've broken and fixed this website. From making it faster to that time I created a circular dependency nightmare in SASS (that was fun), these posts are for anyone else crazy enough to build a technical blog with Jekyll. Learn from my mistakes so you don't have to make them yourself.

## Meta & Reflection

**Year-End**:

- Google Services Sprawl

A rant about how Google has turned "add analytics to my blog" into a multi-service integration nightmare. Seriously, why does everything have to be so complicated?

## Why Bother With a Schedule?

Honestly, I'm terrible at sticking to schedules, but here's why I'm trying:

1. **Consistency**: Turns out people like knowing when new stuff is coming
2. **Documentation**: If I don't write it down while it's fresh, I'll forget how I fixed that weird thing
3. **Knowledge Sharing**: The homelab community has helped me out tons, so I should give back
4. **Personal Growth**: Writing about technical stuff makes me understand it better (who knew?)

## Content Themes

Looking at the roadmap, several themes emerge:

- **Practical Homelab**: Real hardware, real problems, real solutions
- **Performance Optimization**: Making the most of limited resources
- **Automation**: Python tools to solve recurring problems
- **Web Development**: Jekyll optimization and architectural lessons
- **System Administration**: CLI tools and troubleshooting techniques

## Reality Check

Look, I have general timelines, but let's be honest - stuff happens. Remember this all has to fit in between my MBA program, a fulltime job, and family. The nice thing about Jekyll's future-dated posts is I can shuffle things around if I finish something early or if my homelab decides to have a meltdown and gives me emergency content.

The goal is consistency, not perfection. Some weeks might get bonus posts if I break something spectacularly or figure out something particularly cool.

## What's the Point?

This is about 4 months of content that should take us through the end of 2025. Everything comes from actual stuff I'm doing in my homelab or development work, so it's not theoretical nonsense - it's real problems and real solutions (or at least real attempts at solutions).

The mix ranges from deep technical rabbit holes (Ceph tuning, anyone?) to simple tools that just make life easier. Hopefully there's something useful for everyone who's crazy enough to run their own infrastructure.

Here's to actually sticking to a publishing schedule for once!
