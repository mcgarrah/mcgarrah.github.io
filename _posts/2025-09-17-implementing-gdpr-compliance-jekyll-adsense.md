---
title: "Implementing GDPR Compliance for Jekyll Sites: A Real-World AdSense Integration Story"
layout: post
categories: [web-development, privacy, jekyll]
tags: [gdpr, jekyll, adsense, analytics, privacy, compliance, javascript]
excerpt: "A detailed walkthrough of implementing GDPR cookie consent for Jekyll sites with Google AdSense and Analytics, including debugging challenges and solutions."
description: "Learn how to implement GDPR compliance on Jekyll sites with custom cookie consent, conditional script loading, and proper privacy policies for AdSense approval."
date: 2025-01-17
last_modified_at: 2025-01-17
published: true
seo:
  type: BlogPosting
  date_published: 2025-09-17
  date_modified: 2025-09-17
---

## The GDPR Challenge: When AdSense Review Meets Compliance Reality

When Google AdSense requires GDPR compliance "by tomorrow," you quickly learn that privacy regulations aren't just legal checkboxes—they're complex technical implementations that can make or break your site's functionality.

This is the story of implementing GDPR compliance on a Jekyll static site in one day, complete with the debugging challenges, false starts, and eventual success that led to AdSense approval.

## The Urgent Requirements

The email was clear: Google AdSense review pending, GDPR compliance required immediately. The checklist seemed straightforward:

- ✅ Cookie consent banner for EU visitors
- ✅ Privacy policy updates  
- ✅ User consent management
- ✅ Data processing transparency
- ✅ Right to withdraw consent

But as any developer knows, "straightforward" requirements often hide complex implementation details.

## The Technical Challenge

Jekyll static sites present unique challenges for GDPR compliance:

1. **No server-side processing** - Everything must work client-side
2. **Build-time vs runtime** - Jekyll processes templates at build time, but consent happens at runtime
3. **Third-party scripts** - Google Analytics and AdSense must load conditionally
4. **No external dependencies** - Keep it lightweight and maintainable

## Implementation Architecture

### The Three-Layer Approach

I designed a three-layer system:

1. **Passive Includes** - Jekyll templates that initialize but don't load scripts
2. **Consent Manager** - JavaScript that handles user choices and script loading
3. **Dynamic Loading** - Scripts load only after explicit consent

### File Structure

```text
├── _includes/
│   ├── cookie-consent.html      # Banner component
│   ├── analytics.html           # Passive Analytics setup
│   └── adsense.html             # Passive AdSense setup
├── assets/
│   ├── css/cookie-consent.css   # Banner styling
│   └── js/cookie-consent.js     # Consent logic
├── _layouts/default.html        # Integration point
└── privacypolicy.md             # GDPR-compliant policy
```

## The Implementation Journey

### Step 1: The Cookie Consent Banner

The banner needed to be more than just a notification—it required three distinct consent levels:

```html
<div id="cookie-consent-banner" class="cookie-consent-banner">
  <div class="cookie-consent-content">
    <p>This site uses cookies to improve your experience and for analytics. 
       <a href="/privacy/">Learn more</a></p>
    <div class="cookie-consent-buttons">
      <button id="cookie-accept">Accept All</button>
      <button id="cookie-necessary">Necessary Only</button>
      <button id="cookie-decline">Decline</button>
    </div>
  </div>
</div>
```

**Key Design Decisions:**

- Fixed positioning at bottom (less intrusive than top)
- Mobile-responsive button layout
- Clear privacy policy link
- Three consent levels for granular control

### Step 2: The Consent Management System

The JavaScript needed to handle multiple complex requirements:

```javascript
---
---
// GDPR Cookie Consent Management
(function() {
    'use strict';
    
    const CONSENT_KEY = 'cookie-consent';
    const GA_ID = '{{ site.google_analytics }}';
    const ADSENSE_ID = '{{ site.google_adsense }}';
    
    function loadConsentBasedScripts(consentLevel) {
        // Load Google Analytics conditionally
        if (GA_ID && !document.querySelector('script[src*="googletagmanager.com/gtag"]')) {
            const gaScript = document.createElement('script');
            gaScript.async = true;
            gaScript.src = `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`;
            gaScript.onload = function() {
                gtag('js', new Date());
                gtag('config', GA_ID);
                gtag('consent', 'update', {
                    'analytics_storage': consentLevel === 'all' ? 'granted' : 'denied',
                    'ad_storage': consentLevel === 'all' ? 'granted' : 'denied'
                });
            };
            document.head.appendChild(gaScript);
        }
        
        // Load AdSense if full consent given
        if (consentLevel === 'all') {
            loadAdSense();
        }
    }
})();
```

