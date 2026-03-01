---
title: "Email Forwarding for 16 Domains: Evaluating Forward Email After Porkbun Migration"
layout: post
date: 2026-02-07
categories: [technical, homelab, email]
tags: [porkbun, forward-email, mailgun, email-forwarding, dns, mx-records]
excerpt: "After migrating 16 domains from SquareSpace to Porkbun, evaluating email forwarding options. Comparing Porkbun's built-in service, Mailgun (current), and Forward Email for cost-effective, privacy-focused email routing."
published: false
---

## The Email Forwarding Challenge

After [migrating 16 domains from SquareSpace to Porkbun](/name-service-registrars/), I need to decide on an email forwarding strategy. At SquareSpace, I used **Mailgun** for MX records and email forwarding as it was free and easy to use. Now at Porkbun, I have several options to evaluate.

<!-- excerpt-end -->

## Current State: Mailgun

**Status:** Operational on 9 migrated domains  
**Cost:** Free tier (limited sends)  
**Configuration:** MX records pointing to mxa.mailgun.org and mxb.mailgun.org

Mailgun has worked reliably for years, providing:

- Email forwarding to Gmail/Yahoo
- SPF and DKIM configuration
- SMTP sending capability
- API access for automation

**Example configuration (mcgarrah.dev):**

```text
@ MX 10 mxa.mailgun.org
@ MX 10 mxb.mailgun.org
@ TXT "v=spf1 include:mailgun.org ~all"
k1._domainkey TXT "k=rsa; p=MIGfMA0GCS..."
```

## Email Forwarding Options at Porkbun

### Option 1: Porkbun Email Forwarding (Free)

**Cost:** $0.00  
**Limitations:**

- 20 email forwarding addresses per domain
- No wildcard/catch-all support (`*@domain.com`)
- Specific addresses only

**Quote from Porkbun:**
> "Email Forwarding - Forward email from your domain to an existing inbox. Did we mention it's free? Includes: 20 Email forwarding addresses"

**Verdict:** Too limited for 16 domains with multiple aliases per domain. I might limp along with it short term.

### Option 2: Porkbun Email Hosting ($2/month)

**Cost:** $2.00/month per domain = $384/year for 16 domains  
**Features:**

- 10 GB storage per user
- Webmail, POP3, and IMAP access
- Full mailbox hosting

**Verdict:** Expensive for simple forwarding needs. Overkill when I just need to forward to existing Gmail/Yahoo accounts.

### Option 3: Porkbun + Proton Mail Partnership ($6/month)

**Cost:** $6.00/month per domain = $1,152/year for 16 domains  
**Features:**

- 15 GB storage per user
- 3 custom email domains
- Secure calendar
- Cloud storage

**Verdict:** Premium features I don't need. Far too expensive for forwarding.

### Option 4: Keep Mailgun (Current Solution)

**Cost:** $0.00 (free tier)  
**Limits:** 100 emails/day per domain

**Features:**

- RESTful email APIs and SMTP relay
- 1 custom sending domain per account
- Tracking, analytics, and webhooks
- 2 API keys
- Email analytics and reporting
- 1 day log retention
- 1 inbound route
- Ticket support

**Limitations:**

- **100 emails/day limit** (3,000/month) - restrictive for active domains
- Only 1 custom domain per free account (need 16 accounts for 16 domains)
- Requires manual DNS configuration per domain
- No catch-all without paid plan
- 1 day log retention only

**Verdict:** Free tier's 100 emails/day limit and 1-domain restriction makes it impractical for 16 domains. Would need 16 separate Mailgun accounts.

### Option 5: ImprovMX

**Cost:** $9/month = $108/year (Pro plan)  
**Free tier:** 10 emails/day per domain

**Pro Plan Features:**
- Unlimited email aliases
- Unlimited domains
- SMTP sending
- Email logs and analytics
- Priority support

**Limitations:**
- Free tier: Only 10 emails/day (too restrictive)
- Pro plan: $108/year (3x more than Forward Email)
- No encrypted DNS records option

