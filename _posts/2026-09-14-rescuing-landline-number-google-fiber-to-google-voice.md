---
layout: post
title: "Rescuing a Landline Number: Migrating Out of Google Fiber and Into Google Voice"
image: /assets/images/og/rescuing-landline-number-google-fiber-to-google-voice.png
categories: [personal, technical]
tags: [google, google-fiber, google-voice, esim, number-porting, voip, telecom, tello]
excerpt: "Google Fiber quietly dropped SMS support on its home phone service and reassigned my number to a random replacement. Porting a VoIP landline directly into Google Voice isn't allowed, so I bridged it through a temporary mobile eSIM line to rescue a number tied to decades of professional history."
description: "How I recovered a 15-year-old phone number after Google Fiber changed its telephony backend and broke SMS -- using a temporary Tello eSIM as a mobile bridge to satisfy Google Voice's carrier-type porting requirements."
date: 2026-09-14
last_modified_at: 2026-09-14
seo:
  type: BlogPosting
  date_published: 2026-09-14
  date_modified: 2026-09-14
---

Losing a primary phone number tied to decades of professional history, resumes, and account recovery flows is a technical emergency, not a mild inconvenience. It's the number on file with banks, with two-factor recovery paths, with people who haven't updated their contacts since a job I left years ago. When Google Fiber changed its home phone backend and quietly dropped SMS support -- and a backend glitch forced an unwanted random number reassignment on top of it -- my number, `919-807-1057`, ended up stranded on a deprecated VoIP endpoint with no straightforward way off it.

<!-- excerpt-end -->

Google Voice won't accept a direct port from a landline or fixed VoIP provider. That restriction turned what should have been a five-minute porting form into a multi-step migration across three different carrier systems.

## The Technical Roadblock: VoIP vs. Mobile Classification

Google Fiber phone numbers live on a traditional VoIP carrier network. Google Voice's porting pipeline checks the number's carrier-type classification in the Local Number Portability (LNP) database, and it only accepts inbound ports from numbers classified under a mobile carrier block. Submit a port request straight from a landline or fixed VoIP number, and it gets rejected immediately on carrier type -- no amount of retrying the form changes that outcome.

To get the number in front of Google Voice at all, it first had to exist on real mobile infrastructure. That meant introducing an intermediate carrier hop: land the number on a mobile network first, let the LNP database catch up, then port from there.

## The Migration Path

**1. Secure the account parameters.** Before touching anything, I logged into the Google Fiber account portal to pull the exact account number and generate a valid port-out PIN. The service has to stay active through this step -- cancelling early releases the number back into the pool and closes the window for good.

**2. Bridge through a mobile eSIM.** I had a spare eSIM slot on a Galaxy S23 Ultra, so I activated a low-cost line with Tello, a mobile carrier riding on major cellular infrastructure. Instead of keeping Tello's assigned placeholder number, I immediately filed a port-in request against it using the Fiber account number and PIN, moving `919-807-1057` onto Tello.

**3. Wait for LNP propagation.** Once the carrier-to-carrier port cleared, the number's record in the LNP database now showed a mobile carrier block. That's the only thing Google Voice's porting form actually checks -- it doesn't care that the line spent all of ten minutes on Tello before moving again.

**4. Port into Google Voice.** With the classification fixed, I submitted the port request through [voice.google.com/porting](https://voice.google.com/porting), paid the one-time $20 porting fee, and anchored the Voice account to a separate mobile number for verification (Google Voice requires a working number to receive porting status updates and as a fallback contact during the transition). The port cleared a few hours later once NPAC (Number Portability Administration Center) finished routing synchronization.

## The Takeaway

The eSIM bridge is the whole trick: it's not a real carrier relationship, just a brief stop that changes the number's classification in the LNP database so the next port is one Google Voice will actually accept. The number is back on modern infrastructure now, with full SMS, call history, and voicemail -- and none of the professional contacts or account-recovery flows built around it over the years had to change.

If you're stuck in the same spot -- a landline or fixed VoIP number Google Voice won't take directly -- the fix isn't a support ticket, it's routing around the carrier-type check with a throwaway mobile line you control long enough to make the classification stick.
