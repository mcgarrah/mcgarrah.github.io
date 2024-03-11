---
title:  "Amazon Web Services"
layout: post
categories: personal aws
---

New job and learning [AWS](http://aws.amazon.com) in support of distributed computing. I've done a good bit of research to understand the ecology of web services. They can be expensive but when you count total costs, they come out pretty close to break-even. You can lease computational power for relatively short periods to do quick work, then give the hardware back and stop paying for it. That is a powerful shift in technology.

OpenStack, CloudStack, Eucalyptus and a couple others where in the running while doing the evaluations. Each had their advantages which I'll probably write about later.

I settled on implementing a [Eucalyptus system](http://www.eucalyptus.com) using spare hardware. So far I've got a working and running system built from the source code. It provides a subset of the AWS services on local hardware for testing.  The [S3](http://aws.amazon.com/s3/) support isn't quite there as of version 3.3.0 but it might improve in the next couple of months. S3 is simple storage interface allowing for storing information by a key value.  Their [EC2](http://aws.amazon.com/ec2/) support appears to be much better and allows for quickly building virtual machines with pre-configured operating systems.

In the background, I'm writing Java code to implement AWS tools and services. I forgot how much fun Java can be.
