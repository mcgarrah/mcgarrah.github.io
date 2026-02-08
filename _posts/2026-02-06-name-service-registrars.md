---
title:  "Migrating 16 Domains from SquareSpace to Porkbun"
layout: post
date: 2026-02-06
excerpt: "Documenting the multi-week process of transferring 16 domains from SquareSpace to Porkbun in batches, managing costs, and dealing with transfer delays. Why Porkbun won for homelab domain management."
published: false
---

"He was in a bind 'cause he was way behind"
-- Charlie Daniels from "The Devil Went Down to Georgia"

## Google Domains - Gone But Not Forgotten

Google Domains was highly recommended for good reason: transparent pricing, clean interface, and reliable service. Google's decision to shut down and sell to SquareSpace forced this entire migration project. A reminder that even Google services aren't permanent. This left me with a technical debt to resolve on something that I had been able to ignore for a long time since the service just worked.

## The Situation

I'm migrating 16 domains from SquareSpace (SS) to Porkbun (PB). These domains originally came from Google Domains before Google sold their registrar business to SquareSpace. The migration is slow and somewhat expensive as I have to do the whole year of registration costs at once, but this is now necessary. I have some other projects involving Technitium and PowerDNS with Split Horizon that require automation which SquareSpace does not have.

### Domain Inventory

All domains currently at SquareSpace, sorted by renewal date:

| Domain | Renewal Date | Batch | Risk Level | Status | Notes |
|--------|--------------|-------|------------|--------|-------|
| mathomancer.com | Mar 31, 2026 | 1 | Low | ✅ Complete | Email forwarding only, minimal traffic |
| mathomancy.com | Mar 31, 2026 | 1 | Low | ✅ Complete | Old site, little to no traffic |
| brainyzone.com | Apr 17, 2026 | 1 | Low | ✅ Complete | Email forwarding, minimal traffic |
| brainyzone.org | Apr 17, 2026 | 1 | Low | ✅ Complete | Email forwarding, minimal traffic |
| cshensley.com | May 8, 2026 | 1 | **Medium** | ✅ Complete | **Active website + email - son's resume site, GitHub Pages reconfigured** |
| brainyz.one | May 17, 2026 | 2 | Low | ✅ Complete | Minimal usage |
| brainyzone.app | May 17, 2026 | 2 | Low | ✅ Complete | Minimal usage |
| brainyzone.net | May 17, 2026 | 2 | Low | ✅ Complete | Minimal usage |
| brainyzone.us | May 17, 2026 | 2 | Low | ✅ Complete | Minimal usage |
| phonemes.org | Jun 16, 2026 | 3 | **Medium** | Pending | **May have AWS demo site + email - needs investigation** |
| darkmagic.org | Aug 16, 2026 | 3 | Medium | Pending | Long-held domain, may have complexity |
| mcgarrah.dev | Mar 3, 2027 | 4 | Medium | Pending | Development projects |
| mcgarrah.us | Sep 22, 2027 | 4 | Medium | Pending | Forwards to blog.mcgarrah.org |
| mcgarrah.app | Mar 3, 2028 | 5 | Medium | Pending | Application projects |
| mcgarware.com | Jun 9, 2026 | 6 | High | Pending | Deferred to later batch |
| mcgarrah.org | Aug 2, 2027 | 6 | **High** | Pending | **Primary domain - highest risk, migrate last** |

**Migration Strategy:**

- **Batch 1 (Low Risk):** ✅ COMPLETE - First 4 domains - email forwarding and old sites with minimal traffic
- **Batch 1 (Medium Risk):** ✅ COMPLETE - cshensley.com - first active site with critical email and resume content
- **Batch 2 (Low Risk):** ✅ COMPLETE - All "brain" domains - minimal usage
- **Batch 3 (Medium Risk):** phonemes.org - potential AWS demo site and email to investigate before migration
- **Batch 3 (Medium Risk):** darkmagic.org - long-held domain, potential complexity
- **Batch 4-5 (Medium Risk):** mcgarrah.dev, mcgarrah.us, mcgarrah.app - active but lower priority
- **Batch 6 (High Risk):** mcgarrah.org + mcgarware.com - primary domains, migrate last after gaining experience
- **Abandoning phonemes.biz** - letting it expire rather than renew/transfer
- Spreads cost over multiple months while building migration confidence

### The Transfer Process Challenges

