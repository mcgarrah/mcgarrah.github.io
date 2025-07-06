---
title: "New Features: Copy Buttons, Comments, Tags, and More!"
layout: post
published: true
categories: 
 - Website 
 - Updates
tags: 
 - feature
 - clipboard
 - gisc
 - tags
 - categories
---

I'm happy to announce a batch of new features that enhance the functionality and user experience of this blog. These improvements make the content more interactive, organized, and user-friendly. Hopefully, you like the changes.

<!-- excerpt-end -->

## Copy to Clipboard for Code Blocks

No more tedious manual selection of code! We've added a convenient "Copy" button to all code blocks throughout the site:

- A clean, minimalist button appears in the top-right corner of each code block
- Powered by clipboard.js for reliable cross-browser compatibility
- Visual feedback confirms when code has been successfully copied
- Button appears on hover, maintaining a clean reading experience

This feature makes it much easier to use code examples from our tutorials and guides in your own projects.

## Giscus Comment System

We've integrated Giscus, a comments system powered by GitHub Discussions, allowing for more meaningful conversations around our content:

- Comment using your GitHub account
- Support for Markdown formatting in comments
- Reactions to show appreciation or agreement
- Threaded replies for organized discussions
- All comments are stored in GitHub Discussions, making them searchable and preservable

The Giscus widget appears at the bottom of each post, creating a space for community interaction and feedback.

## Tags and Categories System

Finding related content is now much easier with our comprehensive tagging system:

- Posts are organized with relevant tags and categories
- Tag and category links on each post lead to listing pages showing all related content
- Dedicated pages at [/tags](/tags) and [/categories](/categories) provide a complete overview
- Visual indicators show the number of posts in each tag or category
- Tags and Categories are being refined on older posts

This system helps you discover content that matches your specific interests and makes navigation more intuitive.

## Reading Time Indicator

Ever wondered how long it will take to read a post? Now you'll know at a glance:

- Each post displays an estimated reading time (e.g., "5 min read")
- Calculation based on average reading speed
- Helps you decide when you have time to read a particular article

## A whole pile of security and modernization fixes

There is just basic maintenance needed with a website core code. Here are some house cleaning pieces that I just caught up on.

- Add the new Github Code Scanning capabilities to the repository to track for security issues in code.
- Adding Dependabot to the workflow to track for outdated libraries and modules.
- Refactoring and future-proofs the theme against Sass 3.0 changes by adopting the module system while maintaining the same visual output
- Replace deprecated SASS global color functions with namespaced versions
- Replace local KaTeX with CDN version to improve security, reduces repository size, and simplifies future maintenance of the math rendering library.

## What's Next?

I'd like to improve your experience. In upcoming releases, I plan to:

- Enhance the mobile responsiveness of the site
- Add dark mode support
- Improve search functionality
- Introduce related posts suggestions

I appreciate your feedback on these new features. If you encounter any issues or have ideas for further improvements, please let me know through our GitHub repository or the comments section below.

Happy coding!
