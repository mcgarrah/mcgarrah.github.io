---
title: "Adding Ceph Dashboard to Your Proxmox Cluster"
layout: post
categories: [technical, homelab]
tags: [proxmox, ceph, dashboard, monitoring, cluster, web-interface]
---

The Ceph Dashboard is incredibly useful for monitoring your cluster's health, but setting it up on Proxmox isn't as straightforward as the documentation suggests. After wrestling with SSL certificates and password policies, here's how to get it working properly.

## Why You Want the Ceph Dashboard

The dashboard gives you a web interface to monitor your Ceph cluster without SSH'ing into nodes and running CLI commands. You can see OSD status, pool usage, performance metrics, and cluster health at a glance. It's essential for any serious homelab running Ceph. Or if you are doing something unusual like use USB Drives for your storage media and want additional metrics for performance evaluation. I also have fast SSDs for my DB/WAL with the USB Drives for Data.

<!-- excerpt-end -->

## Step 1: Install Dashboard Package

First, install the dashboard package on all manager nodes. In my 3-node cluster, that means all three nodes since they all run ceph-mgr:

```bash
# Run on each manager node
apt install ceph-mgr-dashboard -y
```

For my cluster:

```bash
root@harlan:~# apt install ceph-mgr-dashboard -y
root@kovacs:~# apt install ceph-mgr-dashboard -y  
root@poe:~# apt install ceph-mgr-dashboard -y
```

## Step 2: Enable the Dashboard Module

On any manager node (I used harlan as my primary):

```bash
# Enable the dashboard module
ceph mgr module enable dashboard

# Verify it's enabled
ceph mgr module ls | grep dashboard
```

## Step 3: The SSL Certificate Challenge

Here's where things get interesting. The standard `ceph dashboard create-self-signed-cert` command fails on newer Proxmox versions:

```bash
root@harlan:~# ceph dashboard create-self-signed-cert
Error ENOTSUP: Creating self-signed certificates is currently not available.
```

### Option A: Disable SSL (Quick and Dirty)

For homelab use behind a firewall, you can disable SSL entirely:

```bash
# Disable SSL
ceph config set mgr mgr/dashboard/ssl false

# Restart the dashboard
ceph mgr module disable dashboard
ceph mgr module enable dashboard

# Check the service URL
ceph mgr services
```

This gives you HTTP access on port 8080.

### Option B: Manual SSL Setup (Recommended)

For proper SSL, create certificates manually:

```bash
# Generate self-signed certificate
openssl req -newkey rsa:2048 -nodes -x509 \
  -keyout /root/dashboard-key.pem -out /root/dashboard-crt.pem -sha512 \
  -days 3650 -subj "/CN=IT/O=ceph-mgr-dashboard" -utf8

# Install the certificates
ceph config-key set mgr/dashboard/key -i /root/dashboard-key.pem
ceph config-key set mgr/dashboard/crt -i /root/dashboard-crt.pem

# Enable SSL
ceph config set mgr mgr/dashboard/ssl true

# Restart dashboard
ceph mgr module disable dashboard
ceph mgr module enable dashboard
```

## Step 4: Create Dashboard User

Now for the fun part - creating a user. The default password policy is ridiculously strict for homelab use:

```bash
# This will fail with "Password is too weak"
echo "admin" > ./password
ceph dashboard ac-user-create admin -i ./password administrator --force
```

### Disable Password Policies

For homelab use, disable the password complexity requirements:

```bash
# Disable password complexity checks
ceph dashboard set-pwd-policy-check-complexity-enabled false

# If that's not enough, disable password policy entirely
ceph dashboard set-pwd-policy-enabled false

# Now create the user
ceph dashboard ac-user-create admin -i ./password administrator --force
```

## Step 5: Access Your Dashboard

Find your dashboard URL:

```bash
ceph mgr services
```

This will show something like:
- HTTP: `http://192.168.86.12:8080/`
- HTTPS: `https://192.168.86.12:8443/`

The dashboard runs on whichever node is currently the active Ceph manager. If the manager fails over to another node, the URL will change to that node's IP.

## My Working Configuration

After all the setup, here's what I ended up with:

- **URL**: `https://192.168.86.12:8443/#/dashboard`
- **Username**: `admin`
- **Password**: `admin` (don't judge, it's a homelab)
- **SSL**: Enabled with self-signed certificates
- **Password Policy**: Disabled for sanity

## Dashboard Features You'll Love

Once logged in, you get access to:

- **Cluster Status**: Overall health and warnings
- **OSD Management**: Individual drive status and performance
- **Pool Information**: Usage, PG status, and performance metrics
- **Performance Graphs**: IOPS, bandwidth, and latency over time
- **Configuration**: Cluster settings and module management

## Troubleshooting Tips

1. **Dashboard not accessible?** Check `ceph mgr services` to see which node is active
2. **SSL certificate warnings?** Expected with self-signed certs - just accept the risk
3. **Password too weak errors?** Disable password policies as shown above
4. **Module not starting?** Check `systemctl status ceph-mgr@[hostname].service`

## Important Notes

- The dashboard follows the active ceph-mgr service, so the URL can change during fail overs
- SSL certificates are cluster-wide, you only need to create them once
- User accounts are also cluster-wide
- The dashboard uses the same authentication as the Ceph cluster

## Security Considerations

For production use, you'd want:

- Proper SSL certificates from a CA
- Strong password policies enabled
- Network access restrictions
- Regular password rotation

But for homelab monitoring, the simplified setup works perfectly and gives you the visibility you need into your Ceph cluster's health and performance.

## References

- [Proxmox Forum Discussion](https://forum.proxmox.com/threads/nautilus-activating-ceph-dashboard.85961/) - Original setup guidance
- [Ceph Dashboard Documentation](https://docs.ceph.com/en/reef/mgr/dashboard/) - Official docs with SSL details

The Ceph Dashboard has become an essential part of my homelab monitoring stack. Being able to quickly check cluster health and OSD performance from a web interface beats SSH'ing into nodes every time.
