---
title:  "Introducing oneworldsync: A Python Module for 1WorldSync Content1 API Access"
layout: post
categories: [development, programming]
tags: [python, api, module, development, programming, automation, data-integration]
published: true
---

## Introducing `oneworldsync`

### A Python Module for 1WorldSync Content1 API Access

I'm pleased to introduce a Python module I've developed from scratch called `oneworldsync`. For those who need to programmatically access product content data from the 1WorldSync Content1 API, finding a streamlined solution was challenging to say the least. The only path provided was a very simple Python example, some older PDF documentation and a reference Java SDK. I work primarily in the Machine Learning space so Python first was a priority. Those were my primary motivations behind creating `oneworldsync` as I stumbled towards building a library.

<!-- excerpt-end -->

### What is `oneworldsync`?

At its core, `oneworldsync` is a Python library designed to simplify access to product information from the 1WorldSync Content1 repository. It provides a python library and a command line interface to access the REST API. 1WorldSync is a leading product content provider, and their [Content1](https://1worldsync.com/product-descriptions/content1/) platform is a major source of rich product data. This includes specifications, images, marketing copy, logistical information, and much more. The objective was to provide an intuitive and Pythonic method for developers and data analysts to access this extensive information.

### The Spark and the Build

`oneworldsync` originated from a direct need to work with this type of data. The aim was to develop a tool that would manage the complexities of interacting with the 1WorldSync Content1 API, specifically for accessing the detailed product attributes available through their Content1 offering. This allows users to focus on utilizing the product content rather than wrestling with request formats and authentication. The development process involved understanding the intricacies of the 1WorldSync Content1 API, designing a user-friendly library interface, and, of course, writing and testing the code.

### Why `oneworldsync` May Be Useful

* Simplified Access: It abstracts away the low-level details of API calls to 1WorldSync.
* Rich Data: Retrieve comprehensive product attributes from the Content1 platform.
* Pythonic Interface: Designed for straightforward integration into existing Python workflows.

### Availability: PyPI and ReadTheDocs

Once the core functionality was established, the next step was to make `oneworldsync` accessible to the Python community. This was achieved through two key platforms:

* PyPI (Python Package Index): Publishing `oneworldsync` on PyPI allows installation via a simple `pip install oneworldsync`. This was a relatively straightforward process. The library can be found here: [https://pypi.org/project/oneworldsync/](https://pypi.org/project/oneworldsync/)
* ReadTheDocs: Comprehensive documentation is important for any library. Sphinx was used to generate documentation, which is hosted on ReadTheDocs. This platform integrates well with GitHub, facilitating up-to-date documentation. The documentation is available at: [https://oneworldsync-python.readthedocs.io/](https://oneworldsync-python.readthedocs.io/)

The source code is open and available on GitHub: [https://github.com/mcgarrah/oneworldsync_python](https://github.com/mcgarrah/oneworldsync_python)

### Further Development and Use

`oneworldsync` has reached a stage where I think it can be a useful tool for others. I encourage those interested to explore its capabilities, review the examples in the documentation, and try out the command-line interface features such as `ows login` to verify credentials or `ows count` to quickly get item counts.

The process from identifying a need to publishing a solution has been instructive, offering valuable insights into the Python packaging ecosystem. The tools and packaging were surprisingly easy to use. For those contemplating open-sourcing a project, it can be a worthwhile endeavor.

This is definitely not a finished product but delivers enough value that it felt like it was time to share it. I know I definitely have bugs hiding in the code but not as many as earlier. If you find one, consider contributing to its development on GitHub.
