---
layout: post
title: "Getting Started with Claude Code: A Guide for IDE-First Developers"
categories: [ai, development-tools, automation]
tags: [claude-code, ai-coding-assistant, cli, amazon-q, anthropic, developer-tools]
excerpt: "Setting up Claude Code as a CLI-based AI coding assistant — from the perspective of someone used to IDE-integrated tools like Amazon Q in VS Code."
description: "A practical guide to installing, configuring, and using Claude Code for AI-assisted development, written for developers transitioning from IDE-based assistants like Amazon Q to a terminal-first workflow."
date: 2026-05-01
last_modified_at: 2026-05-01
published: false
seo:
  type: BlogPosting
  date_published: 2026-05-01
  date_modified: 2026-05-01
---

I've been using Amazon Q Developer with the VS Code plugin as my primary AI coding assistant for a while now. With Amazon Q being deprecated in favor of [Amazon Kiro](https://kiro.dev/), I started looking at alternatives. Claude Code from Anthropic caught my attention — but it's a very different experience. There's no IDE plugin. It's a CLI tool. If you're coming from a comfortable VS Code integration, that shift takes some adjustment. As someone who grew up on UNIX terminals, the CLI itself isn't the problem — it's losing the IDE conveniences I've gotten comfortable with.

<!-- excerpt-end -->

This article covers what Claude Code is, how to set it up, and what the day-to-day workflow looks like when your AI assistant lives in the terminal instead of your editor sidebar.

## What Is Claude Code

Claude Code is Anthropic's agentic coding tool built on top of their Claude model family. Unlike Amazon Q (which embeds into VS Code as a chat panel, inline completions, and slash commands), Claude Code runs entirely in your terminal. You launch it in a project directory and interact with it through a conversational CLI.

It can:

- Read and write files in your project
- Execute shell commands
- Search codebases
- Create, modify, and refactor code
- Run tests and debug failures
- Interact with git

The key difference from IDE-based tools: Claude Code operates on your filesystem directly from the terminal. There's no GUI, no sidebar, no inline ghost text. You describe what you want, and it acts.

## Why Consider Claude Code

If you're happy with an IDE-integrated assistant, the CLI approach might seem like a step backward. Here's why it's worth considering:

- **Model quality** — Claude Sonnet and Opus are strong at complex reasoning and large codebase understanding
- **Agentic workflow** — It doesn't just suggest code; it can execute multi-step plans autonomously
- **No IDE lock-in** — Works the same whether you use VS Code, Neovim, Emacs, or just a terminal
- **Project-wide context** — It reads your entire project structure, not just the open file
- **Git-aware** — Understands your repo state and can work with branches and diffs

## Prerequisites

Before installing Claude Code, you'll need:

- **Node.js 18+** — Claude Code is distributed as an npm package
- **An Anthropic API key** or **Anthropic Max subscription** — Claude Code requires authentication
- **A terminal you're comfortable in** — This is where you'll spend your time

## Installation

```bash
# Install globally via npm
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version
```

That's it. There is a [Claude Code extension for VS Code](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code) that embeds the CLI experience into the editor, but the primary interface is the terminal.

## Authentication

Claude Code supports multiple authentication methods:

```bash
# Interactive login (opens browser for Anthropic account)
claude login

# Or set your API key directly
export ANTHROPIC_API_KEY="<your-api-key>"
```

If you have an Anthropic Max subscription, the interactive login is the simplest path. For API key usage, you'll want to add the export to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) so it persists across sessions.

## First Run

Navigate to your project directory and launch Claude Code:

```bash
cd ~/github/your-project
claude
```

You'll get an interactive prompt. From here, you can ask it to do things:

```
> What does this project do? Summarize the structure.

> Find all TODO comments in the codebase.

> Add error handling to the fetch calls in src/api.js

> Run the test suite and fix any failures.
```

Claude Code will read files, propose changes, and ask for confirmation before writing to disk or executing commands. You stay in control.

## The Workflow Shift: IDE vs CLI

This is the part that takes the most adjustment. Here's how common tasks compare:

