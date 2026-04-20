---
title: "Adding a Dark Mode Toggle to a Jekyll Blog"
layout: post
categories: [web-development, jekyll]
tags: [jekyll, dark-mode, css, javascript, accessibility, user-experience]
date: 2026-07-08
last_modified_at: 2026-07-08
excerpt: "My Jekyll blog already respects prefers-color-scheme for automatic dark mode, but there's no way for readers to override it. Time to add a toggle switch that remembers their preference — without breaking GDPR consent or adding external dependencies."
description: "Implementing a dark mode toggle switch for a Jekyll blog that already has CSS dark mode via prefers-color-scheme. Covers the toggle UI, localStorage persistence, GDPR considerations, and avoiding flash of wrong theme on page load."
seo:
  type: BlogPosting
  date_published: 2026-07-08
  date_modified: 2026-07-08
---

My site already has dark mode. If your OS is set to dark, the blog follows automatically via `prefers-color-scheme: dark` in the CSS. But there's no way to override it — if you want dark mode during the day, or light mode at night, you're stuck changing your entire OS setting.

Time to fix that with a toggle switch.

<!-- excerpt-end -->

## What Already Works

The current implementation uses CSS media queries in the SASS files:

```sass
@media (prefers-color-scheme: dark)
  body
    background: $dark
    color: $light
```

This is scattered across `basic.sass`, `index.sass`, `frame.sass`, and `google-search.sass`. It works — but it's purely automatic. The user has no control.

## What I Want

1. A small toggle switch in the navigation bar (sun/moon icon)
2. Clicking it overrides the OS preference
3. The choice persists across page loads (localStorage)
4. First visit respects the OS preference (no flash of wrong theme)
5. No external dependencies — pure CSS + vanilla JS
6. GDPR-friendly — localStorage for theme preference is "strictly necessary" (functional, not tracking)

## The Implementation Plan

### Strategy: CSS Class Override

Instead of relying solely on `@media (prefers-color-scheme: dark)`, add a class-based override:

- `<html data-theme="light">` → force light mode
- `<html data-theme="dark">` → force dark mode
- No `data-theme` attribute → follow OS preference (current behavior)

This means refactoring the existing `@media` queries into a dual system:

```sass
// OS-level preference (default, no override)
@media (prefers-color-scheme: dark)
  body
    background: $dark
    color: $light

// User override via toggle
[data-theme="dark"] body
  background: $dark
  color: $light

[data-theme="light"] body
  background: $light
  color: $dark
```

### The Toggle Component

A button in the nav bar with sun/moon SVG icons from the existing Font Awesome sprite:

```html
<button id="theme-toggle" aria-label="Toggle dark mode" title="Toggle dark mode">
  <svg class="icon icon-sun"><use xlink:href="/assets/fontawesome/icons.svg#sun"></use></svg>
  <svg class="icon icon-moon"><use xlink:href="/assets/fontawesome/icons.svg#moon"></use></svg>
</button>
```

Show the moon when in light mode (click to go dark), show the sun when in dark mode (click to go light).

### Avoiding Flash of Wrong Theme (FOWT)

The critical UX issue: if the theme JS runs after the page renders, users see a flash of the wrong theme. The fix is a tiny inline script in `<head>` that runs before the body renders:

```html
<script>
  (function() {
    var theme = localStorage.getItem('theme');
    if (theme) {
      document.documentElement.setAttribute('data-theme', theme);
    }
  })();
</script>
```

This runs synchronously before any CSS paints, so the correct theme is applied immediately.

### localStorage and GDPR

Theme preference in localStorage is a **functional cookie equivalent** — it's not tracking, not analytics, not advertising. Under GDPR, strictly necessary storage doesn't require consent. The cookie consent banner already distinguishes between necessary and optional storage, so this fits cleanly into the existing framework.

No changes needed to the GDPR consent implementation.

## Tasks

<!-- TODO: These are the implementation steps. Work through them and document what happens. -->

- [ ] Add `sun` and `moon` icons to the Font Awesome sprite (check if already in `_config.yml` icon list)
- [ ] Create the toggle button markup in `_includes/menu.html` or `_layouts/default.html`
- [ ] Add the inline `<head>` script to prevent FOWT
- [ ] Write `assets/js/theme-toggle.js` — toggle logic, localStorage read/write, icon swap
- [ ] Refactor SASS: duplicate `@media (prefers-color-scheme: dark)` rules as `[data-theme="dark"]` selectors
- [ ] Style the toggle button (minimal, fits nav bar aesthetic)
- [ ] Test: OS dark + no override → dark (existing behavior preserved)
- [ ] Test: OS dark + user selects light → light (override works)
- [ ] Test: Refresh page → override persists (localStorage)
- [ ] Test: Clear localStorage → falls back to OS preference
- [ ] Test: Mobile responsive (toggle visible and tappable)
- [ ] Test: Accessibility (keyboard navigable, aria-label, focus visible)

## Considerations

- **Mermaid diagrams** already detect dark mode via `window.matchMedia('(prefers-color-scheme: dark)')` in `default.html`. The toggle needs to update this or Mermaid diagrams will use the wrong theme.
- **Giscus comments** have `theme: preferred_color_scheme` — may need to reload the Giscus iframe when theme changes, or switch to explicit light/dark theme values.
- **Code syntax highlighting** — verify that code blocks look good in both modes. The highlighter CSS may need dark mode variants.
- **Images** — some screenshots may look bad on dark backgrounds. Consider `<picture>` with media queries for critical images, or add subtle borders.

## References

- [web.dev: Building a theme switch](https://web.dev/articles/building/a-theme-switch-component)
- [CSS-Tricks: A Complete Guide to Dark Mode on the Web](https://css-tricks.com/a-complete-guide-to-dark-mode-on-the-web/)
- [MDN: prefers-color-scheme](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme)

## Related Articles

- [Jekyll Small Things: Polish Features](/jekyll-small-things-polish-features/) — Previous UI improvements
- [Implementing GDPR Compliance for Jekyll with AdSense](/implementing-gdpr-compliance-jekyll-adsense/) — Consent framework this integrates with
