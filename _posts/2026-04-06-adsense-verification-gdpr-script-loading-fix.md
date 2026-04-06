---
title: "Fixing AdSense Verification Without Breaking GDPR: The Script Loading Mistake"
layout: post
categories: [web-development, privacy, jekyll]
tags: [gdpr, jekyll, adsense, analytics, privacy, compliance, javascript, seo, debugging]
excerpt: "My GDPR implementation was too aggressive — it hid the AdSense script from Google's verification bot. Here's how I separated verification from ad serving while keeping GDPR compliance intact."
description: "How an overly strict GDPR cookie consent implementation prevented Google AdSense approval by hiding the verification script from crawlers, and the architectural fix that separates script loading from ad activation."
date: 2026-04-06
last_modified_at: 2026-04-06
published: true
seo:
  type: BlogPosting
  date_published: 2026-04-06
  date_modified: 2026-04-06
---

In September 2025, I [implemented GDPR compliance](/implementing-gdpr-compliance-jekyll-adsense/) for this Jekyll site to satisfy Google AdSense requirements. The implementation worked — it passed the initial AdSense review. Then I got rejected anyway, repeatedly, for months. In [March 2026](/adsense-approval-failure-remediation/) I started systematically debugging the rejections, and in [April](/improving-eeat-jekyll-adsense/) I shifted focus to E-E-A-T signals.

But there was a fundamental architectural problem hiding in plain sight the entire time: **my GDPR implementation was so thorough that it hid the AdSense verification script from Google's own crawler.**

<!-- excerpt-end -->

## The Original Architecture

When I built the GDPR consent system in September 2025, I designed it around a principle that seemed obviously correct: *no third-party scripts should load until the user consents*. The implementation had three layers:

1. **Passive includes** in `<head>` — just initialized JavaScript arrays, loaded nothing
2. **Consent manager** — detected user region, showed banner to EU visitors
3. **Dynamic script injection** — only after consent, JavaScript would create `<script>` elements and inject them into the DOM

Here's what `_includes/adsense.html` looked like:

```html
<!-- AdSense - Loaded conditionally based on consent -->
<script>
  window.adsbygoogle = window.adsbygoogle || [];
  // AdSense script will be loaded by consent manager
</script>
```

And in `cookie-consent.js`, the `loadAdSense()` function would dynamically create and inject the script after consent:

```javascript
function loadAdSense() {
    if (ADSENSE_ID && !document.querySelector('script[src*="adsbygoogle"]')) {
        const script = document.createElement('script');
        script.async = true;
        script.src = `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${ADSENSE_ID}`;
        script.crossOrigin = 'anonymous';
        script.onload = function() {
            (adsbygoogle = window.adsbygoogle || []).push({
                google_ad_client: ADSENSE_ID,
                enable_page_level_ads: true
            });
        };
        document.head.appendChild(script);
    }
}
```

This was clean, privacy-respecting, and completely wrong for AdSense approval.

## The Problem: Bots Don't Click "Accept"

Google's AdSense verification bot crawls your site to confirm two things:

1. The `ads.txt` file contains your publisher ID
2. The AdSense script tag with your client ID is present in the page `<head>`

The bot reads raw HTML. It does not execute JavaScript. It does not interact with cookie consent banners. It does not wait for dynamic script injection.

When the bot crawled my site, here's what it saw in the HTML source:

```html
<script>
  window.adsbygoogle = window.adsbygoogle || [];
</script>
```

That's it. An empty array initialization. No reference to `pagead2.googlesyndication.com`. No client ID. From the bot's perspective, AdSense wasn't installed on the site at all.

For non-EU visitors, my consent manager would auto-consent and inject the script immediately — so real users saw ads fine. But the bot? The bot saw nothing.

## The Distinction That Matters

The fix required understanding a distinction I'd missed: **loading a script is not the same as activating it.**

The AdSense JavaScript library (`adsbygoogle.js`) does two separate things:

1. **Loads and registers** — The `<script>` tag downloads the library and makes it available
2. **Activates ads** — Calling `adsbygoogle.push()` with your client config actually triggers ad serving

Step 1 is what Google's bot looks for during verification. Step 2 is what requires user consent under GDPR. These are independent operations, and my original implementation conflated them.

## The Fix

Two files changed. The `_includes/adsense.html` now contains the actual script tag:

```html
<!-- AdSense verification script - always present for bot verification -->
<!-- Ad display is controlled by cookie-consent.js based on user consent -->
<script async
  src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX"
  crossorigin="anonymous"></script>
<script>window.adsbygoogle = window.adsbygoogle || [];</script>
```

