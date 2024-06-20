---
title:  "How to package software in Chocolatey"
layout: post
published: false
---

I'm interested in learning a bit more about Chocolatey packaging for Windows environments. I'm using it for my Thinkpad T480 Windows development laptops running WSLv2 and base windows tools. It makes updates a lot easier with a CLI and GUI package manager. I recently encountered a utility that wasn't packaged ([easyWSL](https://github.com/redcode-labs/easyWSL)) that I like using and wanted to figure out how hard it is to package it up and keep it current.



So first I need to setup an account on [Chocolatey](https://community.chocolatey.org/) so you can upload and manage a package. I did this awhile back but the photo on there is old and I need to update my profile a bit to be current.

Next, I need to start reading the [Quick Start for Package Creation](https://docs.chocolatey.org/en-us/create/create-packages-quick-start/) and get a basic idea of what you need to manage a package. In my case, I already have an existing Github (and Gitlab) accounts and been contributing to other stuff for awhile.

Now, I'm looking for an existing utility that installs off Github releases. I will also need to learn a bit about how to install dependencies since the package I want to setup [easyWSL](https://github.com/redcode-labs/easyWSL) depends on [.NET Desktop Runtime 6.0.3 x64](https://community.chocolatey.org/packages/dotnet-6.0-desktopruntime) which is an already packaged in ```choco```.

