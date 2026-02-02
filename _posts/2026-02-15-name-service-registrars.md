---
title:  "Migrating 16 Domains from SquareSpace to Porkbun"
layout: post
date: 2026-02-15
excerpt: "Documenting the multi-week process of transferring 16 domains from SquareSpace to Porkbun in batches, managing costs, and dealing with transfer delays. Why Porkbun won for homelab domain management."
published: true
---

"He was in a bind 'cause he was way behind"
-- Charlie Daniels from "The Devil Went Down to Georgia"

## The Situation

I'm migrating 16 domains from SquareSpace (SS) to Porkbun (PB). These domains originally came from Google Domains before Google sold their registrar business to SquareSpace. The migration is slow and expensive, but necessary.

### The Transfer Process Challenges

**SquareSpace Delays:**
- 24-48 hours to receive transfer authorization codes via email
- Mandatory 5-day transfer hold with no apparent way to expedite
- Each delay multiplies across multiple domains

**Cost Management:**
- Each transfer requires 1-year renewal at Porkbun
- Migrating in batches by renewal date to spread costs
- Total migration cost: several hundred dollars

### Domain Inventory

All domains currently at SquareSpace, sorted by renewal date:

| Domain | Renewal Date | Batch | Risk Level | Notes |
|--------|--------------|-------|------------|-------|
| mathomancer.com | Mar 31, 2026 | 1 | Low | Email forwarding only, minimal traffic |
| mathomancy.com | Mar 31, 2026 | 1 | Low | Old site, little to no traffic |
| brainyzone.com | Apr 17, 2026 | 1 | Low | Email forwarding, minimal traffic |
| brainyzone.org | Apr 17, 2026 | 1 | Low | Email forwarding, minimal traffic |
| cshensley.com | May 8, 2026 | 1 | **Medium** | **Active website + email - son's resume site** |
| brainyz.one | May 17, 2026 | 2 | Low | Minimal usage |
| brainyzone.app | May 17, 2026 | 2 | Low | Minimal usage |
| brainyzone.net | May 17, 2026 | 2 | Low | Minimal usage |
| brainyzone.us | May 17, 2026 | 2 | Low | Minimal usage |
| phonemes.org | Jun 16, 2026 | 3 | **Medium** | **May have AWS demo site + email - needs investigation** |
| darkmagic.org | Aug 16, 2026 | 3 | Medium | Long-held domain, may have complexity |
| mcgarrah.dev | Mar 3, 2027 | 4 | Medium | Development projects |
| mcgarrah.us | Sep 22, 2027 | 4 | Medium | Forwards to blog.mcgarrah.org |
| mcgarrah.app | Mar 3, 2028 | 5 | Medium | Application projects |
| mcgarware.com | Jun 9, 2026 | 6 | High | Deferred to later batch |
| mcgarrah.org | Aug 2, 2027 | 6 | **High** | **Primary domain - highest risk, migrate last** |

**Migration Strategy:**
- **Batch 1 (Low Risk):** First 4 domains - email forwarding and old sites with minimal traffic
- **Batch 1 (Medium Risk):** cshensley.com - first active site with critical email and resume content
- **Batch 2 (Low Risk):** All "brain" domains - minimal usage
- **Batch 3 (Medium Risk):** phonemes.org - potential AWS demo site and email to investigate before migration
- **Batch 3 (Medium Risk):** darkmagic.org - long-held domain, potential complexity
- **Batch 4-5 (Medium Risk):** mcgarrah.dev, mcgarrah.us, mcgarrah.app - active but lower priority
- **Batch 6 (High Risk):** mcgarrah.org + mcgarware.com - primary domains, migrate last after gaining experience
- **Abandoning phonemes.biz** - letting it expire rather than renew/transfer
- Spreads cost over multiple months while building migration confidence

### Pre-Migration Investigation Needed

**phonemes.org:**
- [ ] Check AWS Console for active resources (EC2, S3, CloudFront, Route53)
- [ ] Search email for AWS account notifications related to phonemes.org
- [ ] Verify if email is configured (check MX records)
- [ ] Document any demo website URLs and functionality
- [ ] Identify AWS services that depend on domain DNS
- [ ] Plan AWS resource updates if DNS changes required

## Why Porkbun?

After evaluating multiple registrars, Porkbun emerged as the clear winner for homelab domain management:

### Key Advantages

**API Access:**
- Full REST API for programmatic DNS management
- Perfect integration with PowerDNS homelab setup
- No walled garden restrictions (unlike SquareSpace)

**Pricing:**
- Competitive renewal rates
- No hidden fees or upsells
- Transparent pricing structure

**Developer-Friendly:**
- Clean, modern interface
- Excellent documentation
- No vendor lock-in for transfers

**Homelab Integration:**
- API-driven DNS updates
- Automation-friendly
- Works seamlessly with infrastructure-as-code

## Hard Pass Registrars

### GoDaddy - Never Again

Multiple negative experiences, both personal and professional:

- **DNS Migration Disaster:** During a professional engagement, GoDaddy left the business without DNS services for several days during what should have been a routine migration. Email, website, and all online services were down. The support response was inadequate and slow.
- **Constant Price Increases:** Renewal prices creep up every year
- **Aggressive Upselling:** Every interaction tries to sell additional services
- **Buggy Interface:** Frequent UI issues and confusing workflows