**Critical Implementation Details:**

- Jekyll front matter (`---`) makes the file processable
- Uses site config variables instead of hardcoded values
- Conditional script loading prevents errors
- Proper consent mode integration with Google services

### Step 3: The Debugging Nightmare

The first implementation seemed to work, but testing revealed multiple issues:

#### Issue 1: Scripts Loading Unconditionally

**Problem:** Google Analytics was loading with HTTP 200 status before consent
**Root Cause:** The analytics include was calling `gtag()` immediately
**Solution:** Made includes truly passive, moved all logic to consent manager

#### Issue 2: AdSense Showing as "BLOCKED"

**Problem:** AdSense appeared blocked in Network tab
**Initial Panic:** Thought the implementation was broken
**Reality Check:** BLOCKED status was actually correct—it meant consent was working!
**Learning:** "BLOCKED" before consent = success, HTTP 200 after consent = success

#### Issue 3: Hardcoded Configuration Values

**Problem:** JavaScript had hardcoded Google Analytics ID
**Impact:** Not maintainable or reusable
**Solution:** Convert JS to Jekyll-processed file with front matter

### Step 4: Privacy Policy Overhaul

The existing privacy policy needed comprehensive GDPR updates:

```markdown
## Quick Summary

This is a personal blog that tries to be privacy-friendly. We don't collect your personal info directly, but we do use Google Analytics (to see what people read) and Google AdSense (to show ads). If you leave comments, those go through GitHub and follow their privacy rules.

## Your Rights (GDPR)

If you are in the EU, you have the right to:
- **Access**: Request information about data we process
- **Rectification**: Correct inaccurate personal data
- **Erasure**: Request deletion of your personal data
- **Portability**: Receive your data in a structured format
- **Object**: Object to processing of your personal data
- **Withdraw Consent**: Withdraw consent for cookie usage at any time
```

**Key Additions:**

- Human-readable summary at the top
- Detailed GDPR rights explanation
- Cookie type classifications
- Third-party service documentation
- Contact information for privacy requests

## Testing and Debugging Process

### The Testing Protocol

Testing GDPR compliance requires systematic verification:

```bash
# 1. Start Jekyll development server
bundle exec jekyll serve --livereload

# 2. Open Chrome incognito window
# Navigate to http://localhost:4000

# 3. Open DevTools (F12) → Network tab
# Reload page (banner should appear)

# 4. Verify BEFORE consent:
# - adsbygoogle.js should be BLOCKED or absent
# - gtag/js should be BLOCKED or absent

# 5. Click "Accept All"

# 6. Verify AFTER consent:
# - Both scripts should load with HTTP 200
# - Banner should disappear
```

### Console Commands for Testing

```javascript
// Check current consent status
localStorage.getItem('cookie-consent')

// Clear consent (banner should reappear)
localStorage.removeItem('cookie-consent')

// Verify script loading
typeof gtag  // 'undefined' before, 'function' after consent
document.querySelector('script[src*="adsbygoogle"]')  // null before, element after
```

### Common Testing Pitfalls

1. **Using regular browser instead of incognito** - Cached consent masks issues
2. **Not clearing localStorage between tests** - Previous consent affects results
3. **Misinterpreting "BLOCKED" status** - It's actually the desired behavior
4. **Testing only happy path** - Need to test consent withdrawal too

## Lessons Learned

### Technical Insights

1. **Jekyll Processing is Powerful** - Front matter in JS files enables dynamic configuration
2. **Passive Includes Work Better** - Let consent manager handle all script loading
3. **Testing is Critical** - GDPR compliance isn't "set and forget"
4. **Documentation Matters** - Complex implementations need thorough documentation

### GDPR Implementation Principles

1. **Consent Before Collection** - No tracking scripts until explicit consent
2. **Granular Choices** - Users need meaningful options beyond "accept all"
3. **Transparency** - Clear explanation of what data is collected and why
4. **Easy Withdrawal** - Users must be able to change their minds

## Why Custom Implementation Over NPM Libraries?

When implementing GDPR compliance, I considered several popular NPM libraries but ultimately chose a custom solution. Here's why:

### Available NPM Options

Several mature libraries exist for cookie consent:

- **cookieconsent** (~50k weekly downloads) - Lightweight but basic styling
- **vanilla-cookieconsent** (~8k downloads) - Modern ES6+, highly customizable
- **klaro** (~3k downloads) - Privacy-focused with granular consent management
- **cookie-consent-js** (~1k downloads) - Simple and framework-agnostic

