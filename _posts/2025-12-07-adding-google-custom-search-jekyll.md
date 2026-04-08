---
title: "Adding Google Custom Search to Jekyll Website"
layout: post
categories: [web-development, technical]
tags: [google, search, jekyll, github-pages, feature, web-development]
excerpt: "How to implement Google Custom Search Engine (CSE) on a Jekyll website hosted on GitHub Pages for better content discoverability."
description: "Complete guide to implementing Google Custom Search Engine on Jekyll websites. Includes setup, customization, troubleshooting, and styling for GitHub Pages hosting."
image: /assets/images/google-search-jekyll.png
author: Michael McGarrah
date: 2025-12-07
last_modified_at: 2025-12-07
published: true
seo:
  type: BlogPosting
  date_published: 2025-12-07
  date_modified: 2025-12-07
---

As my Jekyll blog has grown to over 100 posts, finding specific content has become challenging for both me and my readers. While Jekyll has built-in tag and category systems, a proper search function was missing. Here's how I implemented Google Custom Search Engine (CSE) to solve this problem.

<!-- excerpt-end -->

## Why Google Custom Search?

For Jekyll sites hosted on GitHub Pages, search options are limited since we can't run server-side code. Google Custom Search Engine provides:

- **Free tier available** - No cost for basic usage
- **No server required** - Pure client-side implementation
- **Google-powered results** - Leverages Google's indexing of your site
- **Customizable appearance** - Matches your site's design
- **Easy integration** - Minimal code changes required

## Prerequisites

Before implementing, ensure you have:

1. A Jekyll website with content indexed by Google
2. Google account for accessing Google Custom Search
3. Your site verified in Google Search Console (recommended)

## Implementation Steps

### Step 1: Create Google Custom Search Engine

