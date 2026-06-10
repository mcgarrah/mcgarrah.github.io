---
title: "Migrating 16 Domains from SquareSpace to Porkbun — Part 2: The Sprint Finish"
image: /assets/images/og/name-service-registrars-part-2.png
layout: post
date: 2026-06-10
last_modified_at: 2026-06-10
categories: [technical, infrastructure]
tags: [dns, domains, porkbun, squarespace, migration, homelab, automation, email]
excerpt: "With several domains approaching renewal at SquareSpace, I pushed through the remaining transfers in a rush week. Fifteen of sixteen domains now live at Porkbun — only mcgarrah.org remains, deliberately held back until I have a proper weekend to migrate its 25+ DNS records without breaking production services."
description: "Part 2 of the SquareSpace to Porkbun domain migration. Completing the transfer of 15 out of 16 domains in a rush week before renewal deadlines, dealing with email forwarding without wildcard support, and why mcgarrah.org stays behind until the Executive MBA wraps up."
seo:
  type: BlogPosting
  date_published: 2026-06-10
  date_modified: 2026-06-10
---

Sometimes the best migration strategy is "renewals are coming, just move." Several domains were approaching their SquareSpace renewal dates in June, and paying full-year renewal to a registrar I was actively leaving felt like burning money. So this week became a sprint: get everything transferred before the charges hit, deal with the rough edges after.

> "Done is better than perfect — unless you're migrating a domain with 25 DNS records serving production traffic."

This is Part 2. [Part 1](/name-service-registrars/) covered the evaluation, batching strategy, and first nine transfers. This covers the final push — and the one domain I'm deliberately leaving behind.

<!-- excerpt-end -->

## The Urgency

The original plan from Part 1 was methodical: batch by renewal date, spread costs, migrate carefully. That plan assumed I'd have steady free time across several months. Reality intervened — between the Executive MBA coursework at UNCW and a full workload at Envestnet, those careful weekends never materialized. Then June arrived, and suddenly mcgarware.com (June 9), phonemes.org (June 16), and darkmagic.org (August 16) were all staring me down.

Renewing at SquareSpace just to transfer later would mean paying twice for the same year. The math was simple: move them now or eat the cost.

## What Got Migrated This Week

| Domain | Transfer Date | New Expiration | Notes |
|--------|--------------|----------------|-------|
| mcgarware.com | Jun 2026 | Jun 9, 2027 | Legacy domain, dead server records cleaned up |
| phonemes.org | Jun 2026 | Jun 16, 2027 | Email forwarding configured |
| darkmagic.org | Jun 2026 | Aug 16, 2027 | Legacy domain, minimal records |
| mcgarrah.dev | Jun 2026 | Mar 4, 2028 | Mailgun email retained |
| mcgarrah.us | Jun 2026 | Sep 22, 2028 | URL forwarding reconfigured |
| mcgarrah.app | Jun 2026 | Mar 4, 2029 | Mailgun email retained |

**Also: phonemes.biz** — let expire as planned. No transfer, no renewal. One less domain to manage.

**Updated totals: 15 of 16 domains at Porkbun (93.75% complete)**

## The Transfer Process — Abbreviated

Having done this nine times already in Batch 1 and 2, the process was mechanical:

1. Export DNS records from SquareSpace WebUI (copy/paste — still no export button)
2. Request transfer authorization code from SquareSpace
3. Wait for auth code email (24-48 hours)
4. Initiate transfer at Porkbun with auth code
5. Contact Porkbun support to request accelerated transfer
6. Respond to verification email
7. Recreate DNS records at Porkbun
8. Verify propagation

The bottleneck remained the same: SquareSpace's initial 24 hour auth code delivery and the 5-day hold unless you contact their support for an accelerated transfer process which cuts that hold to round trip email responses, but I was still at the mercy of email round-trips, catching a support person and dealing with multiple domains simultaneously. Hectic but with organization, it is manageable.

### Credit Where It's Due: SquareSpace Support

