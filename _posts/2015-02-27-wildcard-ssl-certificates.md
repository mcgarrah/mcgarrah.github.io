---
title:  "Wildcard SSL Certificates"
layout: post
categories: technical
---

I’m beginning to setup enough infrastructure that a wildcard certificate would be nice but I’m uninterested in paying several hundred dollars a year for that certificate. The free certs that used to be around just are not there anymore so far as I can see. My goal is to setup SSL certificates for both my email server and all the virtual host web sites I’m hosting under my mcgarrah.org domain for less than a hundred dollars a year.

<!-- excerpt-end -->

I looked at the cheaper single shot $5 certs but with the proliferation of domains and sub-domain under those that I own (brainyzone, mcgarrah, darkmagic, and several others), this approach will only lead to heartache and an empty wallet.  Thus the wildcard certificate. This trend may only get worse as Google has started their Domain services making it easier and cheaper for me to buy domains.

The vendor I was evaluating was StartSSL [https://www.startssl.com/](https://www.startssl.com/) and a few others. It seemed like the cheapest and least objectionable.

All that got turned over when the “Let’s Encrypt” offering [https://letsencrypt.org/](https://letsencrypt.org/) hit the scene. It is making me think about holding off on buying the certificate. I don’t need the certificate right this minute so I’m okay with waiting a month or two and see how this works out. Take a look at them if you are thinking about buying certificates and can wait a few months.

The CA’s out there have something to worry about with this new offering.