1. Visit [Google Custom Search](https://cse.google.com/cse/)
2. Click "Add" to create a new search engine
3. Enter your site URL: `yourdomain.com` or `username.github.io`
4. Name your search engine (e.g., "My Blog Search")
5. Click "Create" and copy the search engine ID

The search engine ID looks like: `012345678901234567890:abcdefghijk`

### Step 2: Create Search Page

Create `search.html` in your Jekyll root:

```html
{% raw %}---
title: "Search"
layout: default
permalink: /search/
sitemap: false
---

<article>
  <header><h1>Search</h1></header>
  
  <div class="gcse-search"></div>
  
  {% if site.google_cse_id %}
  <script async src="https://cse.google.com/cse.js?cx={{ site.google_cse_id }}"></script>
  {% endif %}
</article>{% endraw %}
```

### Step 3: Add Configuration

Update `_config.yml` to include your search engine ID:

```yaml
# Google Custom Search
google_cse_id: "YOUR_SEARCH_ENGINE_ID"  # Replace with actual ID
```

### Step 4: Add to Navigation

Add search to your navigation menu in `_config.yml`:

```yaml
navigation:
  - {file: "index.html", icon: blog}
  - {file: "archive.html", icon: list}
  - {file: "tags.html", title: Tags, icon: tags}
  - {file: "categories.html", title: Categories, icon: th-list}
  - {file: "search.html", title: Search, icon: search}  # New search page
  - {file: "README.md", icon: user}
```

## Customization Options

### Appearance Customization

In the Google CSE console:

1. Go to "Look and feel" section
2. Choose layout (Overlay, Two page, Results only)
3. Customize colors to match your theme
4. Set font family and sizes

For Jekyll integration, "Results only" layout works best.

### Dark/Light Theme Integration

To make Google Custom Search match your site's automatic dark/light theme, add comprehensive styles to your main SASS file. Google's CSS has high specificity, so we need multiple selectors and `!important` declarations:

```sass
// Add to _sass/main.sass

// Google Custom Search styling with high specificity
.gcse-search,
.gsc-control-cse,
.gsc-control-cse .gsc-control-cse
  background-color: transparent !important
  border: none !important

.gcse-search .gsc-input-box,
.gsc-input-box,
.gsc-input-box-hover,
.gsc-input-box-focus
  background: $light !important
  border: 1px solid reduce(20) !important
  border-radius: 4px !important
  box-shadow: none !important

.gcse-search .gsc-search-button,
.gsc-search-button,
.gsc-search-button-v2
  background: $link-color !important
  border: 1px solid $link-color !important
  border-radius: 4px !important

.gcse-search input.gsc-input,
.gsc-input
  background: transparent !important
  color: $dark !important
  border: none !important

// Dark theme with higher specificity
@media (prefers-color-scheme: dark)
  .gcse-search,
  .gsc-control-cse,
  .gsc-control-cse .gsc-control-cse
    background-color: $dark !important
    
  .gcse-search .gsc-input-box,
  .gsc-input-box,
  .gsc-input-box-hover,
  .gsc-input-box-focus
    background: $dark !important
    border: 1px solid reduce(80) !important
    color: $light !important
  
  .gcse-search input.gsc-input,
  .gsc-input,
  input.gsc-input
    background: transparent !important
    color: $light !important
    border: none !important
  
  .gcse-search .gs-title a,
  .gs-title a,
  .gs-title a:link,
  .gs-title a:visited
    color: $link-color !important
    
  .gcse-search .gs-snippet,
  .gs-snippet
    color: $light !important
```

**Important Notes:**

- Add these styles directly to your existing `_sass/main.sass` file to avoid SASS module circular dependency errors
- The multiple selectors are necessary to override Google's high-specificity CSS
- **Limitation:** Search results may still show some Google default styling that's difficult to override due to how Google loads and applies their CSS dynamically

This approach successfully styles the search input and basic elements to match your site's theme, though some result formatting may remain in Google's default styling.

### Advanced Features

Enable additional features in CSE console:

- **Image search** - Include images in results
- **Autocomplete** - Suggest queries as users type
- **Promotions** - Highlight specific pages
- **Synonyms** - Improve search accuracy

## Testing and Validation

1. Build your site locally:

   ```bash
   bundle exec jekyll serve
   ```

2. Navigate to `/search/` and test various queries

3. Verify search results include your recent posts

4. Check mobile responsiveness

## Troubleshooting Custom Domains

If you're using a custom domain (like `yourdomain.com` instead of `username.github.io`), you need to ensure Google Custom Search is configured for the correct domain.

### Common Issue: Domain Mismatch

Your Jekyll site might be served from a custom domain, but Google CSE is configured for the GitHub domain. This results in no search results.

**Example scenario:**

- Site URL: `www.mcgarrah.org` (custom domain)
- CSE configured for: `mcgarrah.github.io` (GitHub domain)
- Result: No search results found

### Fix Custom Domain Configuration

1. **Check your CNAME file** in your repository root:

   ```text
   www.yourdomain.com
   ```

2. **Update Google Custom Search Engine**:

   - Go to [Google CSE Console](https://cse.google.com/cse/)
   - Select your search engine
   - Click "Setup" → "Sites to search"
   - Remove: `username.github.io`
   - Add: `www.yourdomain.com` (matching your CNAME)
   - Or use: `*.yourdomain.com` for subdomain support

3. **Verify Google indexing** of your custom domain:

   ```text
   site:www.yourdomain.com
   site:yourdomain.com
   ```

4. **Add fallback search** for immediate testing:

   ```html
   <form action="https://www.google.com/search" method="get" target="_blank">
     <input type="hidden" name="sitesearch" value="yourdomain.com">
     <input type="text" name="q" placeholder="Search this site...">
     <input type="submit" value="Search">
   </form>
   ```

### Google Search Console Setup

Ensure both domain variants are added to Google Search Console:

- `https://www.yourdomain.com`
- `https://yourdomain.com`

This helps Google properly index and understand your site's canonical domain.

### Wait Time

After updating CSE configuration for a custom domain, allow 24-48 hours for Google to recognize the change and start returning results from the correct domain.

## Performance Considerations

- Google CSE loads asynchronously, minimizing impact on page load
- Results are cached by Google for faster subsequent searches
- No database or server resources required on your end

## Limitations

- **Indexing delay** - New content may take days to appear in search
- **Google dependency** - Relies on Google's indexing of your site
- **Limited customization** - Appearance options are constrained
- **Ads in free tier** - Google may show ads in search results
- **Domain configuration** - Must match your actual serving domain exactly
- **Initial setup delay** - New CSE configurations may take 24-48 hours to work
- **Styling limitations** - Google's dynamic CSS loading makes complete theme matching difficult; some search result elements may retain Google's default styling despite custom CSS

## Alternative Solutions

For comparison, other Jekyll search options include:

- **[Algolia](https://www.algolia.com/doc/framework-integration/jekyll/)** - More powerful search with instant results, faceted search, and analytics. Requires API key setup, has usage limits on free tier, and needs build-time indexing. Not pursued due to complexity and potential costs for larger sites.

- **[Lunr.js](https://lunrjs.com/)** - Client-side JavaScript search that builds an index from your content. Provides fast, offline-capable search without external dependencies. Not chosen because it requires a JavaScript build process, increases page load time with large content indexes, and lacks the comprehensive indexing that Google provides.

- **[Simple Jekyll Search](https://github.com/christian-fei/Simple-Jekyll-Search)** - Lightweight JavaScript solution that searches through a JSON file of your posts. Easy to implement and fully self-contained. Rejected because it only searches post metadata (titles, tags, categories) rather than full content, and doesn't scale well with large amounts of content.

## Results

After implementation, the search functionality provides:

- Instant access to all indexed content
- Better user experience for content discovery
- Reduced bounce rate from users unable to find content
- Analytics on what users are searching for

## Next Steps

Future enhancements could include:

- Adding search box to header/sidebar
- Implementing search result analytics
- Creating search-driven content recommendations
- Adding site-specific search filters

## Conclusion

Google Custom Search Engine provides an effective, zero-maintenance search solution for Jekyll websites. While it has limitations compared to dedicated search services, it's perfect for personal blogs and small sites that need basic search functionality without server-side complexity.

The implementation took less than 30 minutes and immediately improved the site's usability. For Jekyll sites hosted on GitHub Pages, it's an excellent balance of functionality and simplicity.

---

*This feature has been added to my website as part of ongoing improvements. You can see the search functionality in action at the [Search](/search/) page.*
