---
title:  "Claude on ChromeOS"
layout: post
categories: [technical]
tags: [chromeos, claude, ai]
---

I have an idea of using my Lenovo ChromeOS as a quick spot for doing development.

<!-- excerpt-end -->

I already have the VS Code, Github and Crostini/Linux setup on that system.


You can run Claude Code and the Claude Chrome extension on ChromeOS via the Linux development environment (Crostini). This gives you a native, terminal-based AI coding assistant that seamlessly connects with your browser for testing and debugging. [1, 2]  

1. Set Up Your Linux Environment 

• Open Settings &gt; Advanced &gt; Developers on your Chromebook. 
• Turn on the Linux development environment and follow the on-screen prompts. 
• Update your packages and install  and : [2, 3, 4, 5]  

2. Install Claude Code 

• Open your Linux terminal. 
• Run the official zero-dependency installation script: 
• Once installed, run  to sign in with your paid Claude account (Pro, Team, or Enterprise). [6]  

3. Install the Claude Chrome Extension 

• Open your regular Chrome browser (not the Linux app). 
• Download the Claude Chrome Extension from the Chrome Web Store. 
• Sign in and pin the extension to your toolbar. [7, 8, 9]  

4. Connect Claude Code to Chrome 

• In your Linux terminal, start Claude Code with the Chrome integration flag: 
• Once inside the CLI, type  to verify the connection. [10]  

Now you can write and modify code in your terminal, then ask Claude to open your local web app, read console logs, and click through your UI. Review the Claude Chrome Documentation for full examples of build-test-verify workflows. [1]  

AI responses may include mistakes.

[1] https://code.claude.com/docs/en/chrome
[2] https://www.linkedin.com/posts/jonathan-lees-548a32115_i-finally-got-claude-cowork-on-my-chromebook-activity-7447639060178866176-tL3_
[3] https://medium.com/google-cloud/who-said-you-cant-code-on-a-chromebook-local-development-with-cloud-functions-4e68dca1240b
[4] https://www.youtube.com/shorts/f-mrDx3yTgY
[5] https://www.quantvps.com/blog/how-to-install-claude-code-on-vps
[6] https://www.nxcode.io/resources/news/install-claude-code-setup-guide-2026
[7] https://support.claude.com/en/articles/12012173-get-started-with-claude-in-chrome
[8] https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn
[9] https://www.youtube.com/watch?v=niRLNJz-tCI
[10] https://www.reddit.com/r/ClaudeAI/comments/1pthd5z/spent_this_weekend_with_claude_code_chrome/
