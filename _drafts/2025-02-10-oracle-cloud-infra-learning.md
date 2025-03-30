---
title:  "Oracle Cloud Infrastructure for the Homelab"
layout: post
published: false
---

OCI is an interesting proposition. They offer something called the Always Free Tier which seems to have a very generous amount of hardware.

I am an Amazon guy mostly with some Azure, Google, DigitalOcean, IBM, and Rackspace thrown into the mix. So this offer of 24GB RAM and 4 decent vCPUs with 200GB of disk space and 20GB of object storage just sounds too good to be true.

I just remember that anything free means you are the product being sold.

<!-- excerpt-end -->

---

## Reference and Research

Big hits for this:

Compute Resources ($500 year worth)
Networking
Kubernetes (uses above compute resources)


https://www.reddit.com/r/oraclecloud/comments/1adolgv/oracle_cloud_always_free_tier/

 

the two AMD micro instances are self-explanatory

the way they explain the Ampere is weird

basically, assuming 24/7 operation for the full month, you can have a single 4-core / 24GB RAM system, or you could divide it up into smaller systems, such as four 1-core / 6GB RAM systems

also note that you have 200GB of boot/block storage, which a minimum boot drive size of ~50MB (actually 47, I think?) so this caps you at 4 total instances if you want to stay within always free limits. This could be two 2-core / 12 GB Amperes + 2 AMD Micros, or it could be four 1-core / 6 GB Amperes, but you'd have to give up your micros.

Personally I just do a single 4-core 24GB Ampere + a single Micro + my last 100GB set up as Block Storage mounted on my Ampere using paravirtualized, NOT iSCSI (slow garbage).


Yes, it’s actually free. If you stick within the Always Free tier limits, you won’t be charged. This means you can run a 4-core, 24GB machine with a 200GB disk 24/7 and it should not cost you anything. Or you can split those limits into 2 or 4 machines if you want.

I’ve been using them for a couple of years now and the only times I’ve been charged are when I went over the limits, such as when I was creating a new machine to replace an existing one, or when I was trying out a new service and didn’t realise I’d passed the limits (trying kubernetes enhanced clusters in my case). In each case the charges were a few pounds. My biggest bill has been about £6 for a month. Most months it’s 0.

I’ve been putting together a blog post about running kubernetes on Oracle for free, I’ll post it somewhere here when it’s ready.

 

https://me.mattscott.cloud/kubernetes-on-oracle-cloud-for-free/

 

 

https://registry.terraform.io/modules/robinlieb/free-tier-kubernetes/oci/latest

https://github.com/robinlieb/terraform-oci-free-tier-kubernetes

 

https://registry.terraform.io/modules/ystory/always-free-oke/oci/latest

https://github.com/ystory/terraform-oci-always-free-oke
                https://github.com/incrig/tf-oci-free_k8s (9 ahead)

Oracle Cloud Infrastructure (OCI) Free Tier has limits on the number of compute instances, block storage, object storage, and bandwidth that can be used. These limits are in place to prevent fraudulent accounts from using too many resources.

 

https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm#freetier_topic_Always_Free_Resources_Infrastructure

https://github.com/anotherglitchinthematrix/oci-free-tier-terraform-module (retry create)

Interesting one for creating max CPU resources (also does it thru the OCI Resource Manager)

https://github.com/RhubarbSin/terraform-oci-free-compute-maximal-example

https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources_Launching.htm  OCI Resource Manager to accelerate infrastructure buildout

 