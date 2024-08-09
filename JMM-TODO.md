
Jekyll Plugins
    https://jekyllrb.com/docs/plugins/your-first-plugin/

    https://github.com/bdesham/reading_time

    https://github.com/hendrikschneider/jekyll-analytics

    https://github.com/jekyll/jekyll-seo-tag
    https://github.com/pmarsceill/jekyll-seo-gem

    https://github.com/jekyll/jekyll-admin
    https://github.com/erikw/jekyll-google_search_console_verification_file

Merge the Jekyll-Plugin branch to main

As part of the VPN solution:
    Turn off DHCP on Google WiFi to use another DHCP Server
    https://www.reddit.com/r/GoogleWiFi/comments/p0h4wu/turn_off_dhcp_on_google_wifi_to_use_another_dhcp/

CARP and LAG and LACP

ProCurve CheatSheet (has LAG/LACP)
https://community.spiceworks.com/how_to/85991-hp-procurve-cli-cheat-sheet


WSLv2 APT Upgrade

```
Processing triggers for libc-bin (2.35-0ubuntu3.6) ...
/sbin/ldconfig.real: /usr/lib/wsl/lib/libcuda.so.1 is not a symbolic link
```

JekyllRB

https://jekyllrb.com/docs/permalinks/
https://poe.com/chat/24mtugccnxe99ji1srz

PDF version of Resume autogen
https://ognjen.io/generating-pdf-from-jekyll-using-pandoc/

T480 Thomas
    WSLv2 with VSCode
    Chocolatey setup
    Document using nvidia mx150 for AI/ML with Automatic1111 and Comfy

Aimos KVM
    https://www.aliexpress.us/item/3256806092416308.html
    https://www.amazon.com/gp/product/B08QCR62VL
        Really good review with limitations of this KVM
    https://www.reddit.com/r/pikvm/comments/tmkx21/comment/i1yb5qi/?utm_source=share&utm_medium=web2x&context=3

PiKVM setup
    Ctrl-Alt-F2 to get to second virtual console
    
    ScrollLock-ScrollLock - 1-8
    Ctrl-Ctrl 1-8

    Fix terminal consoles - currently 75 rows 200 colums
    https://unix.stackexchange.com/questions/473599/how-to-resize-tty-console-width
        stty -a
        stty rows 45 cols 160
        resizecons 80x25 (FAILED)

    Change passwords (root & admin)
        To change passwords, use the following commands (under root):
        su -  # If you're in the webterm
        rw  # Switch filesystem to read-write mode
        passwd root  # Change OS root password
        kvmd-htpasswd set admin  # Change web ui admin password
        ro  # Back to read-only

    Static IP to PiKVM
        Enable writing with "rw" command on CLI
        Edit file /etc/systemd/network/eth0.network for Ethernet or wlan0.network for Wi-Fi and edit the [Network] section:
        [Network]
        Address=192.168.x.x/24
        Gateway=192.168.x.x
        DNS=192.168.x.x
        DNS=192.168.x.x
        Don't forget the /24 suffix (CIDR), otherwise it will not work and your PiKVM will become unreachable

    https://docs.pikvm.org/edid/

    /etc/kvmd/override.yaml

    How do I add my own SSL cert?
    https://docs.pikvm.org/letsencrypt/

    https://docs.pikvm.org/faq/#common-questions
    What is the default password? How do I change it? (admin/admin)

Tailscale / Headscale vs WireGuard on Brume2
    Thinking space here...

TheTinkerDad (German dude) on Youtube with long rambling LXC/LXD permissions
    Need to grab those and consolidate it to something shorter
    for a cheatsheet. It is really long and boring...
    "LXC + Docker Containers + Storage - A Crash Course!"
    https://youtu.be/QT-WW4iczZ0?si=58myWL5dmqdRozjS

https://www.youtube.com/@TheTinkerDad maybe worth digging into other videos
    https://youtu.be/CjY4-kozIkI?si=GJvK3LIkSdpgSvrQ
    https://youtu.be/fYl5poBJtE4?si=pN0RG-hW7sL500wd
    https://youtu.be/aaFLEdxfyOk?si=gzVWB_VQ2zYrROlC

PiKVM and KVM setup video on youtube
    The order of operation is important and having an HDMI splitter
    that doesn't break the bank for local and webui is important.
    https://youtu.be/w56QCshaiNQ?si=5uERVHKveVXrE0vn
    Maybe fix for media https://youtu.be/azQjfgOMIQQ?si=ckOrqIGmTjbR0I33

    https://blog.ktz.me/pikvm-controlling-up-to-4-servers-simultaneously/
    https://blog.ktz.me/use-1-pikvm-instance-to-control-4-systems/

    How to add PiKVM KVM buttons to webui
    https://github.com/pikvm/pikvm/issues/207#issuecomment-1806784764


Link Aggregation (LAG/LACP) - https://youtu.be/NVO2UV_HQhs?si=pueS2LnSDVEhaxmE
LoRaWAN Apalrd - https://youtu.be/HWF6Qm7JhJU?si=PwX1Ah21EFCPFa-j