And `loadAdSense()` in `cookie-consent.js` was simplified — it no longer injects a script (it's already there), it just activates ads after consent:

```javascript
function loadAdSense() {
    if (window.location.hostname === 'localhost' ||
        window.location.hostname === '127.0.0.1') {
        return;
    }
    // Script is already loaded in <head> via adsense.html.
    // Only activate auto ads here after user consent.
    if (ADSENSE_ID) {
        (adsbygoogle = window.adsbygoogle || []).push({
            google_ad_client: ADSENSE_ID,
            enable_page_level_ads: true
        });
    }
}
```

## Is This Still GDPR Compliant?

Yes. Here's why:

Loading the AdSense library (`adsbygoogle.js`) does not, by itself, set cookies or collect personal data. It makes the ad-serving API available in the browser. Ads are only requested and cookies are only set when you call `adsbygoogle.push()` with the page-level ads configuration — and that still only happens after consent.

The consent flow for each visitor type remains:

**EU visitors:**
1. Page loads → AdSense library loads (no cookies, no tracking)
2. Consent banner appears → user chooses
3. "Accept All" → `adsbygoogle.push()` fires → ads appear
4. "Necessary Only" or "Decline" → `push()` never fires → no ads, no cookies

**US visitors:**
1. Page loads → AdSense library loads
2. Auto-consent → `adsbygoogle.push()` fires immediately → ads appear

The key insight: the GDPR requirement is consent before *processing personal data*, not consent before *loading a JavaScript file*. The script sitting idle in the browser doesn't process anything until you tell it to.

## The Broader HTML Structure Fix

This change was part of a larger cleanup. The default layout (`_layouts/default.html`) also had no `<head>` or `<body>` tags — everything was dumped directly under `<html>`. Even if the AdSense script had been present, it wouldn't have been in a proper `<head>` section for the bot to find.

The full set of structural fixes:

| Issue | Before | After |
|-------|--------|-------|
| `<head>` tag | Missing | Wraps all meta, styles, scripts |
| `<body>` tag | Missing | Wraps all visible content |
| AdSense script | Dynamic JS injection only | Static `<script>` tag in `<head>` |
| Ad activation | Bundled with script loading | Separate consent-gated `push()` call |
| Canonical tags | Duplicated (SEO plugin + manual) | Single tag from SEO plugin |
| Sidebar CSS | `<link>` inside `<aside>` element | `<link>` in `<head>` |

## What I Should Have Known

Looking back at [Google's AdSense setup documentation](https://support.google.com/adsense/answer/9274634), the instructions are explicit: "Copy the code and paste it between the `<head>` and `</head>` tags of your page." Not "dynamically inject it after consent." Not "initialize an empty array." Paste the script tag in the head.

I was so focused on building a privacy-correct consent system that I forgot the most basic requirement: Google needs to see its own script in your HTML to verify you installed it.

## Timeline of the AdSense Journey

For context, here's how this fits into the larger saga:

| Date | Event | Article |
|------|-------|---------|
| Sep 2025 | GDPR consent system built, initial AdSense review passed | [Implementing GDPR Compliance](/implementing-gdpr-compliance-jekyll-adsense/) |
| Late 2025 | Repeated AdSense rejections with vague "site isn't ready" messages | — |
| Mar 2026 | Systematic debugging: sitemap 404s, missing contact page, thin content | [AdSense Approval Failure](/adsense-approval-failure-remediation/) |
| Apr 2026 | E-E-A-T improvements: author bios, structured data, Wikidata, content clusters | [Improving E-E-A-T Signals](/improving-eeat-jekyll-adsense/) |
| Apr 2026 | HTML structure fix and AdSense verification script fix | This article |

Each round of fixes addressed real problems. The sitemap 404s were real. The missing E-E-A-T signals were real. But the verification script issue may have been the original blocker all along — Google couldn't even confirm AdSense was installed.

## Lessons Learned

**Privacy compliance and platform requirements can conflict.** The GDPR-correct approach (load nothing without consent) directly contradicted the AdSense-correct approach (always have the script tag present). The solution was understanding the granularity: load the library always, activate it conditionally.

**Bots see HTML, not JavaScript.** Any verification system that depends on a crawler seeing something on your page needs that something in the raw HTML. Dynamic injection is invisible to most bots.

**Valid HTML structure matters.** Missing `<head>` and `<body>` tags didn't break any browser rendering — browsers are forgiving. But bots that parse HTML structurally (looking for scripts specifically in `<head>`) will miss things that aren't where they expect them.

**Test from the bot's perspective.** `curl -s https://yoursite.com | grep adsbygoogle` would have caught this immediately. I was testing in browsers where the consent manager ran JavaScript and everything looked fine.

## Related Articles

- [Implementing GDPR Compliance for Jekyll Sites](/implementing-gdpr-compliance-jekyll-adsense/) — The original consent system implementation
- [Google AdSense Approval Failure: Debugging the 'Site Isn't Ready' Rejection](/adsense-approval-failure-remediation/) — Sitemap, contact page, and thin content fixes
- [Improving E-E-A-T Signals for Google AdSense Approval on Jekyll](/improving-eeat-jekyll-adsense/) — Author attribution, structured data, and Wikidata
- [Jekyll SEO, Sitemap, and Canonical URL Fixes](/jekyll-seo-sitemap-canonical-url-fixes/) — Earlier SEO work