**Cost Management:**

- Each transfer requires 1-year renewal at Porkbun
- Migrating in batches by renewal date to spread costs over the year is not an option
- Total migration cost: approximately $180-200 for all 16 domains

**Porkbun Annual Renewal Pricing (as of Feb 2026):**

- .com: $11.08/year
- .net: $12.52/year
- .org: $10.74/year
- .app: $14.93/year
- .dev: $12.87/year
- .us: $7.00/year
- .one: $12.40/year

**My Domain Breakdown:**

- 7x .com domains = ~$77.56
- 3x .org domains = ~$32.22
- 2x .net domains = ~$25.04
- 1x .app domain = ~$14.93
- 1x .dev domain = ~$12.87
- 1x .us domain = ~$7.00
- 1x .one domain = ~$12.40
- **Total: ~$182** (plus phonemes.biz being abandoned)

**SquareSpace Delays:**

- 24-48 hours to receive transfer authorization codes via email
- Mandatory 5-day transfer hold (can be expedited - see below)
- Each delay multiplies across multiple domains unless I batch the changes

**Accelerated Transfer Process (IMPORTANT):**

You CAN expedite the 5-day transfer hold:

1. Contact Porkbun support and request accelerated transfer
2. They will send authentication request to domain's registered email
3. Respond from valid domain email address to verify ownership
4. Transfer completes much faster than standard 5-day wait

This significantly reduces migration time per domain batch.

**Note**: While this built-in delay is frustrating, it protects my domains against DNS hijacking and I appreciate they are protecting my domains. But also very glad they will accelerate the process as well. Good on SquareSpace. Would be happy to return if they stop the walled-garden and have competitive pricing.

### Pre-Migration Investigation Needed

**phonemes.org:**

- [ ] Check AWS Console for active resources (EC2, S3, CloudFront, Route53)
- [ ] Search email for AWS account notifications related to phonemes.org
- [ ] Verify if email is configured (check MX records)
- [ ] Document any demo website URLs and functionality
- [ ] Identify AWS services that depend on domain DNS
- [ ] Plan AWS resource updates if DNS changes required

**mcgarrah.org (HIGHEST COMPLEXITY):**

This is the primary domain with the most complex DNS configuration:

- **GitHub Pages hosting** - Main blog site (this site) at mcgarrah.org and www.mcgarrah.org
  - Root domain: 4x A records pointing to GitHub Pages IPs (185.199.108-111.153)
  - www subdomain: CNAME to mcgarrah.github.io
  - GitHub Pages challenge: TXT record _github-pages-challenge-mcgarrah
- **Mailgun email service** - Active email forwarding and sending
  - Root MX records: mxa.mailgun.org and mxb.mailgun.org (priority 10)
  - Root SPF record: "v=spf1 include:mailgun.org ~all"
  - DKIM record: smtp._domainkey with RSA public key
  - nutrition subdomain email: Separate MX, SPF, DKIM, and DMARC records
- **DigitalOcean App Platform** - Multiple hosted applications
  - nutrition.mcgarrah.org → nutrition-app-foi8z.ondigitalocean.app
  - quiz.mcgarrah.org → quiz-app-erfpf.ondigitalocean.app
  - shiny-quiz.mcgarrah.org → shiny-quiz-app-r2gvx.ondigitalocean.app
  - docean.mcgarrah.org → 138.197.58.15 (A record)
- **Legacy/Archive records**
  - old-root.mcgarrah.org → 162.192.161.17 (A record)
- **Google verification**
  - 62sny5ubm7fy.mcgarrah.org → gv-wlttolxmsvc7ve.dv.googlehosted.com
- **SquareSpace Domain Connect**
  - _domainconnect.mcgarrah.org → _domainconnect.domains.squarespace.com

**Complete DNS Record Count: 25+ records across root and subdomains**

**Migration checklist for mcgarrah.org:**
- [ ] Backup all DNS records (completed - see backup output above)
- [ ] Document all GitHub Pages configuration and challenge records
- [ ] Verify Mailgun configuration for both root and nutrition subdomain
- [ ] Test all DigitalOcean app URLs before migration
- [ ] Document DKIM keys and DMARC policies
- [ ] Test email forwarding before and after migration
- [ ] Verify Google domain verification still works
- [ ] Update GitHub repository custom domain settings
- [ ] Plan for DNS propagation delay (24-48 hours)
- [ ] Test each DigitalOcean app after DNS change
- [ ] Have rollback plan ready
- [ ] Migrate LAST after all other domains successful

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

