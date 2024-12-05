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

AI Agents for some quick coding:

- https://poe.com/
- https://chatgpt.com/
- https://www.perplexity.ai/
- https://gemini.google.com/
- https://copilot.microsoft.com/

Wow has this been an eye opener on AI Agents helping code. I'm a pretty decent Python programmer with a half-ass approach to Javascript for frontends. I'm coding up a fullstack webapp for quizes using CoPilot.

I did have to prompt for a lot things upfront like:

- Use `Flask` and `Flask-Alchemy` to create a quiz application
- Force an upgrade to current versions from older versions
- [My CoPilot chat session](https://copilot.microsoft.com/chats/hVD49LnGBp1iNpjCoorZg) the primary for this exercise
- [My Gemini chat session](https://gemini.google.com/app/8dbc2a42956f6509) as a backup for various things in isolation
- asdf

- "write some python code to generate a quiz online with flask using a json file for questions and answers"
- "Add a webpage for adding or modifying the questions and answers"
- "Add a timer to the quiz"
- "add a sqlite option for adding questions"
- "make the timer value of 5 minutes an option in the database or json file"
- "show the full application"
- "set a configurable number of questions per quiz session in database"
- "make this so you can have more than one type of quiz questions to select as an option in database"
- "make this so you can import the initial questions from a json file"
- "add an answer details memo field to the questions"
- "show the complete application"
  - This is the first of limits for output breaking the path
- "show the complete step 3"
  - workaround for above
- "make a download file of the complete application"
  - no dice on a download file but output the project with it cut off at quiz.html
- "show quiz.html file"
- "show edit.html"
- "show settings.html"
- Now back on track and using this to document the application for README.md file
- "tell me about select_category.html"
- "tell me about the app.py"
- "what are templates files"
- "describe this applications"
- "display the answer_details with the final results"
  - bug introduced showing details on quiz screen
- "how do I run this"
- "how can I run this application in vscode"
- "generate a requirements.txt file for this project"
- "setup vscode to run flask app in venv"
- "how to run flash webapp with vscode in a venv environment"
- "in edit.html I get an error about undefined 'json'"
- "Fix line 96 error with i variable out of range and check only the questions on the quiz page"
- "Error on line 17 quiz.html jinja2.exceptions.TemplateSyntaxError: expected token ',', got 'for'"
- "app.py line 94 convert question_ids to a numeric value"
- 
