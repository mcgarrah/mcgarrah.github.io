---
title:  "NetApp iSER Performance Evaluation Project Continuation"
layout: post
categories: technical
---

NC State University - Computer Science

Senior Design Project

[“Senior Design: NetApp iSCSI with RDMA/TOE” (Fall 2010 Capstone Project)](https://web.archive.org/web/20210416110703/https://www.csc2.ncsu.edu/sdc/students/information/projects/f2k10.php#p3)

Aug 2010 - Dec 2010

Summary: Develop a methodology for 10Gbps iSCSI that utilized RDMA and TOE to reduce primary CPU and memory usage. Document and managed the project as a team leader. The resulting iSER implementation was utilized in a related NetApp Phd project at the University of Bangalore India.




## NetApp iSER Performance Evaluation Project Continuation

NetApp is a leading vendor of hardware and software to help customers store, manage, and protect data. NetApp clients have very high performance needs. They typically deal with petabytes of data and high-load systems. NetApp is constantly looking for ways to improve performance of their systems. Stated in simplest terms, this project is part of a continuing, year-long effort to evaluate a set of hardware and software technologies which promise to provide a more efficient mechanism to transfer data across a network. NetApp will use our analysis to determine value-added for different applications, which includes cloud computing and virtualization.

Below is a list of terms useful in understanding project goals:

SCSI: "Small Computer System Interface." This is an interface protocol used to access hard disk drives that has been around for many years.

iSCSI: SCSI over TCP/IP. This protocol is newer, and allows a computer to access SCSI devices located across a Storage Area Network (SAN). This type of application typically has high bandwidth and low latency performance requirements. iSCSI functions by opening a TCP connection over the network and exchanging commands and data. The computer that has the physical SCSI disk drives, and that accepts incoming iSCSI connections, is termed the "target". The computer that connects to the target in order to access SCSI devices is known as the "initiator".

iSCSI with TOE: iSCSI with "TCP Offload Engine". Typically TCP is implemented in the kernel, so the CPU carries its overhead. A home broadband connection might have a bandwidth of 30Mbps, which is considered slow by industry standards. The kernel implementation of TCP, then, does not affect network performance in such cases. This project, however, deals with 10 Gbps speeds - nearly 3,000 times faster than home use. In this kind of environment, the CPU's protocol handling adds a significant burden and degrades throughput. A newer technology known as "TCP Offload" was developed to take the TCP protocol and implement it in the hardware of the network adapter, thus relieving the CPU of this load.

DMA: "Direct Memory Access." This is a hardware mechanism in modern computers that allows some I/O devices to directly transfer blocks of data into main memory without the intervention of the CPU, thus freeing CPU cycles. This technology has been around for many years.

RDMA: "Remote Direct Memory Access." This technology takes DMA a step farther, and allows a remote device/computer to perform a DMA transfer across a network while avoiding constant CPU intervention on either end of the transfer. This is accomplished using certain protocols to negotiate DMA transfers, as well as hardware support to actually perform the data transfer using existing DMA hardware.

iSER: "iSCSI Extension for RDMA." This technology allows an iSCSI target/initiator pair to perform data transfer over the network without involving the CPUs of the nodes using an RDMA protocol. This relieves the CPU from copying large amounts of data from the network adapter's I/O buffers to main memory, saving even more CPU cycles than TOE alone. Also, since data does not remain in the network adapter's buffer for long, these buffers can be made significantly smaller than is necessary when using just TOE, decreasing costs and increasing scalability.

TOE: "TCP Offload Engine". See "iSCSI with TOE."

### Fall 2010 Project Statement

1. Using the configuration, setup information, and results documented by the Spring 2010 team, reproduce baseline performance runs to confirm that results are consistent with the previous team's results.
2. Incorporate multiple initiator target pairs into the configuration, and integrate the Cisco Nexus 5000 switch. Run the performance benchmark tests and compare to the baseline results, providing analysis of the results.
3. Configure the system to leverage multiple cores and run baseline performance runs, providing analysis of the results.

### Available project resources

Four Dell T3400 computers, each with:

* Quad Core Intel Processor with 1333Mhz FSB
* 8GB RAM
* Operating system: CentOS 5.3 (64-bit)
* Chelsio 10G optical network card, in a PCI-E x8 slot with Fiber Optic Cabling

Currently these four T3400 are assigned to two pairs, each pair containing a "target" and "initiator". The computers have been labeled as such. The Chelsio cards on each pair of computers are directly connected via fiber cable.

Two Dell PowerEdge 2950 servers, each with:

* Quad Core Intel Xeon E5405 with 2x6MB Cache 2.0Ghz 1333Mhz FSB
* 8GB RAM
* Operating system: Linux RHEL 5.3

One Cisco Nexus 5030 10Gbit Ethernet Switch

Two Dell D380 computers with NC State Realm Linux installations are available for team use. These are not intended as test bed machines.
