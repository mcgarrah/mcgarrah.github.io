---
title: "Consolidating Proxmox Notes: A Python Export Script"
layout: post
categories: [technical, homelab]
tags: [proxmox, python, backup, automation, scripting]
published: true
---

One of the underrated features of Proxmox is the ability to leave notes on the individual resources like the Datacenter, individual nodes, and every VM or Container. However, these notes are tucked away in individual configuration files within the Proxmox Cluster File System (`/etc/pve`).

If you're managing a cluster with nodes like *quell*, *edgar*, and *tanaka*, having a single consolidated Markdown file of all your documentation is incredibly helpful for disaster recovery or general reference.

<!-- excerpt-end -->

## The Challenge

Proxmox stores its configuration in a specialized fuse filesystem at `/etc/pve`. The Proxmox web UI provides a "Notes" feature for each resource (Datacenter, Nodes, VMs, and LXC containers) that stores multi-line documentation as comment lines starting with `#` in the config files.

For example, your datacenter config might contain detailed cluster documentation:

```bash
#We have a six node HA cluster with Tanaka and Harlan/Kovacs/Poe/Edgar/Quell.
#
#We have a five node Ceph Cluster for Harlan/Kovacs/Poe/Edgar/Quell storage nodes
# - 4 x Nvidia P620 GPUs in Harlan/Kovacs/Poe/Quell
# - 2 x Nvidia K600 GPUs in Edgar/Tanaka

keyboard: en-us
```

And individual node configs track hardware-specific issues:

```bash
# /etc/pve/nodes/quell/config
#**2026-01-21**
#
#Pulled the /dev/sdb zfs boot mirror as it was damaged. No boot mirror.
```

To get a clean backup, we need to extract these comment lines and decode any URL-encoded characters that Proxmox uses internally.

## Configuration File Locations

Proxmox uses a specialized cluster filesystem called `pmxcfs` that presents configuration data differently depending on where you look. Here's the critical insight:

**The top-level directories are node-local shortcuts:**

```bash
root@edgar:~# ls /etc/pve/qemu-server/
# Only shows VMs running on edgar

root@edgar:~# ls /etc/pve/lxc/
# Only shows LXC containers on edgar
```

**The true cluster-wide source of truth is in `/etc/pve/nodes/`:**

```bash
# Datacenter-wide configuration
/etc/pve/datacenter.cfg

# Individual node configurations
/etc/pve/nodes/edgar/config
/etc/pve/nodes/harlan/config
/etc/pve/nodes/kovacs/config
/etc/pve/nodes/poe/config
/etc/pve/nodes/quell/config
/etc/pve/nodes/tanaka/config

# Virtual Machines per node
/etc/pve/nodes/edgar/qemu-server/*.conf
/etc/pve/nodes/harlan/qemu-server/*.conf
/etc/pve/nodes/poe/qemu-server/*.conf
# ... (each node has its own subdirectory)

# LXC Containers per node
/etc/pve/nodes/edgar/lxc/*.conf
/etc/pve/nodes/harlan/lxc/*.conf
/etc/pve/nodes/poe/lxc/*.conf
# ... (each node has its own subdirectory)
```

This is the "smoking gun" - to capture notes from your entire cluster from a single node, you must traverse `/etc/pve/nodes/` rather than relying on the top-level shortcuts.

## The Python Solution

The `proxmox_notes_exporter.py` script handles the heavy lifting:

1. **Traverses** the entire `/etc/pve/nodes/` tree to find all configuration files
2. **Decodes** URL-encoded characters from the Web UI (`%20` → space, `%3A` → colon)
3. **Detects** HTML content and wraps it in code blocks for Markdown compatibility
4. **Consolidates** results into a clean engineering report organized by type

### Key Features

