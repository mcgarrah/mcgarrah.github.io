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
  date_published: 2025-01-17
  date_modified: 2025-01-17
---

# The GDPR Challenge: When AdSense Review Meets Compliance Reality

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

This is a personal blog that tries to be privacy-friendly. We don't collect 
your personal info directly, but we do use Google Analytics (to see what 
people read) and Google AdSense (to show ads). If you leave comments, those 
go through GitHub and follow their privacy rules.

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
2. **Granular Choices** - Users need meaningful options, not just "accept all"
3. **Easy Withdrawal** - Consent removal must be as easy as consent giving
4. **Transparency** - Clear language about what data is collected and why

### Jekyll-Specific Considerations

1. **Build vs Runtime** - Understand what happens when
2. **Static Site Limitations** - Everything must work client-side
3. **Configuration Management** - Use Jekyll variables for maintainability
4. **Performance Impact** - Conditional loading can improve performance

## The Final Architecture

The completed system provides:

- **Lightweight Implementation** - No external dependencies
- **Proper Consent Management** - Three-level consent with persistence
- **Conditional Script Loading** - Analytics and AdSense load only with consent
- **Mobile Responsive** - Works on all device sizes
- **Maintainable Code** - Uses Jekyll configuration variables
- **Comprehensive Privacy Policy** - GDPR-compliant with user rights

## Results and Impact

### AdSense Review Success

The implementation passed Google's AdSense review on the first submission. Key factors:

- Scripts properly blocked until consent
- Clear privacy policy with GDPR rights
- Functional consent withdrawal mechanism
- Mobile-responsive design

### Performance Benefits

Conditional loading actually improved site performance:

- Faster initial page loads (no tracking scripts)
- Reduced bandwidth for users who decline tracking
- Better Core Web Vitals scores

### User Experience

The consent banner strikes a balance:

- Non-intrusive bottom placement
- Clear language without legal jargon
- Meaningful choices beyond "accept all"
- Easy access to privacy information

## Code Repository

All implementation files are available in the site repository:

- [Cookie Consent Banner](https://github.com/mcgarrah/mcgarrah.github.io/blob/main/_includes/cookie-consent.html)
- [Consent Management Script](https://github.com/mcgarrah/mcgarrah.github.io/blob/main/assets/js/cookie-consent.js)
- [Privacy Policy](https://github.com/mcgarrah/mcgarrah.github.io/blob/main/privacypolicy.md)

## Conclusion

Implementing GDPR compliance on Jekyll sites is more complex than it initially appears, but the systematic approach of passive includes, consent management, and conditional loading creates a robust, maintainable solution.

The key insights:

- **Start with user experience** - Compliance should enhance, not hinder usability
- **Test thoroughly** - Use browser dev tools to verify script loading behavior
- **Document everything** - Complex implementations need clear documentation
- **Plan for maintenance** - Use configuration variables, not hardcoded values

GDPR compliance isn't just about avoiding fines—it's about respecting user privacy while maintaining site functionality. When done right, it can actually improve both user experience and site performance.

The one-day timeline was aggressive, but the systematic approach and thorough testing made it achievable. Most importantly, the implementation is maintainable and reusable for future Jekyll projects.

---

*This implementation was completed in September 2025 for Google AdSense review compliance. The site successfully passed review and maintains full GDPR compliance while providing a smooth user experience.*
