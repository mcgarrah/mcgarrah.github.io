---
title:  "AWS - Running Services Locally (a quick survey of products)"
layout: post
categories: personal aws cloudstack eucalyptus openstack virtualization
---

My first step was to review the major services we wanted to use on Amazon. They have a massive set of services available for use and some are not easily replicated without a major infrastructure and skill set to manage it. To give you some idea of the number of services here is a summary of the services and a quick reference as of August 2013.

### Amazon Web Services (AWS) as of August 2013

#### Compute & Networking
**EC2**    Virtual Servers in the Cloud
ELB    Elastic Load Balancing or Auto Scaling of services 
EMR   Hosted Hadoop Framework
VPC    Isolated Cloud Resources
Route 53   Scalable Domain Name System (DNS)
Direct Connect Dedicated Network Connection to AWS

#### Storage & CDN
**S3**    Scalable Storage in the Cloud
Glacier    Low-Cost Archive Storage in the Cloud
**EBS**    EC2 Block Storage Volumes
Import/Export  Large Volume Data Transfer
Storage Gateway Integrates on-premises IT environments with Cloud storage
CloudFront  Global Content Delivery Network (CDN)

#### Database
RDS   Managed Relational Database Service for MySQL, Oracle and SQL Server
DynamoDB   Fast, Predictable, Highly-scalable NoSQL data store
ElastiCache  In-Memory Caching Service
Redshift    Fast, Powerful, Fully Managed, Petabyte-scale Data Warehouse Service

#### Application Services
CloudSearch  Managed Search Service
**SWF**   Workflow service for coordinating application components
**SQS**   Message Queue Service
**SES**    Email Sending Service
**SNS**    Push Notification Service
FPS    Amazon Flexible Payments Service (FPS) is an API based payment service
Elastic Transcoder Easy-to-use scalable media transcoding

#### Deployment & Management 
Management Console Web-Based User Interface
**IAM**      Identity and Access Management (IAM) configurable access controls
**CloudWatch**   Resource and Application Monitoring
Elastic Beanstalk  AWS Application Container
CloudFormation  Templates for AWS Resource Creation
Data Pipeline   Orchestration Service for Periodic, Data-Driven Workflows
OpsWorks   DevOps Application Management Services
CloudHSM   Hardware-based Key Storage for Regulatory Compliance

The items above BOLDED are those we deemed important or critical to our project.

## PaaS (Platform as a Service)

I limited the search to the major players in the AWS private cloud market and ignored the non-AWS compatible options. AWS is the gold-standard of cloud services at this time. Other vendors are catching up to the services they offer.  Google, Yahoo, HP, Microsoft, and EMC/VMware are all attempting to gain traction and provide the services that Amazon currently offers. I don't see this changing in the near future but those options may improve as this market matures. Google in particular seems to want into this space and the EMC/VMWare has the [Pivotal](http://www.gopivotal.com/) initiative with partners. There are other players but Amazon owns this space right now.

With those requirements, [OpenStack](http://www.openstack.org/), [CloudStack](http://cloudstack.apache.org/) and [Eucalyptus](http://www.eucalyptus.com/) are the three major packages I reviewed. They are listed in order of least AWS services to greatest number of services replicated.  The clear winner was Eucalyptus from reviewing the documentation and frequenting the IRC channels for regular users using the products.

OpenStack has a very robust hypervisor management and API for supporting those services. There is a bolted on AWS API for EC2 that works for the most part until it comes into conflict with the way the OpenStack API functions. Reviewing the usage of OpenStack and participating in the community surrounding it, left me with little patience for this product. It was not a very open community of users and there seemed to be some hostility towards AWS compatibility. My goal is to implement an AWS compatible system so this group does not seem to align with that goal. Likewise their API support is limited to EC2 and a limited subset of other services to support EC2. The OpenStack Compute API is very similar to the AWS EC2 API so many people port between them as necessary. There are even some projects out to assist in this effort that don't appear to be very active now.  An older project by Canonical called [AWSOME](https://launchpad.net/awsome) (any web service over me) was supposed to bridge Amazon and OpenStack cloud environments.

As a side note, the OpenStack versus Eucalyptus debate has the feel of the almost religious debates that pervaded the Debian versus Ubuntu arguments several years ago. The free and open software debate is not my primary concern today but I understand the arguments about having long term freedom. Unfortunately, I need to implement something today and the [AWS API](http://aws.amazon.com/documentation/) is the closest thing to a standard we have for this technology right now. I am not ignorant of the risk that using Amazon controlled standards and Eucalyptus implements copies entails if they close the source but I have faith that a branch will emerge to continue the open source version if that happened like with MySQL and many other software packages over the years. Amazon is working hard to continue to innovate and others are pushing to catch up. So this will stay an active area not letting Amazon slow down. The chest beating between OpenStack and other cloud providers makes them less interesting to me.

CloudStack may gain traction now that it is under the Apache Foundation and separated from Citrix the makers of Xen. I hope they increase the number of services offered but as of today, they are not sufficient for our needs. They offer a limited EC2/S3 service without any of the other services that make AWS so interesting. If you are looking for just a virtual machines management system with an EC2 interface, then this will definitely serve your needs. One major advantage over Eucalyptus is that it offers support for additional hypervisors that the current Eucalyptus does support not including Xen, VMWare, and KVM. This could be the difference for some but was not a factor in our decision. The community was quite open and interested in new comers. If they offered more AWS services, I would have been happy with this product.

Eucalyptus which I began working with off the GitHub repository for the 3.3.0 release candidate contains a large number of complex moving parts. In a prior post on Eucalyptus, I gave a list of features that included the base EC2, S3, EBS, AMI, IAM, and the more recently added Autoscaling, Elastic Load Balancer, and Cloudwatch. This whole package was in flux while I was learning about it and building it so I had some additional self-imposed hurdles. The S3 support is lacking some features but is a decent implementing for storing small amounts of information and a relatively small number of files. It serves fine for storing [EMI (Eucalyptus Machine Images)](http://emis.eucalyptus.com/) or simple configuration data. The coverage of supported API is decent. Don't do something strange like use the [AWS DotNet SDK](http://aws.amazon.com/sdkfornet/) and you are likely to get it working fine. The EBS support works but requires some extra effort to create the initial images. Those issues are being worked on actively by Eucalyptus and you should see significant changes in the near future.

The EC2 support appears to be solid but is limited to the [Linux KVM hypervisor](http://www.linux-kvm.org/) only. There used to be support for Xen which was removed in the last couple of versions. Open source users have gotten it to work with Xen recently but it isn't in the main line support right now.

The S3 support is being bolstered internally in their Walrus service and with third party software like [Ceph](http://ceph.com/) and [Riak CS](http://basho.com/riak-cloud-storage/) (S3 compatibility with HA). These are ambitious additions to their existing systems and will likely take a few revisions to work out the issues. You can review their [road map](http://www.eucalyptus.com/eucalyptus-cloud/iaas/roadmap) to see about when they plan for these features.

There are a few options available for AWS replicated services run locally outside of Eucalyptus. I'll have a follow up post sometime in the next few days on a few of these that will include at least: S3, SQS, SNS, DynamoDB, RDS and SWF. These are services not offered or incomplete implementations on Eucalyptus.

Another post that I will flesh out will be about the shared storage used by Eucalyptus to allow for shared volumes between the various components of the system. Not having a NetApp or EMC storage device available made it necessary to learn a bit about free options in this space.

Please comment or ask questions.
