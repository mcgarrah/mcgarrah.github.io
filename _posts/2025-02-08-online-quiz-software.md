---
title:  "Online Quiz Software for Certifications"
layout: post
published: false
date: 2024-12-23
---

I am studying for [several technical certifications](/isc2-cybersecurity-certification/) and I want to study for those using an application that replicates the certification exam process. With that in mind, I started looking around for a simple test or quiz web application that lets me plugin a pile of questions in multiple-choice format with a timer as a baseline.

While, I did find a couple of promising projects, found in the Reference section at the bottom, each had some downside or gaps that would require a good bit of work to make them usable for what I wanted to accomplish. A secondary requirement is to have a somewhat modern web interface and to use a tech stack that I can use to refresh my full-stack programming skills with modern tools.

<!-- excerpt-end -->

Anther goal is to use this as something that is a break from studying. This little project might be the ticket by having a second thing that keeps my brain from imploding. I cannot use my proxmox cluster or ceph or networking as those spiral out of control at every chance. This project has to be something infinitely interruptable.

I want to update by Python webapp skills which leaves me with two major frameworks:

Flask:
  Simplicity, flexibility, small projects, prototyping, learning, APIs, microservices, high performance.

Django:
  Complex projects, rapid development, structure, built-in features, "batteries included" approach.

I know Django and used it for some API and interactive webui work earlier so nothing to gain from using it. That is how Flask was chosen.

My HCI in a webui is not one of my stronger areas but I've been learning a good bit with the Jekyll SCSS pieces for this blog and my resume website.

So for the interactive webui I want something new to me and include some Javascript/Typescript for this. I'm considering Bootstrap initially and may expand out.

I don't want to carry the overhead and complexity of MySQL or PostgreSQL at least initially. But I do want to use them in the future so an ORM that works with Flask is a requirement.

SQLite and JSON are my picks for quick light weight storage for development and stand alone usage.

So here are the distilled quick set of requirements:

1. modern multiple choice ui with CSS and JS
   1. live timer during quiz
   2. onscreen interactive feedback
2. import & export JSON questions
3. use Flask (because I already know Django)
4. use SQLalchemy with SQLite (at least initially)
5. some admin interface

That is all I had mapped out when I started. As I started working, I discovered I had not mapped out the JSON formats for quizes, questions, answers, categories, or other data. You'll see in the code that it was a mistake not to think about those a bit upfront. On the other hand, I also had something up and running in short order as a prototype for testing what worked and didn't work for me. So I had that going for me.

I started writing this webapp back in December 2024 and still have a lot I want to do with it.

[Certification Timed Multiple Choice Quiz WebApp](https://github.com/mcgarrah/legendary_quick_quiz)

I have a README.md with an overview of the project with a high level status.

I have a TODO.md with a list of things I am thinking about doing. This has an item for looking into Github Project to manage the TODO list and requirements along with a roadmap.

FIX BUG templates/footer.html extra QUOTE next to VERSION has extra quote on end of line

``` jinja
Version: <a href="https://github.com/mcgarrah/legendary_quick_quiz/releases/tag/v{{ version }}">v{{ version }}</a>"
```

## Reference

Here is what I found in my research:

- [Web Application for Simulating Certification Exams](https://github.com/mcgarrah/nzarttrainer)

- [Quiz Survey Test - QST](https://sourceforge.net/projects/qstonline/) with a Docker version [Docker QST](https://github.com/elquimista/qst-docker)

- [ClassQuiz is a quiz-application](https://github.com/mawoka-myblock/ClassQuiz) ([fork](https://github.com/mcgarrah/ClassQuiz)) with a [website](https://classquiz.de/). Python code with all the bells and whistles.

- [Reddit: Looking for self-hosted live quiz](https://www.reddit.com/r/selfhosted/comments/fwy250/looking_for_selfhosted_live_quiz/)

This all led to grabbing requirements for each of the project.  Then I found myself finding faults or limitations in each of the applications as they all needed some larger or smaller extensions to do what I needed.
