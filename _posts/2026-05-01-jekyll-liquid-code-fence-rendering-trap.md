---
title: "Jekyll's Invisible Bug: When Code Fences Don't Protect Your Liquid Examples"
layout: post
categories: [web-development, technical, jekyll]
tags: [jekyll, liquid, markdown, debugging, code-blocks, github-pages, raw-tag]
excerpt: "If you write Jekyll posts about Jekyll, your Liquid code examples will silently vanish — or crash the build. Markdown code fences don't protect Liquid tags from execution. Here's how to find every affected post, why it sneaks up on you, and the fix that actually works."
description: "A deep dive into Jekyll's Liquid rendering behavior inside Markdown code fences. Explains why code blocks don't protect Liquid tags, how to detect unprotected tags across an entire site, the difference between silent failures and build crashes, and the correct use of raw/endraw tags with edge cases for nested examples."
date: 2026-05-01
last_modified_at: 2026-05-01
published: true
seo:
  type: BlogPosting
  date_published: 2026-05-01
  date_modified: 2026-05-01
---

I had a blog post about reading time calculation that crashed my Jekyll build. The error pointed to a draft file, but the code it complained about was inside a Markdown code fence — supposedly safe, display-only text. It wasn't.

{% raw %}Jekyll's Liquid template engine processes **every** `{{ }}` and `{% %}` tag in your Markdown files before the Markdown processor ever sees them.{% endraw %} Code fences, backtick spans, indented code blocks — none of them protect Liquid syntax from execution. If you write posts about Jekyll, Liquid, GitHub Actions, or anything else that uses double-curly-brace syntax, your examples are being silently eaten or actively breaking your build.

<!-- excerpt-end -->

## The Problem

Consider a blog post explaining how Jekyll's reading time calculation works. You'd naturally include the implementation:

{% raw %}````markdown
```liquid
{%- assign words_per_minute = 200 -%}
{%- assign number_of_words = include.post.content | number_of_words -%}
```
````{% endraw %}

This looks safe. It's inside a fenced code block. Every other language treats code fences as literal text.

{% raw %}Jekyll doesn't. The Liquid engine runs first, sees the `{% %}` tags, and tries to execute them.{% endraw %} In this case, `include.post.content` is nil (there's no include context), so `number_of_words` gets nil input and the build crashes:

```
Liquid Exception: undefined method `split' for nil:NilClass
```

## Why It Sneaks Up on You

The insidious part is that most unprotected Liquid doesn't crash — it **silently renders as empty text**. A code example like:

{% raw %}````markdown
```html
<meta property="og:url" content="{{ site.url }}{{ page.url }}">
```
````{% endraw %}

Won't crash because `site.url` and `page.url` are valid variables. Jekyll evaluates them, substitutes the values, and your "code example" now shows your actual URL instead of the template syntax. The Markdown renders, the page looks fine at a glance, and you don't notice that your readers see `https://mcgarrah.org/some-post/` where they should see {% raw %}`{{ site.url }}{{ page.url }}`{% endraw %}.

You only discover the problem when:

1. **A variable is nil** — build crashes with `undefined method` errors
2. **A tag is unbalanced** — `Liquid syntax error: 'if' tag was never closed`
3. **A reader reports** that your code examples are blank or show wrong values
4. **You view source** and notice the Liquid output instead of Liquid syntax

### What Triggers Build Failures vs Silent Corruption

| Pattern | Result |
|---------|--------|
| {% raw %}`{{ site.url }}`{% endraw %} | Silent — renders as your actual URL |
| {% raw %}`{{ page.title }}`{% endraw %} | Silent — renders as the post's title |
| {% raw %}`{{ include.post.content }}`{% endraw %} | **Crash** — nil when not inside an include |
| {% raw %}`{% if paginator.previous_page %}`{% endraw %} with matching {% raw %}`{% endif %}`{% endraw %} | Silent — evaluates the condition, renders nothing |
| {% raw %}`{% if condition %}`{% endraw %} without {% raw %}`{% endif %}`{% endraw %} | **Crash** — unclosed tag error |
| {% raw %}`${{ secrets.GITHUB_TOKEN }}`{% endraw %} | Silent — renders as empty string |
| {% raw %}`{% seo %}`{% endraw %} | **Crash or unexpected output** — executes the SEO plugin |

## The Fix: raw / endraw Tags

