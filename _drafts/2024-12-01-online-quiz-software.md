---
title:  "Online Quiz Software for Certifications"
layout: post
published: false
---

While pushing for several certifications, I found myself needing a way to study in a way that replicates the certification exam process. A quiz or test web application that lets me plugin a pile of questions and multiple-choice answers with a timer was a baseline. Digging around did not find much in a first search.

[Web Application for Simulating Certification Exams](https://github.com/mcgarrah/nzarttrainer)

[Quiz Survey Test - QST](https://sourceforge.net/projects/qstonline/) with a Docker version [Docker QST](https://github.com/elquimista/qst-docker)

[ClassQuiz is a quiz-application](https://github.com/mawoka-myblock/ClassQuiz) ([fork](https://github.com/mcgarrah/ClassQuiz)) with a [website](https://classquiz.de/). Python code with all the bells and whistles.

https://www.reddit.com/r/selfhosted/comments/fwy250/looking_for_selfhosted_live_quiz/

<!-- excerpt-end -->

This all led to grabbing requirements for each of the project.  Then I found myself hating the applications
that all needed small extensions.

Enter ChatGPT and a few other AI agents and my recent work in Flask and Django that needed a refresh.

When building something in Python for a webapp

Flask:
 Simplicity, flexibility, small projects, prototyping, learning, APIs, microservices, high performance.

Django:
 Complex projects, rapid development, structure, built-in features, "batteries included" approach.

No MySQL or PostgreSQL required. Figure out how to use Docker (Rancher) to support the work.
SQLite and JSON are my picks for storage.

I need something that is a break from studying and this little project might be the ticket to having a 
second thing that keeps my brain from imploding. I cannot use my proxmox cluster or ceph or networking
as those spiral out of control at every chance. It has to be something infinitely interruptable.

AI Agents for coding:

- https://poe.com/
- https://chatgpt.com/
- https://www.perplexity.ai/
- https://gemini.google.com/
- https://copilot.microsoft.com/