**Verdict:** More expensive than Forward Email Enhanced ($36/year) with similar features. Free tier's 10 emails/day limit is too restrictive.

### Option 6: Migadu

**Cost:** $19/year (Micro) to $90/year (Standard)  
**Limits:** 20 emails/day (Micro), 100 emails/day (Mini), 1000 emails/day (Standard)

**Micro Plan ($19/year):**
- 10 mailboxes
- 5 GB storage
- 20 outgoing emails/day
- 200 incoming emails/day

**Standard Plan ($90/year):**
- 50 mailboxes
- 30 GB storage
- 1000 outgoing emails/day
- 2000 incoming emails/day

**Limitations:**
- Daily email limits on all tiers
- More expensive than Forward Email
- Full mailbox hosting (overkill for forwarding)

**Verdict:** Better suited for full email hosting than simple forwarding. More expensive than Forward Email Enhanced with daily limits.

### Option 7: Forward Email (Evaluation)

**Cost:** $0.00 (free) or $3.00/month (enhanced)  
**Features:** See detailed analysis below

## Forward Email: Detailed Evaluation

[Forward Email](https://forwardemail.net) is an open-source, privacy-focused email forwarding service.

### Free Tier

**Cost:** $0.00/year  
**Unlimited domains:** All 16 domains supported

**Features:**

- DNS-based routing via TXT records
- MX records: `mx1.forwardemail.net` and `mx2.forwardemail.net`
- Open-source codebase
- No vendor lock-in

**Privacy Concern:**

- Forwarding addresses visible in **cleartext** DNS TXT records
- Anyone can query DNS and see destination email addresses
- Example: `forward-email=admin:user@gmail.com`

**Technical Implementation:**

```text
# MX Records
@ MX 10 mx1.forwardemail.net
@ MX 20 mx2.forwardemail.net

# TXT Record - Specific addresses (CLEARTEXT - privacy issue)
@ TXT "forward-email=admin:user@gmail.com,contact:user@yahoo.com"

# TXT Record - Wildcard/catch-all (CLEARTEXT - privacy issue)
@ TXT "forward-email=*:user@gmail.com"

# Verification
@ TXT "forward-email-site-verification=abc123xyz"
```

**Wildcard/Catch-All Support:**
- ✅ **Wildcard IS supported** on free tier
- Uses cleartext TXT record: `forward-email=*:user@gmail.com`
- Anyone can query DNS and see your destination address

**Limitations:**
- No SMTP sending
- Cleartext email addresses in DNS (privacy concern)
- Manual DNS management per domain

### Enhanced Tier ($3/month)

**Cost:** $3.00/month = $36.00/year (covers ALL 16 domains)  
**This is the game-changer.**

**Features:**
- **Encrypted TXT records:** Destination addresses hidden from DNS queries (vs cleartext on free tier)
- **Wildcard support:** `*@domain.com` catch-all routing (same as free, but encrypted)
- **SMTP sending:** Reply "as" your domain through Gmail/Yahoo (not available on free tier)
- **Centralized dashboard:** Manage all 16 domains in one UI (vs manual DNS edits)
- **No per-domain fees:** $36/year total, not per domain

**Privacy Solution:**
```bash
# MX Records (same)
@ MX 10 mx1.forwardemail.net
@ MX 20 mx2.forwardemail.net

# TXT Record (ENCRYPTED)
@ TXT "forward-email=encrypted:a8f3b2c9d1e4f5g6h7i8j9k0"

# Verification
@ TXT "forward-email-site-verification=abc123xyz"
```

**Wildcard Example (works on both free and enhanced tiers):**
- `admin@mcgarrah.org` → user@gmail.com
- `contact@mcgarrah.org` → user@gmail.com
- `anything@mcgarrah.org` → user@gmail.com
- All handled by single `*@domain.com` rule

**Key Difference:** Free tier uses cleartext TXT record, enhanced tier encrypts it.

## Cost Comparison

| Solution | Cost/Year | Domains Covered | Wildcard | SMTP | Privacy |
|----------|-----------|-----------------|----------|------|----------|
| **Porkbun Free** | $0 | 16 | ❌ | ❌ | ⚠️ Limited |
| **Porkbun Hosting** | $384 | 16 | ✅ | ✅ | ✅ |
| **Porkbun + Proton** | $1,152 | 16 | ✅ | ✅ | ✅ |
| **Mailgun Free** | $0 | 1 per account | ❌ | ⚠️ 100/day | ✅ |
| **ImprovMX Free** | $0 | Unlimited | ✅ | ❌ | ⚠️ 10/day limit |
| **ImprovMX Pro** | $108 | Unlimited | ✅ | ✅ | ✅ |
| **Migadu Micro** | $19 | Unlimited | ✅ | ✅ | ⚠️ 20/day limit |
| **Migadu Standard** | $90 | Unlimited | ✅ | ✅ | ⚠️ 1000/day limit |
| **Forward Email Free** | $0 | 16 | ✅ Cleartext | ❌ | ❌ Cleartext |
| **Forward Email Enhanced** | $36 | 16 | ✅ | ✅ | ✅ Encrypted |

**Winner:** Forward Email Enhanced at $36/year provides encrypted wildcard, SMTP, and privacy for all 16 domains.

**Runners-up:**
- **Migadu Micro ($19/year):** Cheaper but has 20 emails/day limit
- **ImprovMX Pro ($108/year):** 3x more expensive with similar features

**Free Tier Alternative:** Forward Email free tier supports wildcard catch-all for all 16 domains at $0/year, but destination addresses are visible in cleartext DNS records. Good for testing or non-sensitive use cases.

**Note:** Mailgun's free tier only supports 1 custom domain per account with 100 emails/day limit. Managing 16 domains would require 16 separate Mailgun accounts, making it impractical compared to Forward Email's flat-fee model.

## Migration Strategy

### Phase 1: Pilot Test (1 domain)

**Domain:** mathomancer.com (low-risk, minimal email traffic)

**Steps:**
1. Sign up for Forward Email Enhanced ($3/month)
2. Configure MX records in Porkbun DNS
3. Add encrypted TXT record
4. Add verification TXT record
5. Test email forwarding for 1 week
6. Verify wildcard routing works
7. Test SMTP sending via Gmail

**Rollback Plan:** Revert to Mailgun MX records if issues arise

### Phase 2: Low-Risk Domains (8 domains)

**Domains:** mathomancy.com, brainyzone.com, brainyzone.org, brainyzone.net, brainyzone.us, brainyzone.app, brainyz.one, cshensley.com

**Timeline:** 1 week after successful pilot

### Phase 3: Medium-Risk Domains (6 domains)

**Domains:** mcgarware.com, phonemes.org, darkmagic.org, mcgarrah.dev, mcgarrah.us, mcgarrah.app

**Timeline:** 2 weeks after Phase 2

### Phase 4: High-Risk Domain (1 domain)

**Domain:** mcgarrah.org (primary domain, highest complexity)

**Timeline:** 1 month after Phase 3, after all others proven stable

**Special considerations:**
- Multiple subdomains with email (nutrition.mcgarrah.org)
- Active DigitalOcean apps
- GitHub Pages hosting
- Migrate LAST

## Technical Implementation

### DNS Configuration (Per Domain)

**Step 1: Update MX Records**
```bash
# Remove old Mailgun MX records
# Add Forward Email MX records
@ MX 10 mx1.forwardemail.net
@ MX 20 mx2.forwardemail.net
```

**Step 2: Add Encrypted TXT Record**
```bash
# Generated from Forward Email dashboard
@ TXT "forward-email=encrypted:a8f3b2c9d1e4f5g6h7i8j9k0"
```

**Step 3: Add Verification TXT Record**
```bash
# Unique per domain from Forward Email
@ TXT "forward-email-site-verification=abc123xyz"
```

**Step 4: Remove Old Mailgun Records**
```bash
# Remove SPF record
@ TXT "v=spf1 include:mailgun.org ~all"

# Remove DKIM record
k1._domainkey TXT "k=rsa; p=..."
```

### Automation Opportunity

**Porkbun API + Forward Email API:**

Future enhancement: Script to automate DNS updates across all 16 domains.

```bash
#!/bin/bash
# Automate Forward Email MX record deployment
# Uses Porkbun API for DNS updates

for domain in "${DOMAINS[@]}"; do
  # Add MX records via Porkbun API
  curl -X POST https://porkbun.com/api/json/v3/dns/create/$domain \
    -d '{"apikey":"$API_KEY","secretapikey":"$SECRET","type":"MX","content":"mx1.forwardemail.net","prio":10}'
  
  # Add encrypted TXT record from Forward Email
  # (requires Forward Email API integration)
done
```

## Decision Matrix

**Choosing Forward Email Enhanced if:**

- ✅ Need wildcard/catch-all for multiple domains
- ✅ Want privacy (encrypted DNS records)
- ✅ Need SMTP sending capability
- ✅ Managing 10+ domains (cost-effective)
- ✅ Prefer open-source solutions

**Sticking with Mailgun if:**

- ✅ Only 1-2 domains (free tier supports 1 domain per account)
- ✅ Low email volume (under 100/day per domain)
- ✅ Need advanced API features
- ✅ Require detailed analytics
- ⚠️ Willing to manage multiple accounts for multiple domains

**Using Porkbun Free if:**

- ✅ Only need 1-2 domains
- ✅ Less than 20 addresses per domain
- ✅ No wildcard needed
- ✅ Privacy not a concern

**Using ImprovMX Pro if:**

- ✅ Need email logs and analytics
- ✅ Willing to pay $108/year
- ⚠️ No daily email limits concern

**Using Migadu if:**

- ✅ Need full mailbox hosting (not just forwarding)
- ✅ Low email volume (under daily limits)
- ✅ Want cheaper option than Forward Email ($19/year vs $36/year)
- ⚠️ Can accept 20-1000 emails/day limits

## Next Steps

- [ ] Sign up for Forward Email Enhanced ($3/month trial)
- [ ] Configure mathomancer.com as pilot domain
- [ ] Test email forwarding for 1 week
- [ ] Verify wildcard routing (`test123@mathomancer.com`)
- [ ] Test SMTP sending via Gmail
- [ ] Document any issues or limitations
- [ ] Proceed with Phase 2 if successful
- [ ] Migrate remaining 15 domains over 6-8 weeks

## Conclusion

For 16 domains requiring email forwarding, **Forward Email Enhanced at $36/year** provides the best value:

- **Cost:** 10x cheaper than Porkbun hosting ($384/year)
- **Privacy:** Encrypted DNS records (unlike free tier)
- **Flexibility:** Wildcard support for all domains
- **Features:** SMTP sending capability
- **Scalability:** Unlimited domains for flat fee

The free tier's cleartext DNS records are a dealbreaker for privacy. The enhanced tier solves this while adding wildcard and SMTP for just $3/month total.

Mailgun's free tier limitation of 1 custom domain per account and 100 emails/day makes it unsuitable for managing 16 domains. Forward Email's flat-fee model ($36/year for unlimited domains) is the clear winner for multi-domain email forwarding.

## References

- [Forward Email Documentation](https://forwardemail.net/en/faq)
- [Forward Email Pricing](https://forwardemail.net/en/pricing)
- [ImprovMX Pricing](https://improvmx.com/pricing)
- [Migadu Pricing](https://migadu.com/pricing/)
- [Porkbun Email Services](https://porkbun.com/products/email)
- [Mailgun Pricing](https://www.mailgun.com/pricing/)
- [Migrating 16 Domains to Porkbun](/name-service-registrars/) (previous article)