### Why Custom Was the Right Choice

#### **Jekyll Integration Challenges**

Most libraries expect dynamic backends for configuration. They can't access Jekyll variables like `{{ site.google_analytics }}` directly, requiring additional build steps or manual configuration.

#### **Tailored Logic Requirements**

My implementation needed specific features:

- EU/US region detection with automatic US consent
- Jekyll variable integration
- Conditional loading of exactly two services (GA + AdSense)
- Lightweight footprint for static site performance

#### **Performance Benefits**

```javascript
// Custom solution: ~5KB, no additional HTTP requests
// vs
// Library solutions: 13-50KB + CDN request + configuration overhead
```

#### **Maintenance Advantages**

- **Full Control**: No dependency on external library updates or breaking changes
- **No Bloat**: Only includes features actually needed
- **Direct Integration**: Works seamlessly with Jekyll's build process
- **Custom Logic**: EU/US detection would require custom code anyway

### When Libraries Make Sense

Libraries would be better if you need:

- Extensive multilingual support
- Complex consent categories beyond basic analytics/advertising
- Integration with multiple CMPs (Consent Management Platforms)
- Enterprise-level compliance reporting

### The Verdict

For Jekyll static sites with straightforward GDPR needs, a custom implementation offers:

- Better performance (smaller bundle, fewer requests)
- Tighter integration (Jekyll variables, build process)
- Easier maintenance (no external dependencies)
- Exact feature match (no unused code)

The custom approach was more work upfront but resulted in a more maintainable, performant solution tailored exactly to the use case.

## Results and Validation

After implementing the complete GDPR solution:

### AdSense Approval Success

- ✅ Google AdSense review passed
- ✅ GDPR compliance verified
- ✅ Privacy policy accepted
- ✅ Cookie consent functioning properly

### Performance Impact

- **Before consent**: No tracking scripts loaded (0 requests)
- **After consent**: Scripts load conditionally (2 requests)
- **Bundle size**: 5KB total (JS + CSS)
- **No external dependencies**: All code self-contained

### User Experience

- EU users see consent banner with clear choices
- US users get automatic consent (no banner interruption)
- Privacy policy clearly explains data usage
- Easy consent withdrawal via browser settings

## Conclusion

Implementing GDPR compliance on Jekyll sites requires careful consideration of static site limitations and user experience. While NPM libraries exist, a custom solution often provides better integration, performance, and maintainability for straightforward use cases.

The key is understanding that GDPR compliance isn't just about showing a banner—it's about respecting user privacy through thoughtful technical implementation and transparent communication.

**Final recommendation**: Start with a custom implementation for Jekyll sites unless you have complex enterprise requirements that justify the overhead of external libraries.aningful options, not just "accept all"
3. **Easy Withdrawal** - Consent removal must be as easy as consent giving
4. **Transparency** - Clear language about what data is collected and why

### Jekyll-Specific Considerations

1. **Build vs Runtime** - Understand what happens when
2. **Static Site Limitations** - Everything must work client-side
3. **Configuration Management** - Use Jekyll variables for maintainability
4. **Performance Impact** - Conditional loading can improve performance

## Advanced Enhancement: Region-Based GDPR Detection

After the initial implementation, I realized that showing GDPR banners to all users worldwide wasn't optimal. US users don't need GDPR consent, and the banner creates unnecessary friction.

### The Region Detection Solution

I implemented intelligent region detection that:

- Shows consent banner only to EU visitors
- Auto-consents US users for seamless experience
- Maintains full GDPR compliance where required

```javascript
// EU countries requiring GDPR consent
const EU_COUNTRIES = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'GB', 'IS', 'LI', 'NO'];

async function checkUserRegion() {
    try {
        // Primary: Geolocation API
        const response = await fetch('https://ipapi.co/json/', { timeout: 3000 });
        const data = await response.json();
        return EU_COUNTRIES.includes(data.country_code);
    } catch (error) {
        // Fallback: Timezone detection
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        const euTimezones = ['Europe/', 'Atlantic/Reykjavik', 'Atlantic/Canary'];
        return euTimezones.some(tz => timezone.startsWith(tz));
    }
}

async function initConsent() {
    const consent = getConsent();
    const isEU = await checkUserRegion();
    
    if (!consent) {
        if (isEU) {
            showBanner(); // EU users see consent banner
        } else {
            setConsent('all'); // US users auto-consent
            return;
        }
    } else {
        loadConsentBasedScripts(consent);
    }
}
```

### Detection Strategy

**Primary Method: Geolocation API**