After the multi-day outage incident, I moved all personal domains away and have recommended against GoDaddy professionally ever since.

### Register.com / Network Solutions

Poor customer service, outdated systems, and overpriced renewals. Multiple frustrating support interactions over the years made these registrars non-starters.

### SquareSpace

Expensive, limited API access, not developer-friendly. The forced migration from Google Domains revealed how restrictive their platform is compared to alternatives. No DNS export functionality is particularly frustrating.

## Alternative Registrars Considered

### NameCheap

World's second-largest registrar with competitive pricing and good support. Offers affordable SSL certificates and premium DNS with DDoS protection. Solid choice but lacks the API flexibility needed for homelab automation.

### Dynadot

Favored by domainers and developers on Reddit. Low renewal prices and simple platform. Good option but Porkbun's API capabilities were more compelling for homelab use.

### Cloudflare

Sells domains at cost - lowest prices available. However, requires using Cloudflare DNS exclusively with no option to change nameservers. This restriction conflicts with homelab PowerDNS setup.

## Migration Timeline

**Week 1-2:** Request transfer codes for Batch 1 (5 domains)
**Week 3:** Wait for SquareSpace 5-day hold to expire
**Week 4:** Complete Batch 1 transfers to Porkbun
**Ongoing:** Repeat process for remaining batches

## DNS Records Migration Challenge

### The Problem

SquareSpace doesn't provide an easy export function for DNS records. Before transferring domains, all existing DNS records must be documented and recreated at Porkbun to avoid service disruption.

### Manual Export Method

**For each domain at SquareSpace:**

1. Navigate to Settings → Domains → [domain name] → DNS Settings
2. Screenshot or manually document all records:
   - A records (IPv4 addresses)
   - AAAA records (IPv6 addresses)
   - CNAME records (aliases)
   - MX records (mail servers)
   - TXT records (SPF, DKIM, verification)
   - SRV records (service records)
3. Note TTL values if customized
4. Save to spreadsheet or text file

### Alternative: DNS Query Method

**Use dig or nslookup to query current records:**

```bash
# Query all record types for a domain
dig @8.8.8.8 example.com ANY +noall +answer

# Query specific record types
dig @8.8.8.8 example.com A
dig @8.8.8.8 example.com MX
dig @8.8.8.8 example.com TXT
dig @8.8.8.8 www.example.com CNAME

# Export to file
dig @8.8.8.8 example.com ANY +noall +answer > example.com-dns.txt
```

**Using online DNS lookup tools:**
- [DNSChecker.org](https://dnschecker.org/all-dns-records-of-domain.php)
- [MXToolbox](https://mxtoolbox.com/SuperTool.aspx)
- [WhatsMyDNS.net](https://whatsmydns.net/)

### Import to Porkbun

**Manual method:**
1. Log into Porkbun
2. Navigate to domain → DNS Records
3. Manually recreate each record from documentation
4. Verify all records before changing nameservers

**API method (future automation):**
```bash
# Porkbun API endpoint for DNS records
curl -X POST https://porkbun.com/api/json/v3/dns/create/example.com \
  -H "Content-Type: application/json" \
  -d '{
    "apikey": "YOUR_API_KEY",
    "secretapikey": "YOUR_SECRET_KEY",
    "name": "www",
    "type": "A",
    "content": "192.0.2.1",
    "ttl": "600"
  }'
```

### Migration Checklist

- [ ] Document all DNS records from SquareSpace
- [ ] Create records at Porkbun (don't change nameservers yet)
- [ ] Verify records are correct at Porkbun
- [ ] Lower TTL values 24-48 hours before transfer (if possible)
- [ ] Initiate domain transfer
- [ ] Update nameservers to Porkbun after transfer completes
- [ ] Monitor DNS propagation (24-48 hours)
- [ ] Verify all services working correctly

**Note:** This is the most critical and time-consuming part of the migration. SquareSpace's lack of export functionality makes this unnecessarily manual. Which is also a major factor in why I'm leaving them as well.

## Lessons Learned

**Start Early:** Transfer delays mean starting 2-3 weeks before renewal dates
**Batch Wisely:** Group by renewal date to manage cash flow
**API Matters:** For homelab automation, API access is non-negotiable
**Cost Planning:** Budget for all renewals upfront - transfers aren't free


## Google Domains - Gone But Not Forgotten

Google Domains was highly recommended on Reddit for good reason: transparent pricing, clean interface, and reliable service. Google's decision to shut down and sell to SquareSpace forced this entire migration project. A reminder that even Google services aren't permanent.

---

## References

- [Reddit: Best Cheap Domain Registrar](https://www.reddit.com/r/SiteWays/comments/162841o/the_best_cheap_domain_registrar_according_to/)
- [US News: Cheapest Domain Registrars](https://www.usnews.com/360-reviews/business/domain-registrars/cheapest-domain-registrars)
- [Porkbun API Documentation](https://porkbun.com/api/json/v3/documentation)

*Migration in progress - will update with final results and automation scripts.*
