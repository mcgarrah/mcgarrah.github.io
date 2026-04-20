---
layout: none
date: 1999-12-31
sitemap: false
---

# Jekyll GDPR Plugin - Project Tracker

Build and publish a reusable Jekyll plugin that implements practical GDPR controls for analytics, ads, and optional third-party scripts.

Last updated: 2026-04-20

---

## Repositories

| Repo | Purpose |
|------|---------|
| [mcgarrah/mcgarrah.github.io](https://github.com/mcgarrah/mcgarrah.github.io) | Real-world implementation and test bed |
| (planned) `mcgarrah/jekyll-gdpr-plugin` | Standalone plugin gem + docs + examples |

## Current State

- GDPR behavior already implemented in-site (custom code and template logic)
- Draft article exists: `_drafts/2026-07-06-jekyll-gdpr-plugin-development.md`
- Related GDPR production posts are published and can be used as source material
- No standalone gem/plugin repository yet

## Related Articles

| Status | Date | File | Notes |
|--------|------|------|-------|
| Published | 2025-09-17 | `_posts/2025-09-17-implementing-gdpr-compliance-jekyll-adsense.md` | Initial GDPR implementation journey |
| Published | 2026-04-06 | `_posts/2026-04-06-adsense-verification-gdpr-script-loading-fix.md` | Script loading and verification fixes |
| Draft | 2026-07-06 | `_drafts/2026-07-06-jekyll-gdpr-plugin-development.md` | Plugin productization article |

## Prior Plugin Infrastructure to Reuse

This GDPR plugin should directly leverage the patterns already proven in the Pandoc/plugin and release-automation article cluster.

| Status | Date | File | Reuse Target |
|--------|------|------|--------------|
| Published | 2026-04-11 | `_posts/2026-04-11-ruby-gem-release-automation.md` | Gem versioning, release flow, RubyGems publish steps |
| Published | 2026-04-12 | `_posts/2026-04-12-jekyll-pandoc-exports-plugin.md` | Plugin packaging structure and implementation workflow |
| Published | 2026-04-13 | `_posts/2026-04-13-jekyll-pandoc-exports-resume-integration.md` | Real-site integration pattern and migration strategy |
| Published | 2026-05-08 | `_posts/2026-05-08-jekyll-github-actions-cicd-pipeline.md` | GitHub Actions test/build/release workflow patterns |
| Published | 2026-05-15 | `_posts/2026-05-15-jekyll-content-distribution-pipeline.md` | Distribution and publication automation checkpoints |

## Leverage Checklist (From Prior Work)

- [ ] Reuse gemspec/versioning/release conventions from the Ruby gem automation work
- [ ] Reuse plugin repo layout and docs pattern from the Pandoc plugin implementation
- [ ] Reuse integration test approach from Pandoc resume integration
- [ ] Reuse GitHub Actions CI/CD structure for build/test/release gates
- [ ] Reuse publication/distribution checklist for release readiness

## Plugin Goals

- [ ] Extract GDPR logic from site-specific templates into reusable plugin components
- [ ] Keep default setup simple for static-site authors (minimal config)
- [ ] Support region-aware behavior with privacy-first defaults
- [ ] Gate analytics/ads/embedded scripts behind explicit consent
- [ ] Provide clean integration with existing Jekyll themes
- [ ] Include migration docs from custom implementations

## Proposed Feature Scope (v0.1)

- [ ] Consent banner include and configurable text/actions
- [ ] Cookie preference persistence (consent state)
- [ ] Script gating tags/helpers for analytics and ad scripts
- [ ] Region mode toggle (`eu`, `global`, `off`) with safe defaults
- [ ] Category-level consent (`necessary`, `analytics`, `advertising`)
- [ ] Optional Google AdSense helper mode (disabled by default)
- [ ] Clear no-JavaScript fallback behavior documentation

## Architecture Plan

- [ ] Ruby gem with Jekyll plugin entrypoint
- [ ] Liquid tags/filters for consent checks and script wrapping
- [ ] Include templates shipped by gem (banner/preferences UI)
- [ ] Config schema under `gdpr_plugin:` in `_config.yml`
- [ ] Build-time generation for required assets/snippets
- [ ] Backward-compatible defaults to avoid breaking existing sites

## Implementation Phases

### Phase 1 - MVP Extraction

- [ ] Isolate current GDPR logic from `mcgarrah.github.io`
- [ ] Build plugin skeleton and local path-based gem loading
- [ ] Implement consent state + conditional script rendering
- [ ] Add minimal banner UI and default copy
- [ ] Validate against current site behavior

### Phase 2 - Hardening and DX

- [ ] Add config validation with useful error messages
- [ ] Add developer-friendly docs and example configurations
- [ ] Add theme integration guide (minimal include changes)
- [ ] Add unit tests for Liquid helpers/filters
- [ ] Add integration test site fixture

### Phase 3 - Packaging and Release

- [ ] Create dedicated GitHub repository
- [ ] Add CI for Ruby/Jekyll matrix testing (reuse prior GitHub Actions patterns)
- [ ] Publish gem to RubyGems
- [ ] Version changelog and release notes
- [ ] Add usage examples and migration cookbook

### Phase 4 - Article and Adoption

- [ ] Finalize `_drafts/2026-07-06-jekyll-gdpr-plugin-development.md`
- [ ] Include before/after integration examples
- [ ] Include legal caveat section (not legal advice)
- [ ] Include operational checklist for compliance reviews
- [ ] Collect feedback issues for v0.2 roadmap

## Configuration Sketch

```yaml
gdpr_plugin:
  enabled: true
  region_mode: eu
  consent_cookie_name: gdpr_consent
  categories:
    analytics: false
    advertising: false
  banner:
    position: bottom
    privacy_policy_url: /privacypolicy/
  integrations:
    adsense:
      enabled: false
    google_analytics:
      enabled: false
```

## Risks and Open Questions

- [ ] How much region detection should happen client-side vs config-only
- [ ] How to keep UI accessible while remaining theme-agnostic
- [ ] Which integrations belong in core vs optional modules
- [ ] How to document compliance boundaries without legal overreach
- [ ] Whether to support consent log export in v1 or defer

## Success Criteria

- [ ] Can be dropped into a clean Jekyll site with <= 15 minutes setup
- [ ] Blocks non-essential scripts before consent in EU mode
- [ ] Works with and without AdSense enabled
- [ ] Has automated tests covering consent gating behavior
- [ ] Documentation is clear enough for non-Ruby-first users

## Notes

- This tracker supports the 2026-07-06 article and should stay aligned with that draft's scope.
- Keep this document as the single source of truth for plugin status and next actions.
