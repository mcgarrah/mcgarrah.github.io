---
title:  "Online Quiz Software for Certifications"
layout: post
published: false
---

I have been studying for [several technical certifications](/isc2-cybersecurity-certification/) and recently an online MBA program with Exams that require studying. A goal in the back of my mind was to study for those using an application that replicates the certification and exam process. With that in mind, I started looking around for a simple test or quiz web application that lets me plugin a pile of questions in multiple-choice format with a timer as a baseline.

While, I did find a couple of promising projects, found in the **Research** section below, each had some downside or gaps that would require a good bit of rework to make them usable for what I wanted to accomplish. A secondary requirement is to have a somewhat modern web interface and to use a tech stack that I can use to refresh my full-stack programming skills with modern tools.

Another goal is to use this as something that is a break from studying. This little project might be the ticket by having a second thing that keeps my brain from imploding. I cannot use my proxmox clusters or ceph or even networking as those spiral out of control at every chance. This project has to be something infinitely interruptable.

<!-- excerpt-end -->

## Research

Here is what I found in my exploration of existing open source projects. This is not a comprehensive list as I eliminated some based on personal preferences and likely missed a few just from not digging deeply enough.

* [Web Application for Simulating Certification Exams](https://github.com/mcgarrah/nzarttrainer)
* [Quiz Survey Test - QST](https://sourceforge.net/projects/qstonline/) with a Docker version [Docker QST](https://github.com/elquimista/qst-docker)
* [ClassQuiz is a quiz-application](https://github.com/mawoka-myblock/ClassQuiz) ([fork](https://github.com/mcgarrah/ClassQuiz)) with a [website](https://classquiz.de/). Python code with all the bells and whistles.
* [Reddit: Looking for self-hosted live quiz](https://www.reddit.com/r/selfhosted/comments/fwy250/looking_for_selfhosted_live_quiz/)

What this project research did do is led me to grabbing requirements for each of the project. Then I found myself finding faults or limitations in each of the applications as they all needed some larger or smaller extensions to do what I wanted. The research phase helped me refine the next section of **Requirements**.

## Requirements

Another goal is that I want to update by Python webapp skills which leaves me with two major frameworks:

Flask:
  Simplicity, flexibility, small projects, prototyping, learning, APIs, microservices, high performance.

Django:
  Complex projects, rapid development, structure, built-in features, "batteries included" approach.

I know Django and used it for some API and interactive webui work earlier for a professional work project so nothing to gain from using it. I have also done some very simplistic Flask API work but not at any depth. So that is how Flask was chosen.

* Python Flask framework

My [Human-Computer Interaction (HCI)](https://en.wikipedia.org/wiki/Human%E2%80%93computer_interaction) in a webui is not one of my stronger areas but I've been learning a good bit with the Jekyll SCSS pieces for this blog and my resume website along with [course work](https://omscs.gatech.edu/cs-6750-human-computer-interaction) from a few years back.

So for the interactive webui I want something new to me and include some Javascript/Typescript for this. I'm considering Bootstrap initially and may expand out.

* Bootstrap 3 or latest version
* Javascript/Typescript
* CSS/SCCS

I don't want to carry the overhead and complexity of MySQL or PostgreSQL at least initially. But I do want to use them in the future if this scales up so an ORM that works with Flask is a requirement.

* SQLite and JSON are my picks for quick light weight storage for development and stand alone usage.
* SQLAlchemy with SQLite seems like a good ORM

I hate hacking in SQL to do administrative things for a webapp. So something to do the app administration needs to be built-in.

* Web Admin Interface

So here are the distilled quick set of requirements:

1. modern multiple choice ui with CSS and JS
   1. live timer during quiz
   2. onscreen interactive feedback
2. import & export JSON questions
3. use Flask (because I already know Django)
4. use SQLalchemy with SQLite (at least initially) for persisent storage
5. some form of admin interface (to avoid raw SQL queries on CLI)

## Lessons Learned (or relearned)

That is all I had mapped out when I started. As I started working, I discovered I had not mapped out the JSON formats for quizes, questions, answers, categories, or other data. You'll see in the code that it was a mistake not to think about those a bit upfront. On the other hand, I also had something up and running in short order as a prototype for testing what worked and didn't work for me. So I had that going for me. POC can be either piece-of-crap or proof-of-concept when it comes to refining requirements.

When I started writing this webapp back in December 2024, I didn't have any asperations about what it would end up looking like for a user. I now know I still have a lot I want to do with it and those show up in the [TODO.md](https://github.com/mcgarrah/legendary_quick_quiz/blob/main/TODO.md), [FAQ.md](https://github.com/mcgarrah/legendary_quick_quiz/blob/main/FAQ.md) and [README.md](https://github.com/mcgarrah/legendary_quick_quiz/blob/main/README.md) files. As it stands right now, you can look at the code and see a [demo website](https://plain-gaby-mcgarrah-a35e7264.koyeb.app/) at the Github repository at [Certification Timed Multiple Choice Quiz WebApp](https://github.com/mcgarrah/legendary_quick_quiz).

The [TODO.md](https://github.com/mcgarrah/legendary_quick_quiz/blob/main/TODO.md) file has a list of things I am thinking about doing. One of those items is to look into Github Project to manage the TODO list and requirements along with a roadmap. That would make is easier to find what I want to do next time I get a break and want to write some code. I never thought I'd want Atlassian Jira for personal use until I was playing around.

## Next steps

I'll probably keep having fun with this codebase as I have time to refine it. My eventual goal is to get a fully functional quiz webapp that can replicate all the types of questions for the certification exams. It would also be nice to have an interface for managing different user types. We will see but this is a success in my book as a method to get my full-stack development skills back up to snuff.
