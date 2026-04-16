---
title: "SSH Key-Based Access to a Proxmox Cluster"
layout: post
categories: [proxmox, homelab, security]
tags: [proxmox, ssh, homelab, security, clustering, dell-optiplex-990]
excerpt: "Typing passwords every time you SSH into a Proxmox node gets old fast — especially with a six-node cluster. Here's how to set up SSH key authentication and an SSH config so you can just type 'ssh harlan' and be in."
description: "Step-by-step guide to configuring SSH key-based authentication for a Proxmox cluster. Covers key generation, key deployment, SSH config setup with named hosts, and how Proxmox's shared authorized_keys across cluster nodes means you only copy the key once."
date: 2026-04-17
last_modified_at: 2026-04-17
published: true
seo:
  type: BlogPosting
  date_published: 2026-04-17
  date_modified: 2026-04-17
---

Typing passwords every time you SSH into a Proxmox node gets old fast — especially when you have a six-node cluster and you're bouncing between nodes all day. SSH key-based authentication eliminates the password prompts entirely, and Proxmox makes it even easier because the cluster shares `authorized_keys` across all nodes. Copy the key once, access every node.

I needed this set up so I could run the [Ceph WAL vs DB performance benchmarks](/ceph-wal-vs-db-performance-test/) from my development machine — scripting SSH commands across multiple nodes to collect latency data, trigger scrubs, and restart OSDs is painful when every command demands a password. Getting passwordless SSH sorted first made the whole test workflow possible.

<!-- excerpt-end -->

## Prerequisites

- A local development machine (I'm running Ubuntu 24.04 LTS)
- A Proxmox cluster on the local network (I'm running Proxmox 8.4)
- Root password for at least one Proxmox node (you'll need it one last time)

## My Cluster

My homelab cluster is named **AlteredCarbon** (yes, after the show). Six Dell OptiPlex 990 nodes:

| Node | IP Address |
|------|------------|
| harlan | 192.168.86.11 |
| kovacs | 192.168.86.12 |
| poe | 192.168.86.13 |
| edgar | 192.168.86.14 |
| tanaka | 192.168.86.15 |
| quell | 192.168.86.16 |

## Step 1: Generate an SSH Key

If you already have a key at `~/.ssh/id_ed25519`, skip this step. Check with:

```bash
ls ~/.ssh/id_ed25519.pub
```

If you don't have one, generate it:

```bash
ssh-keygen -t ed25519 -C "yourname-dev"
```

Accept the default path (`~/.ssh/id_ed25519`). Adding a passphrase is optional but recommended — you can use `ssh-agent` to avoid retyping it every time.

**Why ed25519?** It's faster, more secure, and produces shorter keys than RSA. There's no reason to use RSA for new keys unless you're dealing with ancient systems that don't support it.

## Step 2: Pre-load Host Key Fingerprints

The first time you SSH into a new host, you get the "authenticity can't be established" prompt and have to type "yes" to accept the fingerprint. With six nodes, that's six interactive prompts. Skip all of them by pulling the host keys in bulk with `ssh-keyscan`:

```bash
ssh-keyscan 192.168.86.{11..16} >> ~/.ssh/known_hosts 2>/dev/null
```

This grabs the ED25519 (and other) host keys from all six nodes and appends them to your `known_hosts` file. No interactive prompts, no typing "yes" six times.

If you've already set up your SSH config (Step 4 below), you can also scan by name to cover both hostname and IP lookups:

```bash
ssh-keyscan harlan kovacs poe edgar tanaka quell 192.168.86.{11..16} >> ~/.ssh/known_hosts 2>/dev/null
```

## Step 3: Copy the Key to One Proxmox Node

Here's the nice part about Proxmox clusters — the `/etc/pve/` filesystem is shared across all nodes via `pmxcfs` (the Proxmox Cluster File System). This means `authorized_keys` for root is shared too. Copy your key to any single node and it's available on all of them:

```bash
ssh-copy-id root@192.168.86.11
```

Enter the root password when prompted. That's the last time you'll need it.

## Step 4: Create an SSH Config

Rather than typing `ssh root@192.168.86.11` every time, create `~/.ssh/config` so you can just type `ssh harlan`:

```
# AlteredCarbon Proxmox Cluster
Host harlan
    HostName 192.168.86.11
    User root

Host kovacs
    HostName 192.168.86.12
    User root

Host poe
    HostName 192.168.86.13
    User root

Host edgar
    HostName 192.168.86.14
    User root

Host tanaka
    HostName 192.168.86.15
    User root

Host quell
    HostName 192.168.86.16
    User root

Host harlan kovacs poe edgar tanaka quell
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking accept-new
```

Set the correct permissions (SSH will refuse to use a config file that's too open):

```bash
chmod 600 ~/.ssh/config
```

The shared `Host` block at the bottom applies two settings to all cluster nodes:

- **IdentityFile** — points to your ed25519 key so SSH doesn't have to guess
- **StrictHostKeyChecking accept-new** — automatically accepts the host key on first connection, but will warn you if it changes later (which could indicate a MITM attack or a node reinstall)

## Step 5: Test It

```bash
ssh harlan
```

You should drop straight into a root shell with no password prompt. Verify the other nodes work too:

```bash
for node in harlan kovacs poe edgar tanaka quell; do
    echo "--- $node ---"
    ssh $node "hostname && uptime"
done
```

If everything is working, you'll see the hostname and uptime for all six nodes scroll by with no password prompts.

## Optional: Use ssh-agent for Passphrase Keys

If you set a passphrase on your key (and you should consider it), you can avoid retyping it by loading the key into `ssh-agent`:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

On Ubuntu 24.04, the GNOME Keyring typically handles this automatically — you'll be prompted for the passphrase once after login and it's cached for the session.

## Optional: Harden SSH on the Cluster

Once you've confirmed key authentication works on all nodes, you can disable password authentication entirely on the Proxmox side. SSH into any node and run:

```bash
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd
```

**Warning:** Do this carefully. Keep a session open as a safety net, or use the Proxmox web UI console (which doesn't go through SSH) in case something goes wrong. Since this is `/etc/ssh/sshd_config` (a local file, not shared via `/etc/pve/`), you'll need to repeat this on each node individually.

## Why This Works Across the Cluster

Proxmox clusters use `pmxcfs` to share configuration across nodes. The root user's `authorized_keys` lives under this shared filesystem, so any key you add to one node is immediately available on all nodes in the cluster. This is the same mechanism that lets you manage all nodes from a single Proxmox web UI.

This is a Proxmox-specific convenience — on a non-clustered setup, you'd need to run `ssh-copy-id` against each host individually.

## Wrapping Up

Four commands to go from password prompts to passwordless access across an entire Proxmox cluster:

1. `ssh-keygen -t ed25519` — generate the key
2. `ssh-keyscan 192.168.86.{11..16} >> ~/.ssh/known_hosts` — pre-load host fingerprints
3. `ssh-copy-id root@<any-node>` — copy it once
4. Create `~/.ssh/config` — name your nodes

It's a small quality-of-life improvement that pays off every single day when you're managing a homelab cluster. In my case, it was the prerequisite that made running [Ceph WAL vs DB benchmarks](/ceph-wal-vs-db-performance-test/) across all six nodes practical — scripting `ssh harlan 'ceph tell osd.0 bench'` is a lot more pleasant than typing passwords six times per test run.