- Uses free `ipapi.co` service for accurate country detection
- 3-second timeout prevents page blocking
- Covers edge cases like VPN usage

**Fallback Method: Timezone Detection**

- Browser timezone as backup when API fails
- Covers most EU timezones including UK, Iceland, Norway
- Lightweight and always available

### User Experience Impact

**EU Visitors (🇪🇺):**

- See targeted banner: "🇪🇺 As an EU visitor, you can control your privacy preferences"
- Must explicitly choose consent level
- Full GDPR compliance maintained

**US Visitors (🇺🇸):**

- No banner interruption
- Analytics and AdSense load immediately
- Optimal performance and user experience

## The Final Architecture

The completed system provides:

- **Lightweight Implementation** - No external dependencies
- **Region-Aware Consent** - EU-only banner with US auto-consent
- **Proper Consent Management** - Three-level consent with persistence
- **Conditional Script Loading** - Analytics and AdSense load only with consent
- **Mobile Responsive** - Works on all device sizes
- **Maintainable Code** - Uses Jekyll configuration variables
- **Comprehensive Privacy Policy** - GDPR-compliant with user rights
- **Performance Optimized** - Faster experience for non-EU users

## Results and Impact

### AdSense Review Success

The implementation passed Google's AdSense review on the first submission. Key factors:

- Scripts properly blocked until consent
- Clear privacy policy with GDPR rights
- Functional consent withdrawal mechanism
- Mobile-responsive design

### Performance Benefits

The region-aware implementation provides multiple performance improvements:

- **EU Users**: Faster initial loads (scripts blocked until consent)
- **US Users**: Immediate script loading (no consent delay)
- **Reduced API Calls**: Geolocation cached per session
- **Better Core Web Vitals**: Optimized loading for each region
- **Reduced Bandwidth**: EU users can decline tracking entirely

### User Experience

The region-aware system optimizes UX for different audiences:

**EU Users:**
- Targeted messaging acknowledging their location
- Non-intrusive bottom placement
- Clear language without legal jargon
- Meaningful choices beyond "accept all"
- Easy access to privacy information

**US Users:**

- No consent interruption
- Immediate site functionality
- Faster page loads
- Seamless browsing experience

## Code Repository

All implementation files are available in the site repository:

- [Cookie Consent Banner](https://github.com/mcgarrah/mcgarrah.github.io/blob/main/_includes/cookie-consent.html)
- [Consent Management Script](https://github.com/mcgarrah/mcgarrah.github.io/blob/main/assets/js/cookie-consent.js)
- [Privacy Policy](https://github.com/mcgarrah/mcgarrah.github.io/blob/main/privacypolicy.md)

## Testing the Region Detection

### Manual Testing Methods

```javascript
// Force EU detection for testing
localStorage.setItem('test-region', 'EU');
location.reload(); // Banner should appear

// Force US detection for testing  
localStorage.setItem('test-region', 'US');
location.reload(); // No banner, auto-consent

// Clear test overrides
localStorage.removeItem('test-region');
```

### VPN Testing

- Connect to EU VPN server → Banner should appear
- Connect to US VPN server → No banner, immediate consent
- Test fallback with API blocked → Timezone detection works

## Conclusion

Implementing region-aware GDPR compliance on Jekyll sites demonstrates that privacy regulations can be both legally compliant and user-friendly. The evolution from universal consent to targeted compliance shows the importance of iterative improvement.

The key insights:

- **Start with user experience** - Compliance should enhance, not hinder usability
- **Consider your audience** - Different regions have different privacy expectations
- **Test thoroughly** - Use browser dev tools and VPN testing for verification
- **Document everything** - Complex implementations need clear documentation
- **Plan for maintenance** - Use configuration variables, not hardcoded values
- **Iterate and improve** - Initial compliance can be enhanced for better UX

GDPR compliance isn't just about avoiding fines—it's about respecting user privacy while maintaining optimal site functionality. The region-aware approach proves that you can have both legal compliance and excellent user experience.

The implementation went from basic compliance to sophisticated region detection, showing how privacy features can evolve to serve users better while maintaining regulatory compliance.

## Implementation Timeline

**Day 1: Basic GDPR Compliance**

- Universal consent banner
- Conditional script loading
- Privacy policy updates
- AdSense review approval ✅

**Day 2: Region-Aware Enhancement**

- Geolocation API integration
- EU-specific targeting
- US user optimization
- Performance improvements

---

*This implementation was completed in September 2025 for Google AdSense review compliance. The site successfully passed review and maintains full GDPR compliance while providing an optimized user experience based on visitor location.*