Poor customer service, outdated systems, and overpriced renewals. Multiple frustrating support interactions over the years made these registrars non-starters. However, I have not used them in so long that I'm not sure my assessment reflects the current company and is just spite on my part. :)

### SquareSpace

Expensive, limited API access, not developer-friendly. The forced migration from Google Domains revealed how restrictive their platform is compared to alternatives. No DNS export functionality is particularly frustrating.

## Alternative Registrars Considered

### NameCheap

World's second-largest registrar with competitive pricing and good support. Offers affordable SSL certificates and premium DNS with DDoS protection. Solid choice but lacks the API flexibility needed for homelab automation.

### Dynadot

Favored by domainers and developers on Reddit. Low renewal prices and simple platform. Good option but Porkbun's API capabilities were more compelling for homelab use.

### Cloudflare

Sells domains at cost - lowest prices available. However, requires using Cloudflare DNS exclusively with no option to change nameservers. This restriction conflicts with homelab Technitium and PowerDNS setup I plan on using.

## Migration Timeline

**Week 1-2:** Request transfer codes for Batch 1 (5 domains)
**Week 3:** Wait for SquareSpace 5-day hold to expire
**Week 4:** Complete Batch 1 transfers to Porkbun
**Ongoing:** Repeat process for remaining batches

## DNS Records Migration Challenge

### The Problem

⚠️ **CRITICAL:** SquareSpace doesn't provide an easy export function for DNS records. **Once a domain transfers, SquareSpace removes all DNS records with NO way to retrieve them.** You MUST backup DNS records BEFORE initiating transfer.

**Lesson Learned:** After transferring the first 9 domains, discovered that SquareSpace provides no access to DNS records post-transfer. Fortunately, had backed up records to Google Docs using SquareSpace WebUI copy/paste method. This backup was essential for recreating DNS at Porkbun.

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

### Recommended: DNS Query Method

**BEST PRACTICE:** Use dig or nslookup to create automated backup BEFORE transfer. This provides a reliable, timestamped record independent of registrar UI.

⚠️ **IMPORTANT LIMITATION:** The `dig` command only queries **publicly published DNS records**. It cannot discover:
- Subdomain records unless you query them explicitly by name
- Records configured in registrar but not yet propagated
- Internal registrar configurations

**For complete DNS backup, you MUST:**
1. **Export from SquareSpace WebUI** (copy/paste all records) - This is your authoritative source
2. **Run dig backup script** (below) - Validates what's publicly visible
3. **Compare both sources** - Identifies any unpublished or subdomain records

**Why both methods are needed:**
- **WebUI export** shows ALL configured records (even unpublished subdomains)
- **dig queries** show only what's publicly resolvable (misses subdomains you don't explicitly query)
- **SquareSpace's walled garden** makes automated export impossible, forcing manual copy/paste

For mcgarrah.org with 25+ records across multiple subdomains (nutrition, quiz, shiny-quiz, docean, etc.), the WebUI export was essential - dig alone would have missed most subdomain configurations.

**Automated Backup Script:**

Created a bash script to backup all remaining domains at once:

