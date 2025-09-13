---
---
// GDPR Cookie Consent Management
(function() {
    'use strict';
    
    const CONSENT_KEY = 'cookie-consent';
    const CONSENT_EXPIRY = 365; // days
    const GA_ID = '{{ site.google_analytics }}';
    const ADSENSE_ID = '{{ site.google_adsense }}';
    
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
    
    function setCookie(name, value, days) {
        const expires = new Date(Date.now() + days * 864e5).toUTCString();
        document.cookie = `${name}=${value}; expires=${expires}; path=/; SameSite=Lax`;
    }
    
    function getConsent() {
        return localStorage.getItem(CONSENT_KEY);
    }
    
    function setConsent(level) {
        localStorage.setItem(CONSENT_KEY, level);
        setCookie(CONSENT_KEY, level, CONSENT_EXPIRY);
        hideBanner();
        loadConsentBasedScripts(level);
    }
    
    function showBanner() {
        const banner = document.getElementById('cookie-consent-banner');
        if (banner) banner.style.display = 'block';
    }
    
    function hideBanner() {
        const banner = document.getElementById('cookie-consent-banner');
        if (banner) banner.style.display = 'none';
    }
    
    function loadConsentBasedScripts(consentLevel) {
        // Load Google Analytics script and configure
        if (GA_ID && !document.querySelector('script[src*="googletagmanager.com/gtag"]')) {
            const gaScript = document.createElement('script');
            gaScript.async = true;
            gaScript.src = `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`;
            gaScript.onload = function() {
                // Configure analytics after script loads
                gtag('js', new Date());
                gtag('config', GA_ID);
                gtag('consent', 'update', {
                    'analytics_storage': consentLevel === 'all' ? 'granted' : 'denied',
                    'ad_storage': consentLevel === 'all' ? 'granted' : 'denied'
                });
            };
            document.head.appendChild(gaScript);
        }
        
        // Load AdSense if consent given
        if (consentLevel === 'all') {
            loadAdSense();
        }
    }
    
    function loadAdSense() {
        if (ADSENSE_ID && !document.querySelector('script[src*="adsbygoogle"]')) {
            const script = document.createElement('script');
            script.async = true;
            script.src = `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${ADSENSE_ID}`;
            script.crossOrigin = 'anonymous';
            script.onload = function() {
                // Initialize auto ads after script loads
                (adsbygoogle = window.adsbygoogle || []).push({
                    google_ad_client: ADSENSE_ID,
                    enable_page_level_ads: true
                });
            };
            document.head.appendChild(script);
        }
    }
    
    function initConsent() {
        const consent = getConsent();
        
        if (!consent) {
            showBanner();
        } else {
            loadConsentBasedScripts(consent);
        }
        
        // Event listeners
        document.getElementById('cookie-accept')?.addEventListener('click', () => setConsent('all'));
        document.getElementById('cookie-necessary')?.addEventListener('click', () => setConsent('necessary'));
        document.getElementById('cookie-decline')?.addEventListener('click', () => setConsent('declined'));
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initConsent);
    } else {
        initConsent();
    }
})();