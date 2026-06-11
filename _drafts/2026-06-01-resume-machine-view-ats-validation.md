---
layout: post
title: "Testing a Machine-Readable Resume Against ATS Systems and AI Agents"
image: /assets/images/og/resume-machine-view-ats-validation.png
categories: [web-development, technical]
tags: [resume, structured-data, json-ld, seo, ats, schema-org, ai]
excerpt: "I built a machine-readable resume view with JSON-LD and semantic HTML. Now I need to verify it actually works — against Google's validators, ATS resume parsers, and AI agents that recruiters are starting to use."
description: "How to validate a machine-readable resume with JSON-LD structured data against Google Rich Results Test, Schema.org validators, ATS resume parsers (Jobscan, Resume Worded), and AI agents. Includes testing methodology and results."
date: 2026-06-01
last_modified_at: 2026-06-01
published: true
seo:
  type: BlogPosting
  date_published: 2026-06-01
  date_modified: 2026-06-01
---

Building a [machine-readable resume view](/resume-site-ground-up-rebuild/) with JSON-LD and semantic HTML is the easy part. Validating that it actually works — that Google indexes the structured data, that ATS systems can parse the PDF exports, and that AI agents extract accurate information from the semantic markup — requires testing against real systems with different parsing pipelines.

This is the validation phase for the `/resume/machine/` view I built during the [resume site rebuild](/resume-site-ground-up-rebuild/). The view embeds Schema.org structured data using both JSON-LD blocks and microdata attributes. But structured data that passes a syntax validator is not the same as structured data that produces results in the real world.

<!-- excerpt-end -->

## The Two Audiences

A critical distinction that took me too long to internalize: **ATS systems and the machine view serve different audiences through different channels.**

| Channel | Consumer | Input Format | What They Parse |
|---------|----------|--------------|-----------------|
| Job application upload | ATS (Greenhouse, Lever, Workday) | PDF or DOCX | Text extraction → NER → structured fields |
| Web URL | Google, AI agents, recruiters | HTML + JSON-LD | Structured data, semantic markup, visible content |

ATS systems never see your website. They parse the PDF or DOCX you upload through their application portal. The machine view at `/resume/machine/` serves a completely different set of consumers: Google's structured data indexer (for rich results), AI recruiting agents that browse URLs, and technical recruiters who view source.

Both need to be tested independently because they have different failure modes.

## Validation Layer 1: Structured Data (Google)

### Google Rich Results Test

The primary validator for JSON-LD structured data intended for Google Search.