```bash
#!/bin/bash
# DNS Backup Script for SquareSpace Domain Migration
# Backs up all DNS records before transfer to Porkbun

# Check if dig command is available
if ! command -v dig &> /dev/null; then
    echo "ERROR: 'dig' command not found"
    echo "Install with: apt-get install dnsutils (Debian/Ubuntu) or dnf install bind-utils (RHEL/Fedora)"
    exit 1
fi

DOMAINS=(
    # Already migrated to Porkbun (commented out):
    # "mathomancer.com"
    # "mathomancy.com"
    # "brainyzone.com"
    # "brainyzone.org"
    # "cshensley.com"
    # "brainyz.one"
    # "brainyzone.app"
    # "brainyzone.net"
    # "brainyzone.us"
    
    # Still at SquareSpace (active):
    "mcgarware.com"
    "phonemes.org"
    "darkmagic.org"
    "mcgarrah.dev"
    "mcgarrah.org"
    "mcgarrah.us"
    "mcgarrah.app"
)

RECORD_TYPES=("A" "AAAA" "CNAME" "MX" "TXT" "NS" "SOA" "SRV")
BACKUP_DIR="dns-backups-$(date +%Y%m%d-%H%M%S)"

mkdir -p "$BACKUP_DIR"

echo "DNS Backup started at $(date)"
echo "Backup directory: $BACKUP_DIR"
echo "================================"

for domain in "${DOMAINS[@]}"; do
    echo "Backing up: $domain"
    output_file="$BACKUP_DIR/${domain}.txt"
    
    echo "DNS Records for $domain" > "$output_file"
    echo "Backup Date: $(date)" >> "$output_file"
    echo "========================================" >> "$output_file"
    echo "" >> "$output_file"
    
    for type in "${RECORD_TYPES[@]}"; do
        echo "[$type Records]" >> "$output_file"
        dig @8.8.8.8 "$domain" "$type" +noall +answer >> "$output_file" 2>&1
        echo "" >> "$output_file"
    done
    
    # Also check www subdomain
    echo "[WWW Subdomain]" >> "$output_file"
    dig @8.8.8.8 "www.$domain" A +noall +answer >> "$output_file" 2>&1
    echo "" >> "$output_file"
    
    echo "✓ Saved to $output_file"
done

echo "================================"
echo "Backup complete!"
echo "Files saved in: $BACKUP_DIR"
echo ""
echo "To view a domain's records:"
echo "  cat $BACKUP_DIR/mcgarrah.org.txt"
```

**Download and Usage:**

```bash
# Download script
wget https://mcgarrah.org/assets/binaries/backup-dns-records.sh
chmod +x backup-dns-records.sh

# Run backup
./backup-dns-records.sh

# View results
ls -lh dns-backups-*/
cat dns-backups-*/mcgarrah.org.txt
```

**Manual dig commands for individual domains:**

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

- [x] Document all DNS records from SquareSpace (CRITICAL - do this FIRST)
- [x] Save DNS records using both WebUI copy/paste AND dig/nslookup
- [x] Create records at Porkbun (don't change nameservers yet)
- [x] Verify records are correct at Porkbun
- [ ] Lower TTL values 24-48 hours before transfer (if possible)
- [x] Initiate domain transfer
- [x] Contact Porkbun support for accelerated transfer
- [x] Respond to authentication email from domain's registered email
- [x] Update nameservers to Porkbun after transfer completes
- [x] Monitor DNS propagation (24-48 hours)
- [x] Verify all services working correctly
- [x] For GitHub Pages sites (like cshensley.com), reconfigure custom domain in repository settings

## Migration Progress

**Batch 1 & 2 Complete (9 domains):**

- mathomancer.com ✅
- mathomancy.com ✅
- brainyzone.com ✅
- brainyzone.org ✅
- cshensley.com ✅ (GitHub Pages reconfigured)
- brainyz.one ✅
- brainyzone.app ✅
- brainyzone.net ✅
- brainyzone.us ✅

**Key Lessons:**

1. **DNS Backup is MANDATORY** - SquareSpace deletes records after transfer
2. **WebUI export is essential** - dig cannot discover subdomain records automatically
3. **Use BOTH methods** - WebUI for complete config, dig for public validation
4. **SquareSpace's walled garden** - No API, no export, forces manual copy/paste
5. **Request accelerated transfer** from Porkbun support to save days of waiting
6. **GitHub Pages domains** require reconfiguration in repository settings after DNS changes

**Note:** This is the most critical and time-consuming part of the migration. SquareSpace's lack of export functionality and post-transfer record deletion makes DNS backup absolutely essential. The combination of WebUI copy/paste (for completeness) and CLI tools (for validation) provides the most reliable backup strategy.

## Lessons Learned

**Start Early:** Transfer delays mean starting 2-3 weeks before renewal dates
**Batch Wisely:** Group by renewal date to manage cash flow
**API Matters:** For homelab automation, API access is non-negotiable
**Cost Planning:** Budget for all renewals upfront - transfers aren't free

---

## References

- [Reddit: Best Cheap Domain Registrar](https://www.reddit.com/r/SiteWays/comments/162841o/the_best_cheap_domain_registrar_according_to/)
- [US News: Cheapest Domain Registrars](https://www.usnews.com/360-reviews/business/domain-registrars/cheapest-domain-registrars)
- [Porkbun API Documentation](https://porkbun.com/api/json/v3/documentation)

*Migration in progress - will update with final results and automation scripts.*
