---
title: "Writing to Think: Two Decades of Figuring Things Out in Public"
layout: post
categories: [writing, personal]
tags: [writing, blogging, substack, reflection, motivation]
excerpt: "I don't write to share what I know. I write to figure out what I know. After 151 posts across 20+ years, I'm finally honest about why I do this — and why I'm moving to Substack to find the conversation I've been looking for."
description: "A reflection on two decades of technical blogging, the real motivation behind writing things down, and why Substack is the next step for finding the interaction that static sites can't provide."
published: false
---

I've been writing about technology since 2004. That's over twenty years of blog posts, platform migrations, and long stretches of silence. If you looked at my publishing history on a timeline, you'd see bursts of intense activity separated by years of nothing. The pattern tells a story I didn't fully understand until recently.

I don't write to share what I know. I write to figure out what I know.

<!-- excerpt-end -->

## The Real Reason I Write

There's a thing that happens when you're deep in a technical problem — you've got six browser tabs open, three terminal windows, and a half-formed understanding of why something isn't working. You *think* you understand it. You can feel the shape of the solution. But you can't articulate it yet.

Writing is how I close that gap. It is often how I find what I call the elegant solution to a problem rather than the brute force one.

When I sit down to document how I got Ceph running on a cluster of machines that were never designed for distributed storage, or why a Jekyll plugin breaks in a way that makes no sense until it suddenly does, I'm not writing for an audience. I'm writing for the version of me that's still confused. If I can explain it clearly enough that someone else could follow along, then I actually understand it. If I can't, I don't — and the writing shows me exactly where the holes are.