| Task | Amazon Q (VS Code) | Claude Code (CLI) |
|------|-------------------|-------------------|
| Ask a question about code | Chat panel in sidebar | Type in terminal prompt |
| Get inline suggestions | Ghost text while typing | Describe what you want, it writes the file |
| Review changes | Diff view in editor | Terminal diff output, then review in your editor |
| Run commands | Integrated terminal | Claude runs them directly |
| Context | Open files + @file references | Entire project directory |

The biggest mental shift: **you're not editing code with AI suggestions — you're directing an agent that edits code for you.** You describe the outcome, Claude Code figures out the steps.

### What I Miss from IDE Integration

- **Inline completions** — The ghost text while typing is genuinely useful for boilerplate
- **Visual diffs** — Seeing changes highlighted in the editor is easier than terminal output
- **One-click context** — `@file` references in Amazon Q are convenient
- **Multi-repository workspaces** — Amazon Q and Kiro handle multiple repos in a single workspace context; Claude Code is scoped to one project directory at a time

### What's Better in the CLI

- **Multi-file operations** — Claude Code handles cross-file refactors naturally
- **No context window juggling** — It reads what it needs from the filesystem
- **Scriptable** — You can pipe input and integrate it into shell workflows
- **Headless operation** — Works over SSH, in tmux sessions, on remote servers

## Configuration

Claude Code uses a `CLAUDE.md` file in your project root for persistent instructions — similar to Amazon Q's `.amazonq/rules/` directory. If you're already maintaining rules files for Amazon Q, the concept is familiar.

```markdown
# CLAUDE.md

## Project Context
This is a Jekyll blog hosted on GitHub Pages.

## Conventions
- Use YYYY-MM-DD format for post filenames
- All JavaScript wrapped in IIFEs with strict mode
- Prefer const/let over var
- Include front matter in all content files

## Build Commands
- `bundle exec jekyll serve` for local development
- `bundle exec jekyll build` for production build
```

Claude Code reads this file automatically when you start a session in the project directory.

## Tips for the Transition

1. **Keep your editor open alongside the terminal.** Claude Code writes files; your editor picks up the changes. This gives you the visual diff experience you're used to.

2. **Start with read-only tasks.** Ask Claude Code to explain code, find patterns, or summarize structure before letting it make changes. Build trust in what it understands.

3. **Use git as your safety net.** Commit before asking Claude Code to make changes. If something goes wrong, `git checkout .` gets you back.

4. **Be specific about scope.** Instead of "refactor this project," say "refactor the error handling in src/api.js to use async/await with try-catch blocks."

5. **Review before accepting.** Claude Code asks for confirmation before writing files or running commands. Read what it's proposing.

## Cost Considerations

Claude Code uses the Anthropic API, which means token-based pricing. A heavy coding session can consume significant tokens, especially on large codebases where Claude reads many files for context. Monitor your usage through the [Anthropic Console](https://console.anthropic.com/).

The Anthropic Max subscription provides a fixed monthly cost which may be more predictable if you're using it daily.

## What About Kiro?

Amazon Kiro is the successor to Amazon Q Developer. It's a full IDE (not a plugin) with spec-driven development, automated agents, and steering hooks. It also has access to the latest Claude models, which is a nice perk. It's a different philosophy from both Amazon Q and Claude Code. I may write about Kiro separately once it matures, but for now, Claude Code fills the gap left by Amazon Q's deprecation if you want a capable AI assistant without adopting an entirely new IDE.

## Conclusion

Claude Code is a capable AI coding assistant with a fundamentally different interaction model than what IDE plugin users are accustomed to. The CLI-first approach is jarring at first, but the agentic capabilities — reading your whole project, executing multi-step plans, running commands — make it a powerful tool once you adjust your workflow.

If you're coming from Amazon Q in VS Code, expect a transition period. Keep your editor open, use git liberally, and start with small tasks. The terminal-first approach grows on you faster than you'd expect.

## Related Links

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Anthropic Console](https://console.anthropic.com/)
- [Amazon Kiro](https://kiro.dev/)
