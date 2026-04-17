---
title: "After Photosynth: Open Source Photogrammetry Alternatives"
layout: post
categories: [technical, computer-vision]
tags: [photosynth, photogrammetry, point-cloud, computer-vision, open-source, python, gatech]
excerpt: "Microsoft Photosynth is gone, but the photogrammetry techniques behind it live on in open-source tools. A look at what replaced it and where my old Georgia Tech project fits in."
---

Microsoft Photosynth was one of those services that felt like the future when it launched — upload a pile of photos and get back a navigable 3D point cloud. I used it extensively during my [Computational Photography](https://www.youtube.com/watch?v=WZPtuNnaqVc&list=PLG_DpV4CFj60wdkJuM2cWBC-uyKEhbYNL) coursework at Georgia Tech, and it became the foundation for my [final project](/photosync-export-visualizer/) — a Python tool that extracted and visualized Photosynth's point cloud data.

Then Microsoft shut it down. The service went offline, the API disappeared, and years of user-created 3D reconstructions vanished. This post covers what happened, what replaced it, and where the technology stands today.

<!-- excerpt-end -->

## My Photosynth Project

During my Masters at Georgia Tech, I built [PyPhotoSynthExport](https://github.com/mcgarrah/PyPhotoSynthExport) — a Python tool that:

1. Downloaded project data from the Photosynth web service via SOAP/JSON APIs
2. Extracted raw binary point cloud data (XYZ coordinates + RGB color)
3. Converted to standard formats (PLY and OBJ)
4. Loaded the data into VTK for interactive 3D visualization

{% include embed.html url="https://www.youtube.com/embed/WZPtuNnaqVc" %}

The project stretched me in several ways — decoding undocumented binary formats, reverse-engineering SOAP interfaces, and learning 3D visualization with VTK. The point clouds were surprisingly detailed for a consumer web service.

[![PhotoSynth Point Cloud](/assets/images/PhotoSynthPointCloud.png){:width="50%" height="50%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/PhotoSynthPointCloud.png){:target="_blank"}

The [project slides](https://github.com/mcgarrah/PyPhotoSynthExport/blob/master/McGarrah_JMichael_Portfolio.pdf) and [source code](https://github.com/mcgarrah/PyPhotoSynthExport) are still available on GitHub, though the Photosynth service they connect to is long gone.

## The Death of Photosynth

Microsoft shut down Photosynth in stages. The original service (based on Noah Snavely's [Bundler](http://www.cs.cornell.edu/~snavely/bundler/) research at Cornell) was retired, and the photosynth.net URLs went dark. User data was lost unless you had exported it beforehand — which is exactly why I built my extraction tool.

One person who saw this coming was the creator behind [DDD Experiments](https://dddexperiments.github.io/), who [preserved Photosynth data](https://medium.com/@dddexperiments/why-i-preserved-photosynth-2f670d5c8dec) before the shutdown. Their [archive](https://dddexperiments.github.io/photosynth/) and the [Photosynth GitHub organization](https://github.com/photosynth) contain some of the remaining documentation of how the service worked.

This is a recurring theme with cloud services — your data lives at the mercy of the provider's business decisions. It's one reason I'm a fan of open-source alternatives that run on your own hardware.

## The Technology: Structure from Motion

What Photosynth did under the hood is called **Structure from Motion (SfM)** — reconstructing 3D geometry from a series of 2D photographs taken from different viewpoints. The pipeline typically involves:

1. **Feature detection** — Finding distinctive points in each image (SIFT, SURF, ORB)
2. **Feature matching** — Identifying the same points across multiple images
3. **Camera pose estimation** — Determining where each photo was taken from
4. **Triangulation** — Computing 3D coordinates from matched 2D points
5. **Bundle adjustment** — Refining all estimates simultaneously to minimize error
6. **Dense reconstruction** (optional) — Filling in the sparse point cloud with dense geometry

This is the same fundamental technology behind autonomous vehicle mapping, drone surveying, archaeological documentation, and augmented reality.

## Open Source Alternatives

The good news: everything Photosynth did is now available in open-source tools, often with better results. Here's what I've been tracking as potential replacements.

### COLMAP

[COLMAP](https://colmap.github.io/) has become the de facto standard for open-source SfM and multi-view stereo. It handles the complete pipeline from feature extraction through dense reconstruction.

- **Strengths:** Complete pipeline, excellent documentation, GPU-accelerated, active development
- **Output:** Sparse and dense point clouds, meshed surfaces
- **Platform:** Linux, macOS, Windows
- **License:** BSD

This is probably where I'd start if rebuilding my Photosynth project today.

### OpenMVG (Open Multiple View Geometry)

[OpenMVG](https://github.com/openMVG/openMVG) is a library focused on the geometric computer vision aspects of SfM. It's more of a building block than a complete application.

- **Strengths:** Modular C++ library, well-tested algorithms, academic rigor
- **Use case:** When you need to integrate SfM into a larger pipeline
- **License:** MPL2

### OpenSfM

[OpenSfM](https://github.com/mapillary/OpenSfM) was developed by Mapillary (now part of Meta) for street-level imagery reconstruction. It's Python-based, which makes it more accessible for experimentation.

- **Strengths:** Python API, designed for street-level imagery, good documentation
- **Use case:** Large-scale outdoor reconstruction, mapping applications
- **License:** BSD

### Meshroom / AliceVision

[Meshroom](https://alicevision.org/#meshroom) provides a node-based GUI for photogrammetry, built on the [AliceVision](https://github.com/alicevision/AliceVision) framework. It's the closest thing to a "consumer-friendly" open-source Photosynth replacement.

- **Strengths:** Visual node editor, complete pipeline with GUI, NVIDIA GPU acceleration
- **Use case:** Artists, hobbyists, and anyone who wants results without writing code
- **License:** MPL2

### Bundler

[Bundler](http://www.cs.cornell.edu/~snavely/bundler/) by Noah Snavely at Cornell is the original academic SfM system that Photosynth was built on. It's historically important but largely superseded by COLMAP and others.

- **Related:** The [BigSfM](https://www.cs.cornell.edu/projects/bigsfm/) project extended this to city-scale reconstruction
- **Status:** Legacy — use COLMAP for new projects

### VisualSFM

[VisualSFM](http://ccwu.me/vsfm/) by Changchang Wu provides a GUI for SfM with GPU-accelerated feature matching. It was popular in the early 2010s but development has slowed.

- **Strengths:** Fast GPU matching, simple GUI
- **Status:** Largely unmaintained — COLMAP is the modern successor

### Hugin

[Hugin](https://hugin.sourceforge.io/) is primarily a panorama stitcher rather than a full SfM tool, but it shares some of the same feature matching and image alignment foundations.

- **Use case:** Panoramic image stitching, not 3D reconstruction
- **Strengths:** Mature, well-documented, cross-platform

## Where My Project Fits

My [PyPhotoSynthExport](https://github.com/mcgarrah/PyPhotoSynthExport) tool was specifically about extracting data *from* Photosynth's proprietary format — it didn't do the SfM computation itself. Now that Photosynth is gone, the extraction side is obsolete, but the visualization approach (VTK-based interactive point cloud rendering) is still relevant.

If I were to revisit this project, I'd:

1. **Use COLMAP** for the SfM pipeline instead of relying on a cloud service
2. **Keep the VTK visualization** or upgrade to [Open3D](http://www.open3d.org/) for modern point cloud rendering
3. **Run everything locally** — no dependency on services that can disappear
4. **Export to standard formats** (PLY, OBJ, glTF) for use in Blender, MeshLab, or web viewers

The lesson from Photosynth's shutdown is clear: if your workflow depends on a cloud service, have an export strategy. Or better yet, use open-source tools that run on your own hardware from the start.

## Practical Applications

Photogrammetry has moved well beyond academic curiosity:

- **Homelab documentation** — 3D scans of server racks and cable runs
- **Real estate** — Virtual property tours from phone photos
- **Cultural preservation** — Digitizing historical sites and artifacts
- **Drone surveying** — Terrain mapping and volumetric analysis
- **Game development** — Creating realistic 3D assets from real-world objects
- **Insurance/construction** — Progress documentation and damage assessment

With a decent phone camera and COLMAP or Meshroom, you can produce results today that would have required expensive commercial software a decade ago.

## References

- [PyPhotoSynthExport](https://github.com/mcgarrah/PyPhotoSynthExport) — My original Georgia Tech project
- [PhotoSynth Export and Visualizer](/photosync-export-visualizer/) — Original blog post (2016)
- [Computational Photography playlist](https://www.youtube.com/watch?v=WZPtuNnaqVc&list=PLG_DpV4CFj60wdkJuM2cWBC-uyKEhbYNL) — Georgia Tech coursework videos
- [DDD Experiments Photosynth Archive](https://dddexperiments.github.io/photosynth/) — Preserved Photosynth data
- [Why I Preserved Photosynth](https://medium.com/@dddexperiments/why-i-preserved-photosynth-2f670d5c8dec) — Archive motivation
- [COLMAP](https://colmap.github.io/) — Modern open-source SfM
- [Meshroom / AliceVision](https://alicevision.org/#meshroom) — GUI-based photogrammetry
- [OpenMVG](https://github.com/openMVG/openMVG) — SfM library
- [OpenSfM](https://github.com/mapillary/OpenSfM) — Python SfM by Mapillary
- [Bundler](http://www.cs.cornell.edu/~snavely/bundler/) — Original Cornell SfM (Photosynth's foundation)
- [Open3D](http://www.open3d.org/) — Modern point cloud processing library