This is the [Feynman Technique](https://en.wikipedia.org/wiki/Learning_by_teaching) dressed up as a blog. Explain it simply or admit you don't get it yet.

## The Timeline Tells the Story

My publishing history has a pattern:

```mermaid
---
config:
  theme: default
---
xychart-beta
  title "Blog Posts Published Per Year"
  x-axis [2001, 2004, 2005, 2007, 2008, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
  y-axis "Posts" 0 --> 35
  bar [1, 3, 2, 2, 1, 4, 17, 9, 2, 9, 7, 2, 0, 0, 0, 0, 0, 0, 3, 24, 33, 32]
```

The seven-year gap from 2017–2022 is hard to miss. So is the explosion after it.

- **2001–2008** — Nine posts. Life updates, career moves, figuring out what a blog even was.
- **2011–2012** — Twenty-six posts in two years. I'd gotten my hands on a Seagate BlackArmor NAS and couldn't stop pulling it apart. Every post was me working through another layer of that hardware.
- **2013–2016** — Twenty posts across four years. Steady but not urgent. I was learning, but not struggling with anything hard enough to need the writing.
- **2017–2022** — Nothing. Zero posts for nearly seven years. Georgia Tech's OMSCS program, career changes, life. I was learning constantly but not writing any of it down.
- **2023** — Three posts. Testing the waters again.
- **2024** — Twenty-four posts. The homelab buildout year. Proxmox, Ceph, ZFS, networking — every week brought a new problem that needed to be written through.
- **2025–2026** — Sixty-five posts published or scheduled, forty-three more in drafts. Something broke open.

The seven-year gap is the most interesting part. I didn't stop learning during that time — I was doing a master's degree in computer science, working in cloud architecture, building things constantly. But I wasn't writing. And looking back, I think I lost something during that period. Not knowledge, but *clarity*. The kind of clarity you only get when you force yourself to explain what you're doing and why.

When I came back to writing in 2023, it felt like turning on a light in a room I'd been navigating by feel.

## Writing as Debugging

Programmers have a concept called [rubber duck debugging](https://en.wikipedia.org/wiki/Rubber_duck_debugging) — you explain your code to an inanimate object and the act of explaining reveals the bug. My blog is a very elaborate rubber duck.

<!-- TODO: Find the idol picture on my cell phone and upload to assets/images/ for this section. Would make a great visual tie-in here. -->

I can't count the number of times I've started writing a post about how I solved something, only to realize halfway through that my solution was wrong, incomplete, or accidentally correct for the wrong reasons. The writing caught what the doing missed.

A few examples from recent memory:

- Writing about [Ceph nearfull warnings](/proxmox-ceph-nearfull/) forced me to actually understand erasure coding math instead of just trusting the defaults.
- Documenting my [Jekyll GDPR implementation](/implementing-gdpr-compliance-jekyll-adsense/) revealed three edge cases I'd missed in the code.
- The [ZFS boot mirror](/proxmox-zfs-boot-mirrors-part-1/) series started as a quick how-to and turned into a two-part deep dive because the first draft showed me I didn't understand the failure modes.

Every one of those posts made the underlying work better. The writing wasn't a record of what I'd done — it was part of doing it.

## Sharing Is a Side Effect

Here's the part that took me twenty years to be honest about: sharing is a byproduct, not the goal.

I publish these posts because making them public raises the stakes just enough. If it's just notes in a private wiki, I'll cut corners. I'll write "do the thing with the config" and move on. But if someone might actually read it — even if nobody does — I'll make sure the commands actually work, the explanations actually explain, and the logic actually holds.

The audience is a forcing function for quality. But it's not the motivation.

The motivation is that I genuinely cannot figure out complex things without writing them down. My brain needs the structure that sentences and paragraphs impose on messy, nonlinear problem-solving. Code is one kind of thinking. Writing is another. I need both.

## What's Missing: The Conversation

So if sharing isn't the primary goal, why does it bother me that a static Jekyll blog on GitHub Pages is essentially a one-way street?

Because there's a difference between *sharing* and *interaction*.

I set up [Giscus comments](/jekyll-giscus-comments-implementation/) backed by GitHub Discussions, and it works fine technically. But the barrier to commenting on a static blog is high — you need a GitHub account, you need to find the post, you need to care enough to leave a thought. The result is that most posts get zero comments. The writing helps me think, but I'm thinking alone.

What I actually want is the back-and-forth. Someone who reads a post about Ceph storage economics and says "have you considered this other approach?" or "I tried that and here's what happened." Not engagement metrics. Not likes. Actual technical conversation with people who are working on similar problems.

That's the piece a static blog can't provide, and it's why I'm setting up [Substack](https://mcgarrah.substack.com/) for the coming year.

## Why Substack

I'm not abandoning the blog. The Jekyll site is the permanent archive — version controlled, self-hosted, no platform risk. Every post I've written since 2001 lives there and will continue to live there.

But Substack solves the specific problem I have:

- **Email delivery** — Posts land in inboxes instead of waiting to be discovered. The people who want to read them don't have to remember to check a website.
- **Reply culture** — Substack's comment and reply model is lower friction than GitHub Discussions. People actually respond.
- **Discovery** — Substack has a built-in network of readers interested in technical content. My Jekyll blog has whatever Google decides to send my way.
- **Conversation threading** — The discussion happens alongside the content, not in a separate system.

The plan is straightforward: continue writing on the Jekyll blog as the source of truth, cross-post to Substack for distribution and discussion. The writing process doesn't change. The thinking-through-writing doesn't change. What changes is that the writing might actually start conversations instead of sitting in a well-organized archive.

## 151 Posts Later

I've published 151 posts across twenty-plus years. The topics range from NAS hacking to Ceph cluster economics to Jekyll plugin development to tankless water heater maintenance. The through-line isn't the technology — it's the process of encountering something I don't fully understand and writing my way to understanding it.

The bursts in my publishing history correspond exactly to periods when I was building something new and struggling with it. The silences correspond to periods when I was either too busy to write or — more honestly — not struggling enough to need the writing.

I'm in a burst right now. Forty-three drafts in the pipeline, posts scheduled through mid-2026, and a Kubernetes-on-Proxmox project generating new material every week. The homelab keeps breaking in interesting ways, and every break is a post waiting to happen.

If you've read this far, you're probably someone who thinks by writing too. Or you're considering starting. My advice is simple: don't write for an audience. Write for the confused version of yourself. The audience, if it comes, is a bonus. The understanding is the point.

And if you want to actually talk about any of this — that's what the [Substack](https://mcgarrah.substack.com/) is for.
