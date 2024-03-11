---
title:  "Link Aggregated (LAG) and LACP NIC Bonding"
layout: post
published: false
---

# LAG and LACP... what is the difference?

Network Bonding, Trunking (not VLAN trunking), and a variety of other names for Link Aggregating (LAG) network channels together to get redundancy or increased throughput. LAG is the bringing together of network ports while LACP is a protocol(?) for keeping those ports automatically managed for outages and misconfigurations. You can do LAG without LACP.

Think of the network ports as lanes in a highway...  each lane is capped at 70mph (or 112 kph) per car but I cannot get one (1) car to go faster than 70mph but I can have two lanes with two cars going 70mph at the same time in different lanes. In that case, if both cars hold four passengers, I can get a theoretical eight (8) persons moved in half the time with both cars rather than four (4) person in one car in one lane. The volume of traffic is higher. You can also configure for redundancy if one of the lanes goes down but at a cost of throughput. A stream of cars is limited by lane to the speed limit but multiple lanes opens us up to move content being moved at one time.

This same idea happens with LAG. The difference is convert car traffic lanes to 1Gbps network cables. We also convert passengers to network frames or collections of bits to push across the network. So in the above two lane highway, we have two 1Gbps network streams that can push or pull frames across the network cable. This makes it so that we effectively can transport twice the content across the network.

Now for the next step which is how do we determine that a lane is available and open for transport. For this we have rules for moving cars in a direction and speed. LACP is a set of rules for the network lanes and makes sure they are ready for traffic. Both ends of the network must agree that they are connected. With LACP, we can also build in high availability so that we can use both lanes but in the event of an emergency that blocks a lane, we can convert them 

So LAG is the multiple network streams and LACP are the rules to make sure those network streams are ready or available for usage.

We can complicate things to go beyond the analogy of cars and taffic to including highly available networks where we can re-route traffic on networks to keep them up in the event of one network cable going down. Another thing that LAG does is allow for traffic to go in either direction to push or pull the content.


[ServerFault Article](https://serverfault.com/a/569724)
    
My understanding of network bonding is that you cannot exceed the link speed of the member interfaces in one connection. A connection will stick to one interface in the bond after it is established.

However, connections are now split between the two interfaces. If you were to have two connections running from server A to server B, then the connections shouldn't start bottle-necking each other as far as bandwidth goes because they will be traveling across different interfaces. Your total bandwidth using multiple connections should be 2Gb/s, but each connection will be limited to a maximum of 1Gb/s.

[ServerFault Article](https://serverfault.com/questions/569060/link-aggregation-lacp-802-3ad-max-throughput/569125#569125)
    
A quick and dirty explanation is that a single line of communication using LACP will not split packets over multiple interfaces. For example, if you have a single TCP connection streaming packets from HostA to HostB it will not span interfaces to send those packets. I've been looking at LACP a lot here lately for a solution we are working on and this is a common misconception that 'bonding' or 'trunking' multiple network interfaces with LACP gives you a "throughput" of the combined interfaces. Some vendors have made proprietary drivers that will route over multiple interfaces but the LACP standard does not from what I've read. Here's a link to a decent diagram and explanation I found from HP while searching on similar issues: http://www.hp.com/rnd/library/pdf/59692372.pdf

https://community.hpe.com/t5/aruba-provision-based/procurve-2810-24g-trunking-lacp-setup-for-newbie/td-p/5899089