- **Captures notes from Proxmox web UI** - Extracts comment lines (starting with `#`) added via the Notes interface
- **Decodes URL encoding** - Handles `%20` (space), `%3A` (colon), and other encoded characters
- **Organizes by type** - Datacenter, Nodes, VMs, and LXC containers in separate sections
- **Migration-aware** - VMs and LXC containers are listed independently since they can migrate between nodes
- **Preserves community script templates** - LXC containers created from [Helper-Scripts.com](https://helper-scripts.com) include HTML metadata comments
- **Optional inventory mode** - Use `--include-empty` to list all VMs/LXCs even without notes
- **Verbose output** - Use `--verbose` to see processing details and statistics

### Usage Examples

```bash
# Basic usage with default output location
./proxmox_notes_exporter.py

# Specify custom output location
./proxmox_notes_exporter.py /root/cluster_backup.md

# Create complete inventory including guests without notes
./proxmox_notes_exporter.py /tmp/inventory.md --include-empty

# Show processing details and statistics
./proxmox_notes_exporter.py /mnt/backup/notes.md --verbose

# Get help
./proxmox_notes_exporter.py --help
```

### Why Preserve Everything?

During disaster recovery, you want a complete snapshot of your cluster configuration. Those community script comments tell you exactly which template was used to create each container, making it easier to rebuild or troubleshoot. The script treats all comments as valuable documentation.

```python
#!/usr/bin/env python3
"""
Proxmox Cluster Notes Backup Script
Copyright (c) 2026 Michael McGarrah
Licensed under MIT License

Extracts and consolidates notes from Proxmox VE cluster configuration files
Author: Michael McGarrah (mcgarrah@gmail.com)
Website: https://mcgarrah.org
Repository: https://github.com/mcgarrah/mcgarrah.github.io
"""

import os
import argparse
import urllib.parse
from datetime import datetime

def extract_log_entries(filepath):
    """Extracts lines starting with # from Proxmox config files."""
    if not os.path.exists(filepath):
        return None
    
    log_content = []
    has_html = False
    try:
        with open(filepath, 'r') as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith('#'):
                    comment = stripped.lstrip('#').strip()
                    if '<' in comment or 'href=' in comment:
                        has_html = True
                    log_content.append(comment)
        
        if log_content:
            decoded = urllib.parse.unquote("\n".join(log_content))
            if has_html:
                return f"```html\n{decoded}\n```"
            return decoded
        return None
    except Exception:
        return None

def generate_blog_markdown(output_file, include_empty=False, verbose=False):
    """Generate consolidated Markdown report of all Proxmox cluster notes."""
    base_path = "/etc/pve"
    
    if verbose:
        print(f"Scanning Proxmox cluster at {base_path}...")
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    md = ["# Proxmox Cluster Engineering Log\n"]
    md.append(f"**Backup Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Datacenter Master Log
    md.append("## Datacenter Configuration")
    dc_notes = extract_log_entries(os.path.join(base_path, 'datacenter.cfg'))
    if dc_notes:
        md.append(f"```text\n{dc_notes}\n```\n")
    else:
        md.append("No datacenter notes.\n")

    # Collect all VMs and LXCs across nodes
    all_vms = {}
    all_lxcs = {}
    vm_count = lxc_count = 0
    
    # Traverse Node Subdirectories
    md.append("## Node Hardware Logs")
    nodes_dir = os.path.join(base_path, "nodes")
    if os.path.exists(nodes_dir):
        for node in sorted(os.listdir(nodes_dir)):
            if verbose:
                print(f"Processing node: {node}")
            
            # Node Hardware Log
            node_config = os.path.join(nodes_dir, node, "config")
            node_notes = extract_log_entries(node_config)
            if node_notes:
                md.append(f"### {node.upper()}")
                md.append(f"{node_notes}\n")

            # Collect VMs from this node
            qemu_dir = os.path.join(nodes_dir, node, "qemu-server")
            if os.path.exists(qemu_dir):
                for vm in os.listdir(qemu_dir):
                    if vm.endswith(".conf"):
                        vm_id = vm.replace('.conf', '')
                        vm_count += 1
                        note = extract_log_entries(os.path.join(qemu_dir, vm))
                        if note or include_empty:
                            all_vms[vm_id] = (node, note or "No notes.")

            # Collect LXCs from this node
            lxc_dir = os.path.join(nodes_dir, node, "lxc")
            if os.path.exists(lxc_dir):
                for lxc in os.listdir(lxc_dir):
                    if lxc.endswith(".conf"):
                        lxc_id = lxc.replace('.conf', '')
                        lxc_count += 1
                        note = extract_log_entries(os.path.join(lxc_dir, lxc))
                        if note or include_empty:
                            all_lxcs[lxc_id] = (node, note or "No notes.")

    # Output all VMs in one section
    if all_vms:
        md.append("## Virtual Machines")
        for vm_id in sorted(all_vms.keys(), key=int):
            node, note = all_vms[vm_id]
            md.append(f"### VM {vm_id} (on {node})")
            md.append(f"{note}\n")

    # Output all LXCs in one section
    if all_lxcs:
        md.append("## LXC Containers")
        for lxc_id in sorted(all_lxcs.keys(), key=int):
            node, note = all_lxcs[lxc_id]
            md.append(f"### LXC {lxc_id} (on {node})")
            md.append(f"{note}\n")

    with open(output_file, 'w') as f:
        f.write("\n".join(md))
    
    if verbose:
        print(f"\nStatistics:")
        print(f"  Total VMs: {vm_count} (documented: {len(all_vms)})")
        print(f"  Total LXCs: {lxc_count} (documented: {len(all_lxcs)})")
    
    print(f"Success! Backup generated at: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description='Export Proxmox cluster notes to Markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s /root/cluster_backup.md
  %(prog)s /mnt/backup/notes.md --verbose
  %(prog)s /tmp/inventory.md --include-empty
        """)
    
    parser.add_argument('output', 
                        default='/mnt/pve/cephfs/backups/proxmox_notes_backup.md',
                        nargs='?',
                        help='Output file path (default: /mnt/pve/cephfs/backups/proxmox_notes_backup.md)')
    parser.add_argument('--include-empty', 
                        action='store_true',
                        help='Include VMs/LXCs without notes (useful for inventory)')
    parser.add_argument('--verbose', '-v', 
                        action='store_true',
                        help='Show processing details and statistics')
    
    args = parser.parse_args()
    generate_blog_markdown(args.output, args.include_empty, args.verbose)

if __name__ == "__main__":
    main()
```

## Future Enhancements

For publishing the cluster documentation, you could extend this script to generate HTML output alongside the Markdown. This would allow you to serve the documentation through your Caddy LXC container:

```bash
# Generate both Markdown and HTML versions
./proxmox_notes_exporter.py /var/www/cluster/notes.md
pandoc /var/www/cluster/notes.md -o /var/www/cluster/index.html --standalone --css=style.css
```

This creates a web-accessible version of your cluster documentation that stays in sync with your engineering notes. I have not done this part yet and will likely write a follow up when I do it.