I want to be clear — SquareSpace's support team made this migration painless. Their chat and email support were responsive and genuinely helpful in accelerating the transfers. Get someone on the chat, set up the email verification to confirm ownership, and the transfers move quickly. No obstruction, no retention tricks, no guilt trips about leaving.

My issue with SquareSpace is architectural (no API, no DNS export, no automation hooks), not operational. Their support team is competent and professional. I'd use them again — and would happily recommend them for a consulting client — anytime the walled garden isn't a constraint. If your requirements are "reliable registrar with good support and you'll manage DNS through the web UI," SquareSpace is fine. It's only when you need programmatic access that the model breaks down.

No animosity here. That's more than I can say about certain other hosting providers that turned domain exits into adversarial processes.

### Porkbun's Inbound Experience

Porkbun has a greased track for incoming transfers. The process is well-designed, the UI is clear, and everything just works. Auth code goes in, payment processes, domain appears in your account, DNS management is immediately available. No complaints.

## Dead Record Cleanup

This batch was an opportunity to clean house. Several domains had legacy records pointing to 162.192.161.17 — a server that hasn't been online in years. Rather than faithfully recreating dead records at Porkbun, I dropped them:

**Records NOT migrated (intentionally):**
- Wildcard A records pointing to dead servers (mcgarware.com, darkmagic.org)
- Root A records pointing to the same dead IP
- All `_domainconnect` CNAME records (registrar-specific, irrelevant at Porkbun)
- SquareSpace forwarding records for mcgarrah.us (replaced with Porkbun URL forwarding)
- Custom mail server MX records for mcgarware.com and darkmagic.org (servers offline)

Carrying dead DNS records forward is how you accumulate security debt. Wildcard A records pointing to an IP you don't control are an open invitation for subdomain takeover attacks.

## Email Forwarding at Porkbun

The biggest operational change: moving off Mailgun for the simple forwarding domains and onto Porkbun's built-in email forwarding.

**The good:** Porkbun includes email forwarding for free. Twenty aliases per domain, which covers my needs comfortably. Setting up `michael@phonemes.org → mcgarrah@gmail.com` and `mcgarrah@phonemes.org → mcgarrah@gmail.com` took about thirty seconds in their UI.

**The annoying:** No wildcard forwarding. Mailgun's catch-all meant any address `*@domain.com` landed in my inbox. Porkbun requires explicit aliases. For domains where I only ever receive mail at one or two addresses, this is fine — 20 aliases is generous. But for domains where I've historically handed out unique addresses to different services (the `servicename@domain.com` pattern for tracking who sells your email), I'll need to enumerate those aliases manually.

**The pragmatic decision:** For domains still running Mailgun (mcgarrah.dev, mcgarrah.us, mcgarrah.app), I'm keeping it in place for now while I evaluate whether those domains actually *need* wildcard forwarding. The honest answer is probably "no" — I'll audit each one and likely end up replacing Mailgun with Porkbun aliases on most of them. Twenty aliases per domain is generous enough to cover the addresses that actually receive mail, and eliminating Mailgun removes an external dependency and simplifies the DNS configuration.

## The One That Stays Behind: mcgarrah.org

The primary domain isn't moving yet. The [DNS records reference](/assets/data/domain-migration/dns-records-reference.txt) shows why — 25+ records across:

- **GitHub Pages** — 4 A records, www CNAME, challenge TXT (this blog)
- **Mailgun email** — MX, SPF, DKIM for root domain
- **DigitalOcean apps** — nutrition, quiz, shiny-quiz subdomains
- **Nutrition subdomain email** — separate MX, SPF, DKIM, DMARC records
- **Legacy and verification records**

This isn't a "transfer and see what breaks" domain. This is a "block out a Saturday, have a rollback plan, and test every service" domain. Any mistake takes this blog offline, breaks email delivery, and disconnects four hosted applications simultaneously.

The renewal isn't until August 2, 2027. There's no financial pressure. I'm holding this until the Executive MBA wraps up and I can dedicate a proper weekend to the migration without competing priorities. The checklist from Part 1 still applies — I just need the focus time to execute it carefully.

