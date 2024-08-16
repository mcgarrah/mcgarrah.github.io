---
title:  "Github Pages Upgrading Jekyll and Workflow"
layout: post
published: false
---

Summary

Jekyll Theme from https://github.com/niklasbuschmann/contrast is really nice as a starting point for Jekyll on Github Pages.
It was last updated on March 13 of 2021.

<!-- excerpt-end -->

I have a `clean` branch that I'm getting down to just the basic changes I want to release back upstream to Niklas and his original template.

I have an upstream branch that I synced with `master` from https://github.com/niklasbuschmann/contrast so I can check the difference between my `main` branch changes as well.

```console
➜  mcgarrah.github.io git:(main) git diff clean upstream
```

This is an interesting problem to solve for me since I have multiple changes at play.

1. Upgrading Jekyll from 4.2.0 to 4.3.3
   a. fix sass duplicate naming of 'index' to 'main'
   b. fix percentage calculation
   c. Gemfile requirement webrick in 4.3.0
   d. Gemfile update version of Jekyll to latest 4.3.3
2. Update Github Pages workflow from older builtin
3. Add conditionally Google Adsense
4. Add conditionally Google Analytics
5. Feature - add image height and width overrides
6. Pagination and Archives view
7. ...
