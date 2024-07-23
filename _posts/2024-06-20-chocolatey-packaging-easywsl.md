---
title:  "How to package software in Chocolatey"
layout: post
published: false
---

I'm interested in learning a bit more about Chocolatey packaging for Windows environments. I'm using it for my Thinkpad T480 Windows development laptops running WSLv2 and base windows tools. It makes updates a lot easier with a CLI and GUI package manager. I recently encountered a utility that wasn't packaged ([easyWSL](https://github.com/redcode-labs/easyWSL)) that I like using and wanted to figure out how hard it is to package it up and keep it current.

<!-- excerpt-end -->

So first I need to setup an account on [Chocolatey](https://community.chocolatey.org/) so you can upload and manage a package. I did this awhile back but the photo on there is old and I need to update my profile a bit to be current.

Next, I need to start reading the [Quick Start for Package Creation](https://docs.chocolatey.org/en-us/create/create-packages-quick-start/) and get a basic idea of what you need to manage a package. In my case, I already have an existing Github (and Gitlab) accounts and been contributing to other stuff for awhile.

Now, I'm looking for an existing utility that installs off Github releases. I will also need to learn a bit about how to install dependencies since the package I want to setup [easyWSL](https://github.com/redcode-labs/easyWSL) depends on [.NET Desktop Runtime 6.0.3 x64](https://community.chocolatey.org/packages/dotnet-6.0-desktopruntime) which is an already packaged in ```choco```.

The [PowerToys](https://github.com/mkevenaar/chocolatey-packages/tree/master/automatic/powertoys) depends on .Net Desktop Runtime and has the dependencies entries. I also was using the full package name and not the meta-name of [dotnet-desktopruntime](https://community.chocolatey.org/packages/dotnet-desktopruntime) when I was searching for it in other packages. PowerToys also has some nice things to lift like Windows 10 only in the PS1 file ```tools\chocolateyinstall.ps1``` and they have an automated update mechanism setup that I might be able to borrow.

The two files of importance are the NUSPEC file and the PS1 for the installer options. The automatic pieces from [mkevenaar](https://github.com/mkevenaar/chocolatey-packages/tree/master/automatic/) are interesting and worth exploring to make it easier to maintain.

I need to figure out how to do the installation locally on my machine for testing.