## Current State

| Domain | Registrar | Email | Status |
|--------|-----------|-------|--------|
| mathomancer.com | Porkbun ✅ | Porkbun forwarding | Complete |
| mathomancy.com | Porkbun ✅ | Porkbun forwarding | Complete |
| brainyzone.com | Porkbun ✅ | Porkbun forwarding | Complete |
| brainyzone.org | Porkbun ✅ | Porkbun forwarding | Complete |
| cshensley.com | Porkbun ✅ | Porkbun forwarding | Complete |
| brainyz.one | Porkbun ✅ | — | Complete |
| brainyzone.app | Porkbun ✅ | — | Complete |
| brainyzone.net | Porkbun ✅ | — | Complete |
| brainyzone.us | Porkbun ✅ | — | Complete |
| mcgarware.com | Porkbun ✅ | Porkbun forwarding | Complete |
| phonemes.org | Porkbun ✅ | Porkbun forwarding | Complete |
| darkmagic.org | Porkbun ✅ | Porkbun forwarding | Complete |
| mcgarrah.dev | Porkbun ✅ | Mailgun | Complete |
| mcgarrah.us | Porkbun ✅ | Mailgun | Complete |
| mcgarrah.app | Porkbun ✅ | Mailgun | Complete |
| phonemes.biz | — | — | Expired (abandoned) |
| **mcgarrah.org** | **SquareSpace** | **Mailgun** | **Pending — migrate last** |

## Lessons From the Rush

**Batch transfers create email race conditions.** When you're moving six domains in parallel and each has its own auth code email and verification email, it's easy to miss a step. I tracked each domain's transfer state in a simple checklist — without it, I'd have lost track of which domains were waiting on auth codes versus waiting on verification responses.

**Dead records are easier to drop during migration than after.** Once records exist at the new registrar, there's psychological resistance to deleting them ("what if something needs it?"). During transfer is the natural audit point — if you can't explain what a record does, don't recreate it.

**Porkbun's 20-alias limit is fine for personal domains.** I was initially concerned about losing Mailgun's catch-all capability. In practice, I receive email at 2-3 addresses per domain. Twenty aliases is more than generous. The Forward Email evaluation I was considering in a [draft post](/email-forwarding-evaluation/) may not be necessary at all for most of these domains.

**The accelerated transfer process is reliable.** Every time I contacted Porkbun support, the verification email arrived within hours and the transfer completed the same day. Their support team is responsive and the process is straightforward. SquareSpace's chat support deserves equal credit — they facilitated every transfer without friction once I got someone on the line.

## What's Next

1. **mcgarrah.org migration** — Blocked until I have a clear weekend. Target: after Executive MBA coursework concludes. Full rollback plan, service-by-service verification, pre-staged DNS records at Porkbun ready to activate.

2. **Porkbun API automation** — With 15 domains now at Porkbun, automating DNS updates via their API is the next step. This enables the cert-manager DNS-01 challenges and external-dns integration that motivated this entire migration.

3. **Email consolidation** — Evaluating Mailgun on each remaining domain to determine if wildcard forwarding is actually needed. Most likely outcome: replace Mailgun with Porkbun aliases on domains that only receive mail at a handful of known addresses. Keep Mailgun only where I genuinely need catch-all or outbound sending capability.

The migration that started as a careful multi-month project ended as a one-week sprint driven by renewal deadlines. Not how I planned it, but the result is the same: vendor lock-in eliminated, API access gained, and the path to DNS automation is clear. One domain remains, and it'll get the careful migration it deserves — just not this week.

---

## References

- [Part 1: Migrating 16 Domains from SquareSpace to Porkbun](/name-service-registrars/) — Original migration article with full strategy and tooling
- [Complete DNS records reference](/assets/data/domain-migration/dns-records-reference.txt) — Full record exports for all domains
- [Porkbun Email Forwarding](https://porkbun.com/products/email_forwarding) — Free forwarding service details
- [Porkbun API Documentation](https://porkbun.com/api/json/v3/documentation) — REST API for DNS automation
