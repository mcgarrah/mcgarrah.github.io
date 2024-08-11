---
title:  "Proxmox Ceph Nearfull for the Homelab"
layout: post
published: false
---
### Storage NearFull

[Storage Capacity](https://docs.ceph.com/en/latest/rados/configuration/mon-config-ref/#storage-capacity)

```console
root@harlan:~# ceph osd dump | grep ratio
full_ratio 0.95
backfillfull_ratio 0.9
nearfull_ratio 0.85
```

By default, when OSDs reach 85% capacity, `nearfull_ratio` warning is triggered.

By default when OSDs reach 90% capacity, `backfillfull_ratio` warning is triggered.  At this point the cluster will deny backfilling to the OSD in question.

By default when OSDs reach 95% capacity, `full_ratio` is triggered, all PGs (Placement Groups) on the OSDs in question will be marked Read Only, as well as all pools which are associated with the PGs on the OSD. The cluster is marked Read Only, to prevent corruption from occurring.

These settings are changed in the OSDMap using `ceph osd set-nearfull-ratio` and `ceph osd set-full-ratio` and are to be determined based on your specific configuration.

The defaults exist for a reason and you should not modify them without careful consideration.

Identify two numbers for your cluster:

1. The number of OSDs.
2. The total capacity of the cluster

If you divide the total capacity of your cluster by the number of OSDs in your cluster, you will find the mean average capacity of an OSD within your cluster. Consider multiplying that number by the number of OSDs you expect will fail simultaneously during normal operations (a relatively small number). Finally multiply the capacity of the cluster by the full ratio to arrive at a maximum operating capacity; then, subtract the number of amount of data from the OSDs you expect to fail to arrive at a reasonable full ratio. Repeat the foregoing process with a higher number of OSD failures (e.g., a rack of OSDs) to arrive at a reasonable number for a near full ratio.

Ceph returns the nearfull osds message when the cluster reaches the capacity set by the mon osd nearfull ratio defaults parameter. By default, this parameter is set to 0.85 , which means 85% of the cluster capacity.

```console
root@harlan:~# ceph osd df tree
ID  CLASS  WEIGHT    REWEIGHT  SIZE     RAW USE  DATA     OMAP     META     AVAIL    %USE   VAR   PGS  STATUS  TYPE NAME
-1         54.58063         -   41 TiB   26 TiB   26 TiB  152 MiB   80 GiB   15 TiB  62.58  1.00    -          root default
-3         18.19354         -   14 TiB  8.2 TiB  8.2 TiB   48 MiB   26 GiB  5.4 TiB  60.34  0.96    -              host harlan
 0    hdd   4.54839   1.00000  4.5 TiB  2.8 TiB  2.7 TiB   18 MiB  6.9 GiB  1.8 TiB  60.48  0.97   48      up          osd.0
 3    hdd   4.54839   1.00000  4.5 TiB  2.5 TiB  2.5 TiB   16 MiB  6.0 GiB  2.0 TiB  55.66  0.89   47      up          osd.3
 6    hdd   4.54839   1.00000  4.5 TiB  3.0 TiB  2.9 TiB   13 MiB   13 GiB  1.6 TiB  64.88  1.04   46      up          osd.6
-7         18.19354         -   14 TiB  9.2 TiB  9.2 TiB   58 MiB   33 GiB  4.4 TiB  67.74  1.08    -              host kovacs
 2    hdd   4.54839   1.00000  4.5 TiB  3.6 TiB  3.6 TiB   11 MiB  7.6 GiB  942 GiB  79.78  1.27   57      up          osd.2
 5    hdd   4.54839   1.00000  4.5 TiB  2.4 TiB  2.4 TiB   34 MiB   12 GiB  2.1 TiB  53.79  0.86   49      up          osd.5
 8    hdd   4.54839   1.00000  4.5 TiB  3.2 TiB  3.2 TiB   13 MiB   13 GiB  1.4 TiB  69.64  1.11   51      up          osd.8
-5         18.19354         -   14 TiB  8.1 TiB  8.1 TiB   46 MiB   22 GiB  5.5 TiB  59.65  0.95    -              host poe
 1    hdd   4.54839   1.00000  4.5 TiB  2.8 TiB  2.8 TiB   11 MiB  6.4 GiB  1.8 TiB  60.95  0.97   43      up          osd.1
 4    hdd   4.54839   1.00000  4.5 TiB  2.5 TiB  2.5 TiB   19 MiB  5.9 GiB  2.0 TiB  56.06  0.90   47      up          osd.4
 7    hdd   4.54839   1.00000  4.5 TiB  2.8 TiB  2.8 TiB   17 MiB  9.7 GiB  1.7 TiB  61.94  0.99   52      up          osd.7
                        TOTAL   41 TiB   26 TiB   26 TiB  152 MiB   80 GiB   15 TiB  62.58
MIN/MAX VAR: 0.86/1.27  STDDEV: 7.64
```

### Reference

[SUSE Support: Cluster Pools got marked read only, OSDs are near full](https://www.suse.com/support/kb/doc/?id=000019724)

*[PVE]: Proxmox Virtual Environment
