---
layout: post
title: "AI Agent Context Files in Practice: One Repo, Five Agents"
image: /assets/images/og/ai-agent-context-files-in-practice.png
categories: [technical, development]
tags: [ai, claude-code, github-copilot, kiro, gemini, productivity, tooling, plugin-development]
excerpt: "I wrote about managing AI context files across multiple agents in theory. Here's how it actually plays out in a real project — a Jellyfin plugin where Kiro, Claude Code, Copilot, Gemini, and Codex all need to know the same things."
description: "A practical case study of implementing centralized AI agent context management in a real .NET plugin repository. Demonstrates the AGENTS.md pattern with minimal per-tool stubs for Kiro, Claude Code, GitHub Copilot, Gemini CLI, and OpenAI Codex."
date: 2026-08-14
last_modified_at: 2026-08-14
seo:
  type: BlogPosting
  date_published: 2026-08-14
  date_modified: 2026-08-14
---

Two months ago I wrote about [managing context across multiple AI coding assistants](/managing-cross-ai-agent-context/) and documented the [reference guide for every agent's file format](/ai-coding-agent-context-files-reference/). The theory was straightforward: maintain a single source of truth and let each agent's config file be a thin pointer.

This week I put that into practice on [jellyfin-plugin-media-integrity-scanner](https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner) — and discovered what actually matters when you stop thinking about it abstractly and start shipping code with multiple agents hitting the same repo.

<!-- excerpt-end -->

## The Problem That Triggered This

I was implementing the plugin's core components with Kiro (Amazon's new agent-native IDE) and ran into a cascade of build failures. The Jellyfin 10.11 API had removed `IServerEntryPoint`, changed where `MediaType` lives, and renamed the `TaskTriggerInfo` trigger constants. Every time I fixed one issue and pushed, CI failed on the next.

The frustrating part: I'd already figured out these API changes. But without persistent context, each new session started from zero. Worse, when I switched between agents (Kiro for implementation, Claude Code for investigation, Copilot for quick completions), none of them knew what the others had learned.

That's when the articles I'd written stopped being theoretical. I needed exactly the pattern I'd described: one canonical context file that every agent reads.

## The Implementation

Here's what the repository looks like now:

```
jellyfin-plugin-media-integrity-scanner/
├── AGENTS.md                           # Single source of truth
├── CLAUDE.md                           # "Read AGENTS.md"
├── .github/copilot-instructions.md     # "Read AGENTS.md"
├── .gemini/styleguide.md               # "Read AGENTS.md"
├── .kiro/steering/project-context.md   # Pulls in AGENTS.md via inclusion
└── ...
```

Five files. One has content. Four are one-liners.

### Why AGENTS.md

The name matters for exactly one reason: OpenAI Codex auto-discovers `AGENTS.md` by convention, which means one fewer stub file to maintain. Every other agent needs its own config file regardless of what you name the canonical source, so you might as well pick the name that gives you one free discovery.

I considered `CONTEXT.md` (more neutral) and `CONVENTIONS.md` (from my earlier article), but `AGENTS.md` is self-documenting — a human browsing the repo immediately understands what it's for and who it's for.

### The Agents Covered

| Agent | Discovery File | Notes |
|-------|---------------|-------|
| **Kiro** (IDE + CLI) | `.kiro/steering/project-context.md` | File inclusion directive loads full content |
| **Claude Code** | `CLAUDE.md` | Reliably follows file references |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Workspace indexing picks up AGENTS.md |
| **Gemini** (`agy` CLI) | `.gemini/styleguide.md` | Google's Antigravity/Gemini Code Assist |
| **Codex** (OpenAI) | `AGENTS.md` directly | Auto-discovers by convention |

I deliberately dropped Amazon Q Developer support. Amazon shifted their AI developer tooling strategy toward Kiro, and Q Developer's rules system (`.amazonq/rules/`) is headed for deprecation or irrelevance. Maintaining config files for abandoned tooling is exactly the kind of drift I'm trying to avoid.

### The Stub Files

Each agent file is exactly one line:

**CLAUDE.md:**
```
Read AGENTS.md for all project context.
```