The <code>{&#37; raw %}</code> and <code>{&#37; endraw %}</code> tags tell Liquid to pass content through without processing. Wrap your code examples:

{% raw %}````markdown
```liquid
{%- assign words_per_minute = 200 -%}
{%- assign number_of_words = include.post.content | number_of_words -%}
```
````{% endraw %}

Place <code>{&#37; raw %}</code> immediately after the opening code fence and <code>{&#37; endraw %}</code> just before the closing fence.

### Inline Code Too

Backtick inline code is equally unprotected. This in your Markdown:

{% raw %}```markdown
The `{% seo %}` tag generates meta tags.
```{% endraw %}

Needs to become:

```markdown
The {% raw %}`{&#37; seo %}`{% endraw %} tag generates meta tags.
```

### The Nested raw/endraw Problem

You can't show literal <code>{&#37; raw %}</code> or <code>{&#37; endraw %}</code> text inside a <code>{&#37; raw %}</code> block — Liquid sees the inner <code>{&#37; endraw %}</code> and terminates the block early. For posts that need to display the raw/endraw tags themselves (like this one), use HTML character entities:

```
<code>{&#37; raw %}</code> and <code>{&#37; endraw %}</code>
```

The `&#37;` entity renders as `%`, producing <code>{&#37; raw %}</code> visually while avoiding Liquid parsing.

### GitHub Actions Expressions

GitHub Actions uses {% raw %}`${{ }}`{% endraw %} syntax which Liquid also intercepts. Any workflow YAML in a code block needs the same treatment:

````markdown
```yaml
{&#37; raw %}
{% raw %}- name: Build
  run: bundle exec jekyll build --baseurl "${{ steps.pages.outputs.base_path }}"
{% endraw %}{&#37; endraw %}
```
````

## Finding Every Affected File

After discovering this problem in one draft, I found it in a dozen more files. Here's a script that scans your entire site for unprotected Liquid tags outside of `raw` blocks:

{% raw %}```python
#!/usr/bin/env python3
"""Scan Jekyll posts/drafts for unprotected Liquid tags."""
import re, glob

LEGIT_TAGS = [
    '{% highlight', '{% endhighlight',
    '{% include', '{% post_url',
    '{% comment', '{% endcomment',
]

for f in sorted(glob.glob('_posts/*.md') + glob.glob('_drafts/*.md')):
    content = open(f).read()
    # Strip raw blocks
    cleaned = re.sub(
        r'\{%-?\s*raw\s*-?%\}.*?\{%-?\s*endraw\s*-?%\}',
        '', content, flags=re.DOTALL
    )
    # Strip front matter
    cleaned = re.sub(r'^---.*?---', '', cleaned, count=1, flags=re.DOTALL)

    found = []
    for i, line in enumerate(cleaned.split('\n'), 1):
        if '{%' in line or '{{' in line:
            s = line.strip()
            if any(x in s for x in LEGIT_TAGS):
                continue
            found.append(f'  L{i}: {s[:120]}')

    if found:
        print(f'\n=== {f} ===')
        print('\n'.join(found))
```{% endraw %}

Run it from your Jekyll project root:

```bash
python3 find-unprotected-liquid.py
```

The script strips `raw`/`endraw` blocks and front matter first, then reports any remaining Liquid syntax. It skips legitimate Jekyll tags like {% raw %}`{% highlight %}`{% endraw %} and {% raw %}`{% include %}`{% endraw %} that are meant to execute.

## Why This Happens

Jekyll's rendering pipeline processes files in this order:

1. **Liquid template engine** — evaluates all {% raw %}`{{ }}`{% endraw %} and {% raw %}`{% %}`{% endraw %} tags
2. **Markdown processor** (Kramdown) — converts Markdown to HTML
3. **Layout rendering** — wraps content in layout templates

Liquid runs first because Jekyll needs to resolve template variables and includes before Markdown processing. This is the correct design for a template engine — but it means Liquid has no concept of Markdown code fences. By the time Kramdown sees your triple-backtick block, Liquid has already consumed or evaluated everything inside it.

This is documented in [Jekyll's Liquid processing docs](https://jekyllrb.com/docs/liquid/), but it's easy to miss because every other context where you write code (GitHub READMEs, Stack Overflow, documentation sites) treats code fences as sacred.

## Posts That Commonly Need This

If you write about any of these topics, check your code examples:

- **Jekyll configuration** — {% raw %}`{{ site.* }}`{% endraw %}, {% raw %}`{{ page.* }}`{% endraw %} variables
- **Liquid templates** — {% raw %}`{% if %}`, `{% for %}`, `{% assign %}`{% endraw %} tags
- **GitHub Actions workflows** — {% raw %}`${{ secrets.* }}`{% endraw %}, {% raw %}`${{ env.* }}`{% endraw %}, {% raw %}`${{ steps.* }}`{% endraw %}
- **Jinja2 templates** — same {% raw %}`{{ }}`{% endraw %} syntax as Liquid
- **Ansible playbooks** — {% raw %}`{{ variable }}`{% endraw %} syntax
- **Mustache/Handlebars** — {% raw %}`{{ }}`{% endraw %} and {% raw %}`{{{ }}}`{% endraw %} syntax
- **Vue.js templates** — {% raw %}`{{ }}`{% endraw %} interpolation syntax

## Lessons Learned

1. **Code fences are not a security boundary** for Liquid. Never assume content inside backticks is safe from template processing.
2. **Silent failures are worse than crashes.** The posts that render "successfully" with wrong content are harder to catch than the ones that blow up the build.
3. **Scan proactively.** After fixing one post, scan everything. The same pattern tends to appear in clusters — if you wrote one post about Jekyll internals, you probably wrote several.
4. **Keep the detection script.** Run it as part of your pre-commit or CI workflow to catch new instances before they ship.

## Related Posts

- [How the Sausage Is Made: Every Feature Powering This Jekyll Blog](/jekyll-markdown-feature-reference/) — Complete feature reference including Liquid escaping
- [Mermaid Diagram Rendering Challenges](/jekyll-mermaid-diagram-rendering-challenges/) — Another case where Jekyll's rendering pipeline causes surprises

## References

- [Jekyll Liquid Processing](https://jekyllrb.com/docs/liquid/) — Official docs on how Liquid interacts with content
- [Liquid raw Tag](https://shopify.github.io/liquid/tags/template/#raw) — Shopify's Liquid documentation
- [Jekyll Rendering Order](https://jekyllrb.com/docs/plugins/hooks/) — The pipeline that explains why Liquid runs before Markdown
