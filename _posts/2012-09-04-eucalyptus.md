---
title:  "Eucalyptus (AWS private Cloud Computing)"
layout: post
LABELS: AWS, EC2, EUCALYPTUS, ISCSI, S3
categories: personal aws ec2 eucalyptus iscsi s3
---

I'm not going to give a full run down of what Eucalyptus is but just point you to their marketing material at [their website](http://www.eucalyptus.com/). The quick summary is it offers the [Amazon Web Services](http://aws.amazon.com/) loaded on a local computer.  These include several of the most interesting services: EC2, S3, EBS, AMI, IAM, and recently they added Autoscaling, Elastic Load Balancer, and Cloudwatch. If that alphabet soup has your interest piqued, then you should continue reading.

Building one of these using their pre-packaged images is dead simple. I'm not one to do anything the simple way and decided to build everything from the source directly from their [Github repository](https://github.com/eucalyptus/eucalyptus). This was not an easy task but definitely taught me a lot about their software and the components of the system.  I would recommend a first-time user to not take my route and just take their binary builds from RPM or their ISO image. Fedora Core has these as well and the guy who supports it is a great guy. Please take the path of least resistance first to get familiar with the software.




In my configuration, I have a couple five to seven year old servers that used to be production. I've got a system with a twelve (12) core CPU and forty-eight (48) GB of RAM and a second system with dual-core and 4GB of RAM. They are an old database server and an old web-server. The heavy-weight system with the better memory and processor was dedicated to serving out virtual machines and the lower-end system is the web services provider. I had a third system that is just a desktop box that is acting as my SAN device with FreeNAS 8.3.

The front end to the whole thing to isolate it from my network is a cheap wireless router that serves out DHCP reservations and provides a private network. The only smart thing on the router is a firewall with port forwarding. I added another desktop system with Linux installed that I use as a [jump host](http://en.wikipedia.org/wiki/Jump_Server) into the environment running OpenSSH.

Added to this is a virtual machine image that is running CentOS 6.4 that runs on the virtual machine server to actually build the Eucalyptus software. This image is running under Linux KVM which will later be used by the Eucalyptus software to serve out images managed by EC2. I subverted the environment to let me use it for a build server as well.

* router - dLink wireless router
* marduk - web services and custom tools
* tiamat - virtual machine provider
  * buildserver vm image
  * EC2 instances
* anshar - SAN server (iSCSI) running FreeNAS 8.3.1
* gozer - jumphost and utilities server
  * OpenSSH
  * Nagios service monitoring

This relatively cheap set of hardware components allows me to replicate the Amazon services and test my code locally.

I'm not going to sugar coat it, there were issues along the way.  Here is a list of the ones that pop to mind:

1. I abandoned trying to build software on Ubuntu 12.04.02 LTS and migrated to CentOS 6.4 for the buildserver.
2. The build process is only mostly documented (but much better in 3.3) with some dependencies missing and no separation between build and runtime environment.
3. iSCSI is never fun to configure (but no harder than the regular iSCSI fun)
4. The S3 support is hit and miss (DeleteObjects and multi-part POST API fail) some are fixed in version 3.4 and a major update is coming in 4.0 (Ceph and Riak CS). They are addresssing this actively.
5. iSCSI volumes has strange behavior with KVM virtual machines
  1. cache=writethrough necessary for kvm images
  2. DAS configuration of Storage Controller takes a couple tries and is a one-way trip
6. I'm still working on windows imaging (painful but getting better) and the 3.4 will have significant improvement in this area. Eustore may be on option soon.
7. They are still working on bfEBS (bootable EBS) but check the IRC channel for help. It works with caveats.

On the plus side their support is excellent and I would recommend joining their IRC channel. Also, some of the above issues had to do with my learning curve. I could have used the Fedora provided RPM or their FastStart image and have gotten much further quicker but I'm stubborn when I start working on something.

I hope someone can use this later.  I'm trying to write down the entire process of building this system and will post it back out here later when it looks a little better. I've got a lot of documentation that needs to be cleaned up for release so the learning curve is reduced.

On a completely separate note, I've got a quick-and-dirty Grails application to allow for viewing and managing Eucalyptus S3 components and it's pretty cool to have a local repository to play around with before paying for the AWS service. I may post on that later when I get time to clean it up a bit. The code is a mess as I was hacking it together to help diagnose issues with S3 and write clean code.