- **URL**: [search.google.com/test/rich-results](https://search.google.com/test/rich-results)
- **Input**: `https://mcgarrah.org/resume/machine/`
- **What it validates**: JSON-LD syntax, Schema.org type correctness, required properties for rich result eligibility

![Google Rich Results Test showing structured data validation for the machine-readable resume view](/assets/images/resume-ats-validation-001.png)

My initial submission flagged `ScholarlyArticle` warnings in the publications section — the type requires `headline` and `image` properties that I hadn't included. After adding `<meta itemprop="headline">` and `<meta itemprop="image">` tags, the warnings resolved.

**Key learning**: Google's validator is strict about properties it considers "recommended" for types that are eligible for rich results. Schema.org itself is more permissive — a property can be valid Schema.org but still produce a Google warning if Google has specific expectations for that type.

### Schema Markup Validator

- **URL**: [validator.schema.org](https://validator.schema.org/)
- **Input**: paste URL or raw HTML
- **What it validates**: Schema.org vocabulary correctness, nesting, property value types

![Schema.org Markup Validator results for the machine-readable resume](/assets/images/resume-ats-validation-002.png)

More permissive than Google's tool because it validates against the full Schema.org specification, not just the subset Google supports for rich results. Useful for catching structural errors that Google's tool might not flag.

### Google Search Console

After the page is live and indexed:
- Check **Enhancements** → **Unparsable structured data** for any indexing failures
- Check **Performance** → filter by page to see if rich results are appearing
- Monitor over time — structured data issues can appear days after indexing

![Google Search Console showing structured data indexing status](/assets/images/resume-ats-validation-003.png)

## Validation Layer 2: ATS Resume Parsers

ATS systems parse uploaded documents through a pipeline: text extraction → tokenization → section detection → named entity recognition → structured output. Each major system implements this differently, which means a resume that parses perfectly in Greenhouse might lose data in Workday.

### Testing Tools

| Tool | What It Tests | Approach |
|------|---------------|----------|
| **Jobscan** | Keyword match + parse fidelity against a specific job description | Upload PDF + paste job description, get match score |
| **Resume Worded** | ATS score + section detection + keyword gaps | Upload PDF, get structural analysis |
| **SkillSyncer** | Keyword matching + formatting issues | Upload PDF + job description |
| **Teal** | ATS score + keyword tracking across multiple applications | Upload PDF, track over time |

### Testing Methodology

1. Export the brief PDF (`McGarrah-Resume-brief.pdf`) — this is what I'd actually submit to jobs
2. Select 3–5 real job descriptions at target companies (ideally ones using different ATS platforms)
3. Upload to each checker tool with the job description
4. Record for each:
   - **Parse success**: Did it extract name, contact, all jobs, all dates correctly?
   - **Section detection**: Did it identify Education, Experience, Skills as separate sections?
   - **Keyword match score**: What percentage of job description keywords appear in the resume?
   - **Formatting warnings**: Any structural issues that could cause parse failures?

### Direct ATS Upload Testing

The gold standard is submitting through actual ATS portals and checking the parsed result:

- **Greenhouse**: Look for "Powered by Greenhouse" in job posting footers. After applying, some portals show the parsed profile.
- **Lever**: URLs contain `jobs.lever.co`. Lever shows a parsed preview during application.
- **Workday**: Most Fortune 500 companies. The application flow shows parsed fields you can verify.
- **iCIMS**: Common in healthcare, finance, government sectors.

This is time-consuming but reveals real parsing failures that no simulator can catch. The parsed output shows exactly what the recruiter sees — and where data was lost or misassigned.

### Common ATS Parse Failures

Based on research into how these systems work:

- **Multi-column layouts** break section detection (my resume is single-column — safe)
- **Tables for formatting** confuse text extraction order (not used)
- **Headers/footers with contact info** get missed by some parsers (contact is in the body)
- **Non-standard section headings** prevent section classification (I use standard: "Experience", "Education", "Skills")
- **Dates not adjacent to job titles** cause incorrect date-role associations (mine are in the same `<div>`)
- **PDF generated from complex CSS** can produce garbled text extraction (XeLaTeX produces clean text layers)

## Validation Layer 3: AI Agent Parsing

This is the newest validation layer — and the one the `/resume/machine/` view is specifically designed for.

### Test Protocol

Feed the machine view URL to major AI systems and ask them to extract structured information:

**Prompt**: "Extract all jobs with company names, titles, dates, and key accomplishments from this page: https://mcgarrah.org/resume/machine/"

**Test against**:
- Claude (Anthropic)
- ChatGPT (OpenAI)
- Gemini (Google)

**Evaluate**:
- Completeness: Did it find all 27 experience entries?
- Accuracy: Are dates, titles, and company names correct?
- Association: Are skills correctly linked to the right roles?
- Structured output: Can it produce a clean JSON representation?

### Why This Matters

AI recruiting agents are emerging rapidly. Tools like HireVue, Eightfold, and Beamery use AI to match candidates to roles. LinkedIn's recruiter tools increasingly use AI to surface candidates. Having a machine-readable view that AI systems can parse accurately is not a future concern — it is a current competitive advantage.

The JSON-LD in the machine view serves dual purpose: Google structured data for SEO, and grounding context for AI agents. A recruiter's AI assistant that can accurately extract "5 years of EKS experience across 20+ clusters" from structured data will surface that candidate over one whose resume requires PDF text extraction and NLP inference.

## Results and Next Steps

*[This section will be populated after running the validation tests]*

### Export Inventory

Each export serves a different use case and needs independent validation:

| Export | URL | Use Case | ATS Test? | AI Test? |
|--------|-----|----------|-----------|----------|
| Brief PDF (XeLaTeX, 5 pages) | `/resume/downloads/McGarrah-Resume-brief.pdf` | Standard job applications | ✅ Primary | — |
| Ultra-Brief PDF (XeLaTeX, 2 pages) | `/resume/downloads/McGarrah-Resume-ultra-brief.pdf` | Job boards with length limits | ✅ | — |
| Long PDF (XeLaTeX, 34 pages) | `/resume/downloads/McGarrah-Resume-long.pdf` | Deep-dive readers, reference | Optional | — |
| DOCX (Pandoc) | `/resume/downloads/McGarrah-Resume.docx` | ATS systems that prefer Word | ✅ | — |
| Pandoc PDF | `/resume/downloads/McGarrah-Resume.pdf` | Legacy/fallback | Optional | — |
| Machine View (HTML) | `/resume/machine/` | Google, AI agents, recruiters | — | ✅ Primary |

### Structured Data Validation
- [ ] Google Rich Results Test: `/resume/machine/` — re-validate after 2026-05-09 content update
- [ ] Schema Markup Validator: `/resume/machine/`
- [ ] Google Search Console: verify indexing and rich results appearing

### ATS Parse Testing (PDF/DOCX uploads)
- [ ] Brief PDF → Jobscan (3 target job descriptions)
- [ ] Brief PDF → Resume Worded structural analysis
- [ ] Brief PDF → direct Greenhouse upload: verify parsed fields
- [ ] Brief PDF → direct Workday upload: verify parsed fields
- [ ] Ultra-Brief PDF → Jobscan (same 3 job descriptions — compare scores)
- [ ] DOCX → Jobscan (same 3 job descriptions — compare to PDF scores)
- [ ] DOCX → direct Lever upload: verify parsed fields

### AI Agent Extraction (Machine View)
- [ ] Claude: feed `/resume/machine/` URL, extract all jobs/dates/skills, verify completeness
- [ ] ChatGPT: same extraction test
- [ ] Gemini: same extraction test
- [ ] Compare: which agent extracts the most accurate structured data?

### Cross-Format Consistency
- [ ] Verify all exports contain the same job count, date ranges, and credential list
- [ ] Confirm anchor links in ultra-brief PDF resolve to correct `/resume/print/#anchor` targets
- [ ] Verify DOCX preserves section headings that ATS systems use for classification

## The Broader Point

Most resume advice focuses on keywords and formatting — tactical optimizations for a specific ATS. That matters, but it is solving yesterday's problem. The systems that will matter in 2027 are AI agents that understand semantic structure, not keyword matchers that count string occurrences.

Building a machine-readable view with proper Schema.org markup is an investment in the direction hiring technology is moving. ATS keyword matching is table stakes. Semantic structure that AI agents can reason about is the differentiator.

## Related Posts

- [Rebuilding My Resume Site From the Ground Up](/resume-site-ground-up-rebuild/) — The rebuild that created the machine view
- [Caddy Reverse Proxy for Local Multi-Site Jekyll Development](/caddy-reverse-proxy-local-multi-site-jekyll/) — Local development tooling for the resume site