**.github/copilot-instructions.md:**
```
Read AGENTS.md at the repository root for all project context and coding guidelines.
```

**.gemini/styleguide.md:**
```
Read AGENTS.md at the repository root for all project context.
```

No duplicated details. Nothing that can go stale. If the agent can follow a file reference (Claude Code can, reliably), it gets the full context. If it can't, the stub at least tells it where to look, and most modern agents will read the referenced file.

### Kiro's Special Case

Kiro (both the IDE and the forthcoming `kiro-cli`) has a genuinely useful feature here. Its steering files support a file inclusion directive:

**.kiro/steering/project-context.md:**
```markdown
---
inclusion: auto
---

#[[file:AGENTS.md]]
```

The `inclusion: auto` frontmatter means this loads on every session. The `#[[file:AGENTS.md]]` directive injects the full content of AGENTS.md directly into Kiro's context — no cross-referencing, no hoping the agent follows a pointer. The content is there, guaranteed, every time.

This is the closest any agent comes to solving the problem cleanly. The `.kiro/steering/` directory is shared between the IDE and CLI, so the same context file works for both. The others still rely on the agent being smart enough to read a referenced file.

## What Goes in AGENTS.md

The content matters as much as the structure. After iterating on this during real implementation work, here's what proved essential:

### 1. Environment Details That Prevent Wasted Cycles

```markdown
### Important: Shell Execution
- Shell commands must run in a Linux context (bash/zsh), not PowerShell
- `dotnet` is not available locally — do not attempt local builds
- Use `gh` CLI for GitHub API access (runs, PRs, issues)
```

This saved me repeated failures. Kiro's shell execution was trying to run `dotnet build` in a context where the SDK wasn't installed, and it took multiple sessions to diagnose because the context reset each time. Once this was in AGENTS.md, every agent knew immediately: don't try local builds, push and check CI instead.

### 2. API-Specific Gotchas

```markdown
### Removed/Changed APIs
- **`IServerEntryPoint`** — Removed in 10.11. Use `IHostedService` instead.
- **`MediaType`** — Now in `MediaBrowser.Model.Entities`.
- **`TaskTriggerInfo.TriggerDaily`** — Use the string `"DailyTrigger"`.
```

This is the highest-value content in the file. Without it, every agent independently discovers these breaking changes by writing code that fails CI, reading the error, and fixing it — three round-trips per issue, per session. With it, the agent writes correct code on the first attempt.

### 3. Correct Patterns (Not Just What's Wrong)

```csharp
// Scheduled task triggers
new TaskTriggerInfo { Type = "DailyTrigger", TimeOfDayTicks = TimeSpan.FromHours(3).Ticks }
```

Don't just say what's broken — show what's correct. Agents are better at copying patterns than inferring fixes from error descriptions.

### 4. Build Verification Workflow

```markdown
Since `dotnet` is not installed locally, all build verification happens via CI:
1. Push changes to GitHub
2. Check workflow status: `GH_PAGER=cat gh run list --limit 3`
3. View errors: `GH_PAGER=cat gh run view <run-id> --log-failed 2>&1 | grep "error CS"`
```

This tells the agent how to close the feedback loop. Without it, the agent pushes code and considers the task done. With it, the agent knows to check CI and iterate.

## What I Left Out

Equally important: the stub files contain zero details that could go stale. My earlier article suggested keeping a "quick reference" in CLAUDE.md with build commands and key conventions. I tried that initially and removed it within a day.

The problem: when you update AGENTS.md (adding a new API note, fixing a path), you forget to update the duplicated snippets in CLAUDE.md. Now Claude Code has stale context that contradicts the canonical source. The whole point of centralization is defeated the moment you duplicate anything.

One line. One reference. No details in the stubs.

## Does Cross-Referencing Actually Work?

In my earlier article, I was skeptical about cross-referencing — telling one agent to read a competitor's files. Two months later, the landscape has improved:

- **Claude Code**: Reliably reads referenced files. `CLAUDE.md` saying "read AGENTS.md" works.
- **Kiro**: File inclusion directive guarantees the content is loaded. Best solution of any agent.
- **GitHub Copilot**: Reads `.github/copilot-instructions.md` content but does not follow file references within it. However, since AGENTS.md is in the repo, Copilot's workspace indexing picks it up for chat context.
- **Gemini** (`agy` CLI): Reads `.gemini/styleguide.md` and follows file references. Google's tooling respects the pointer pattern.
- **Codex**: Auto-discovers AGENTS.md by convention. No pointer needed.

The pattern works today in mid-2026 in a way it wouldn't have six months ago. Agents are better at following references, and workspace-level indexing means the canonical file gets picked up even without explicit inclusion.

## Lessons Learned

**1. Context persistence is the real problem, not context format.**

I spent time in my earlier articles comparing file formats (MDC vs Markdown, YAML vs prose). That doesn't matter. What matters is: does the agent have the right information when it starts working? AGENTS.md solves that regardless of format differences.

**2. API breakage documentation is the highest-ROI content.**

Of everything in AGENTS.md, the Jellyfin 10.11 API notes save the most time. Environment details are a close second. General coding standards (XML docs, ConfigureAwait) are nice-to-have but agents mostly infer those from existing code.

**3. One file, one truth, no duplication.**

Every time I was tempted to put "just a few key points" in a stub file, I reminded myself: that's how drift starts. The stubs are pointers, not summaries.

**4. The name `AGENTS.md` is a pragmatic choice, not a standard.**

There is still no cross-agent standard. `AGENTS.md` works because Codex reads it natively and the name is self-documenting. But if the ecosystem converges on something else tomorrow, the migration is trivial — rename one file, update four one-liners.

## The Repository

The full implementation is at [github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner](https://github.com/mcgarrah/jellyfin-plugin-media-integrity-scanner). The `feat/agent-context-files` branch contains the agent context setup described here.

## Reality Check: Kiro CLI Is Broken for Enterprise Auth

While the `.kiro/steering/` file inclusion works beautifully in the Kiro IDE, `kiro-cli` — the terminal-based agent — is currently unusable with IAM Identity Center (organization-managed) authentication. I spent hours debugging this and [filed the issue](https://github.com/kirodotdev/Kiro/issues/10587).

The symptoms: `kiro-cli chat` exits silently. No error, no output, exit code 0. Authentication works (`whoami` succeeds, `chat --list-models` returns models), but the chat subprocess never starts. Debug output reveals the problem:

```
no social token found
no idp token found
launching q chat binary
```

The chat subprocess only accepts "social" tokens (Google/GitHub login) or "idp" tokens (Okta/Entra). IAM Identity Center SSO tokens — the enterprise auth path — are simply not handled. The Kiro IDE works fine with the same credentials because it handles auth internally rather than delegating to a subprocess.

This is frustrating for two reasons:

**1. The CLI was closed-source in the transition.** Amazon Q Developer CLI was open source on GitHub. When it was rebranded to Kiro CLI, the repository was archived and the new codebase is proprietary. I can't look at the token-passing code to understand the issue or propose a fix. The debug output (`q_cli::cli`, `launching q chat binary`) reveals the old Q Developer internals are still under the hood — this is a rebrand, not a rewrite — but I can't inspect them anymore.

**2. Builder ID works, enterprise auth doesn't.** The irony of a tool marketed for enterprise adoption failing on the enterprise authentication path while working fine with personal Builder ID login is not lost on me. If you're evaluating Kiro CLI for an organization that uses IAM Identity Center, be aware that chat functionality doesn't work as of version 2.15.2.

For now, my `.kiro/steering/project-context.md` file delivers value through the Kiro IDE (where it works as designed) and awaits a fix for the CLI. The context file pattern is correct — the tooling has a gap.

## Related Articles

- [Managing Context and Rules Across Multiple AI Coding Assistants](/managing-cross-ai-agent-context/) — The strategy article that preceded this implementation
- [AI Coding Agent Context Files: A Reference Guide](/ai-coding-agent-context-files-reference/) — Detailed reference for each agent's file format and conventions

## Series Context

This article is part of the [Jellyfin Media Integrity Scanner](/jellyfin-media-integrity-scanner-introduction/) development series, though it stands alone as a practical guide to AI agent context management applicable to any project.
