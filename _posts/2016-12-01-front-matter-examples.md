---
layout: post
title: Front Matter Examples
category: examples
mathjax: true
tags: [tag1, tag2]
date: 2016-12-05
published: true
---

Examples and tests for [Front Matter](https://jekyllrb.com/docs/front-matter/)

Examples of [Github Front Matter on Github Pages](https://docs.github.com/en/contributing/writing-for-github-docs/using-yaml-frontmatter). The `redirect_from` and `featuredLinks` appear to be worth trying out. `title`, `shortTitle`, and `intro` all look interesting as well.

Example of [Multiline text in YAML/front matter](https://cloudcannon.com/tutorials/jekyll-tutorial/introduction-to-front-matter-and-yaml/#multiline-text-in-yaml%2Ffront-matter) worth reading quickly.

Metadata that did not work

```yaml
---
author: User1
summary: Summary of post
---
```

Metadata that do seem to work

```yaml
---
layout: post
title: Front Matter Examples
category: examples
mathjax: true
tags: [tag1, tag2]
date: 2016-12-05
published: false
---
```

Minimum required metadata for a post that includes default of published

```yaml
---
title:  "This is another post"
layout: post
published: true
---
```
