---
layout: post
title: "AI Coding Agent Context Files: A Reference Guide"
categories: [technical, development]
tags: [ai, amazon-q, claude-code, github-copilot, cursor, windsurf, gemini, cline, aider, kiro, productivity, tooling]
excerpt: "A practical reference for the context and rules files used by every major AI coding assistant — Amazon Q, Claude Code, GitHub Copilot, Cursor, Windsurf, Gemini, Cline, Aider, and Kiro."
description: "Comprehensive reference documenting the exact file paths, formats, scoping rules, and exclusion mechanisms for context files across all major AI coding assistants."
date: 2026-05-27
last_modified_at: 2026-05-27
seo:
  type: BlogPosting
  date_published: 2026-05-27
  date_modified: 2026-05-27
---

Every AI coding assistant has its own way of reading project-level instructions. If you only use one tool, you learn its convention and move on. But if you work across multiple agents — or your team does — knowing exactly what each tool expects becomes essential.

This is a factual reference for the context and rules files used by every major AI coding assistant as of mid-2026. For strategies on managing these across tools, see the companion article [Managing Context and Rules Across Multiple AI Coding Assistants](/managing-cross-ai-agent-context/).

<!-- excerpt-end -->

## Quick Reference Table

| Agent | Context Location | Format | Auto-Loaded | Exclusions |
|-------|-----------------|--------|-------------|------------|
| Amazon Q | `.amazonq/rules/*.md` | Markdown | Yes | `.amazonq/rules/` scoping |
| Claude Code | `CLAUDE.md`, `.claude/` | Markdown | Yes | `.claude/settings.json` |
| GitHub Copilot | `.github/copilot-instructions.md` | Markdown | Yes | `.github/copilot-instructions.md` |
| Cursor | `.cursor/rules/*.mdc` | MDC (Markdown+frontmatter) | Configurable | `.cursorignore` |
| Windsurf | `.windsurf/rules/*.md` | Markdown | Configurable | `.windsurfignore` |
| Gemini Code Assist | `.gemini/styleguide.md` | Markdown | Yes | `.aiexclude` |
| Cline | `.clinerules`, `.cline/rules/*.md` | Markdown | Yes | `.clineignore` |
| Aider | `.aider.conf.yml` | YAML | Yes | `.aiderignore` |
| Kiro | `specs/`, steering hooks | Markdown specs | Yes | Spec-scoped |

## Amazon Q Developer

Amazon Q reads project rules from a `.amazonq/rules/` directory at the repository root. Every `.md` file in that directory (and subdirectories) is automatically loaded into context for every chat and inline request.

### File Structure

```
.amazonq/
└── rules/
    ├── coding-standards.md
    ├── project-context.md
    ├── git-credentials-context.md
    └── memory-bank/
        ├── guidelines.md
        ├── product.md
        ├── structure.md
        └── tech.md
```

### Key Behaviors

- **Auto-loaded**: All `.md` files under `.amazonq/rules/` are injected as implicit instructions on every request
- **No frontmatter required**: Files are plain Markdown
- **Subdirectories supported**: Organize rules into folders for clarity
- **Workspace-scoped**: Rules apply to the workspace root where `.amazonq/` lives
- **Multi-root workspaces**: Each workspace folder can have its own `.amazonq/rules/`
- **User-level prompts**: Personal saved prompts live in `~/.aws/amazonq/prompts/` and are referenced with `@prompt` in chat

### Exclusions

Amazon Q does not have a dedicated ignore file. It respects `.gitignore` for file discovery. You can scope what the agent sees by structuring your rules to tell it what to avoid.

### Example Rule File

```markdown
# Project Context

## Overview
This is a Jekyll blog hosted on GitHub Pages.

## Coding Standards
- Wrap JavaScript in IIFEs with strict mode
- Use const/let, never var
- Include YAML front matter in all content files

## Build Commands
- `bundle exec jekyll serve` for development
- `bundle exec jekyll build` for production
```

### Documentation

- [Amazon Q Developer customization](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/customizations.html)

---

## Claude Code (Anthropic)

Claude Code uses a `CLAUDE.md` file at the project root as its primary context mechanism. It also supports a `.claude/` directory for settings and additional configuration.

### File Structure

```
project-root/
├── CLAUDE.md              # Project-level instructions (committed)
├── .claude/
│   ├── settings.json      # Project settings (committed)
│   └── settings.local.json # Personal settings (gitignored)
└── ...
```

### Key Behaviors

- **Hierarchical loading**: Claude Code reads `CLAUDE.md` files from parent directories down to the current directory, merging them. A `CLAUDE.md` in your home directory applies to all projects
- **Auto-loaded**: The file is read automatically when Claude Code starts in a directory
- **Plain Markdown**: No special frontmatter or syntax required
- **Scoping levels**:
  - `~/CLAUDE.md` — Global, applies everywhere
  - `/path/to/project/CLAUDE.md` — Project-level
  - `/path/to/project/subdir/CLAUDE.md` — Subdirectory-level (additive)
- **Settings file**: `.claude/settings.json` controls permissions, allowed/denied tools, and trusted commands
- **Local overrides**: `.claude/settings.local.json` for personal preferences (add to `.gitignore`)

### Exclusions

Claude Code respects `.gitignore` by default. Additional exclusions can be configured in `.claude/settings.json`:

```json
{
  "permissions": {
    "deny": ["Bash(rm:*)", "Bash(sudo:*)"]
  }
}
```

### Example CLAUDE.md

```markdown
# CLAUDE.md

## Project Context
Jekyll blog with GitHub Pages hosting. Ruby 3.0+, Node.js 16+.

## Conventions
- YYYY-MM-DD format for post filenames
- All JavaScript in IIFEs with strict mode
- Front matter required on all content files

## Commands
- `bundle exec jekyll serve` — local dev
- `bundle exec jekyll build` — production build
- `npm audit` — security check

## Do Not
- Modify _site/ directory directly
- Remove existing test cases
- Use var in JavaScript
```

### Documentation

- [Claude Code overview](https://docs.anthropic.com/en/docs/claude-code/overview)
- [CLAUDE.md memory](https://docs.anthropic.com/en/docs/claude-code/memory)

---

## GitHub Copilot

GitHub Copilot reads repository-level custom instructions from a single file at `.github/copilot-instructions.md`. This applies to Copilot Chat in VS Code, Visual Studio, JetBrains IDEs, and GitHub.com.

### File Structure

```
.github/
└── copilot-instructions.md
```

### Key Behaviors

- **Single file**: One Markdown file, no directory of rules
- **Auto-loaded**: Automatically included as context for Copilot Chat when the setting `github.copilot.chat.codeGeneration.useInstructionFiles` is enabled (it is by default in recent versions)
- **Plain Markdown**: No special syntax or frontmatter
- **Chat-scoped**: Applies to Copilot Chat interactions, not inline completions (ghost text)
- **Repository-scoped**: One file per repository
- **Organization-level**: Enterprise customers can also set organization-wide instructions via GitHub settings
- **No subdirectory scoping**: Unlike Claude Code, there's no hierarchical merging

### Exclusions

Copilot respects a content exclusion policy configured at the organization or enterprise level in GitHub settings. There is no repository-level ignore file for Copilot specifically. It does respect `.gitignore` for file indexing.

### Example File

```markdown
# Copilot Instructions

## Language and Framework
This is a Ruby/Jekyll project. Prefer Ruby 3.0+ idioms.

## Code Style
- Use `const` and `let` in JavaScript, never `var`
- Wrap all JS in IIFEs with `'use strict'`
- Follow existing SCSS variable naming in `_sass/`

## Project Structure
- Blog posts go in `_posts/` with YYYY-MM-DD-title.md naming
- Custom plugins in `_plugins/` must set `safe true`
- Assets organized under `assets/` by type

## Testing
- Run `bundle exec jekyll build` to validate changes
- Check for broken links before committing
```

### Documentation

- [Copilot custom instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)

---

## Cursor

Cursor uses a `.cursor/rules/` directory with files in MDC format (Markdown with YAML frontmatter). The legacy `.cursorrules` file at the project root is still supported but deprecated.

### File Structure

```
.cursor/
└── rules/
    ├── general.mdc
    ├── python-style.mdc
    └── testing.mdc
```

Legacy (deprecated):
```
.cursorrules          # Single file, plain text/markdown
```

### Key Behaviors

- **MDC format**: Markdown files with YAML frontmatter that controls when and how rules are applied
- **Rule types** (set in frontmatter):
  - `always` — Loaded on every request
  - `auto` — Loaded when files matching a glob pattern are involved
  - `agent_requested` — Available for the agent to pull in when it decides it's relevant
  - `manual` — Only included when explicitly referenced by the user with `@rulename`
- **Glob patterns**: The `globs` frontmatter field specifies which files trigger `auto` rules
- **Description field**: A short description helps the agent decide whether to load `agent_requested` rules
- **User-level rules**: Global rules can be set in Cursor's settings (not file-based)

### MDC Frontmatter Example

```markdown
---
description: Python coding standards for this project
globs: "**/*.py"
alwaysApply: false
---

# Python Standards

- Use type hints on all function signatures
- Prefer pathlib over os.path
- Use virtual environments (.venv)
```

### Exclusions

Cursor uses `.cursorignore` at the project root, with `.gitignore` syntax:

```
# .cursorignore
node_modules/
.env
*.secret
vendor/
```

There is also `.cursorindexingignore` which only affects Cursor's codebase indexing but still allows the agent to read files if explicitly referenced.

### Documentation

- [Cursor rules](https://docs.cursor.com/context/rules)

---

## Windsurf (Codeium)

Windsurf uses a `.windsurf/rules/` directory structure similar to Cursor, plus a legacy `.windsurfrules` file.

### File Structure

```
.windsurf/
└── rules/
    ├── general.md
    └── python.md
```

Legacy:
```
.windsurfrules        # Single file at project root
```

### Key Behaviors

- **Markdown files**: Plain Markdown with optional YAML frontmatter for triggering rules
- **Rule types** (similar to Cursor):
  - `always` — Always included
  - `auto` — Triggered by file glob patterns
  - `manual` — Only when explicitly referenced
- **Glob-based activation**: Use `trigger` or `globs` in frontmatter
- **Global rules**: User-level rules configured in Windsurf settings
- **Cascade integration**: Rules feed into Windsurf's Cascade AI flow system

### Exclusions

Windsurf uses `.windsurfignore` with `.gitignore` syntax. It also respects `.gitignore`.

### Documentation

- [Windsurf rules](https://docs.windsurf.com/windsurf/customize/rules)

---

## Gemini Code Assist (Google)

Gemini Code Assist reads a style guide from `.gemini/styleguide.md` and supports a `GEMINI.md` file at the project root. It uses `.aiexclude` for file exclusions.

### File Structure

```
.gemini/
└── styleguide.md
```

Or:
```
GEMINI.md             # Project root alternative
```

### Key Behaviors

- **Auto-loaded**: The style guide is read automatically during Gemini interactions
- **Plain Markdown**: No special syntax
- **Single file focus**: Unlike Amazon Q's multi-file directory, Gemini expects one consolidated file
- **IDE integration**: Works in VS Code, JetBrains, and Cloud Workstations
- **Workspace-scoped**: Applies to the workspace where the file lives

### Exclusions

Gemini uses `.aiexclude` at the repository root with `.gitignore`-style syntax. This is a Gemini-specific mechanism that prevents the AI from reading or indexing matched files:

```
# .aiexclude
*.env
secrets/
*.pem
*.key
vendor/
```

This is separate from `.gitignore` — a file can be tracked in git but excluded from AI context.

### Example Style Guide

```markdown
# Style Guide

## General
- Follow Google's style guides for each language
- Use descriptive variable names
- Keep functions under 30 lines

## Jekyll Specific
- Front matter required on all posts
- Use excerpt separators for custom previews
- Organize assets by type under assets/
```

### Documentation

- [Gemini Code Assist customization](https://cloud.google.com/gemini/docs/discover/customize-gemini-code-assist)

---

## Cline

Cline (formerly Claude Dev) is an open-source VS Code extension that supports both a `.clinerules` file and a `.cline/rules/` directory.

### File Structure

```
.cline/
└── rules/
    ├── general.md
    └── testing.md
```

Or:
```
.clinerules           # Single file at project root
```

### Key Behaviors

- **Dual format**: Supports both single file and directory of rules
- **Auto-loaded**: Rules are included in every interaction
- **Plain Markdown**: No special frontmatter required
- **VS Code only**: Cline is a VS Code extension, not a standalone CLI
- **Model-agnostic**: Works with multiple LLM providers (Anthropic, OpenAI, etc.)
- **MCP support**: Cline supports Model Context Protocol servers for extended tool access

### Exclusions

Cline uses `.clineignore` with `.gitignore` syntax. It also respects `.gitignore`.

### Documentation

- [Cline documentation](https://docs.cline.bot/)

---

## Aider

Aider is an open-source CLI tool for AI pair programming. It uses YAML configuration files and a conventions system.

### File Structure

```
project-root/
├── .aider.conf.yml    # Project-level configuration
└── .aiderignore       # File exclusions
```

User-level:
```
~/.aider.conf.yml      # Global configuration
```

### Key Behaviors

- **YAML configuration**: Not Markdown — uses structured YAML for settings
- **Convention files**: You can specify convention/rules files via the `read` directive in config, which loads files as read-only context
- **CLI flags**: Most settings can also be passed as command-line arguments
- **Model-agnostic**: Works with OpenAI, Anthropic, local models, and others
- **Git-integrated**: Automatically commits changes with descriptive messages
- **Read-only context**: Use `--read` flag or `read` config to load reference files without allowing edits

### Configuration Example

```yaml
# .aider.conf.yml
model: claude-sonnet-4-20250514
auto-commits: true
read:
  - CONVENTIONS.md
  - docs/ARCHITECTURE.md
```

### Exclusions

Aider uses `.aiderignore` with `.gitignore` syntax:

```
# .aiderignore
*.min.js
vendor/
_site/
node_modules/
```

### Documentation

- [Aider configuration](https://aider.chat/docs/config.html)

---

## Amazon Kiro

Kiro is Amazon's successor to Amazon Q Developer as an IDE. It takes a fundamentally different approach — spec-driven development rather than rules files.

### File Structure

```
specs/
├── feature-name/
│   ├── requirements.md    # User stories and acceptance criteria
│   ├── design.md          # Technical design (auto-generated)
│   └── tasks.md           # Implementation tasks (auto-generated)
```

Steering hooks:
```
.kiro/
└── steering/
    ├── on-save.md         # Triggered on file save
    ├── on-commit.md       # Triggered on git commit
    └── custom-hook.md     # Custom automation triggers
```

### Key Behaviors

- **Spec-driven**: Instead of general rules, Kiro works from structured specifications
- **Three-phase workflow**: Requirements → Design → Tasks, each reviewed by the developer
- **Steering hooks**: Event-driven instructions that fire on specific IDE actions (save, commit, etc.)
- **Agent-native IDE**: Kiro is a full IDE (VS Code fork), not a plugin
- **Vibes mode**: Also supports freeform chat similar to other agents, where specs are optional

### How It Differs

Kiro's approach is less about "here are my coding standards" and more about "here is what I want built." The specs system replaces the rules-file pattern with a structured planning workflow. Steering hooks are the closest equivalent to rules files in other tools — they inject instructions at specific points in the development cycle.

### Documentation

- [Kiro documentation](https://kiro.dev/docs/)

---

## Comparison: Key Differences

### Context Loading

| Feature | Amazon Q | Claude Code | Copilot | Cursor | Gemini |
|---------|----------|-------------|---------|--------|--------|
| Multi-file rules | ✅ Directory | ❌ Single file | ❌ Single file | ✅ Directory | ❌ Single file |
| Hierarchical (parent dirs) | ❌ | ✅ | ❌ | ❌ | ❌ |
| Conditional loading (globs) | ❌ | ❌ | ❌ | ✅ | ❌ |
| User-level global rules | ✅ `~/.aws/amazonq/prompts/` | ✅ `~/CLAUDE.md` | ✅ Org-level | ✅ Settings | ❌ |
| Frontmatter/metadata | ❌ | ❌ | ❌ | ✅ Required | Optional |

### Exclusion Mechanisms

| Agent | Exclusion File | Syntax | AI-Specific |
|-------|---------------|--------|-------------|
| Amazon Q | `.gitignore` | gitignore | No (reuses git) |
| Claude Code | `.gitignore` + settings | gitignore + JSON | Partial |
| GitHub Copilot | Org-level policy | Admin UI | Yes |
| Cursor | `.cursorignore` | gitignore | Yes |
| Windsurf | `.windsurfignore` | gitignore | Yes |
| Gemini | `.aiexclude` | gitignore | Yes |
| Cline | `.clineignore` | gitignore | Yes |
| Aider | `.aiderignore` | gitignore | Yes |

### Format Summary

Most agents use plain Markdown. The outliers:
- **Cursor**: MDC format with YAML frontmatter (required for rule types and globs)
- **Aider**: YAML configuration file, not Markdown
- **Kiro**: Structured specs rather than freeform rules

## What's Missing from This Landscape

A few things stand out after surveying all of these:

- **No standard**: There is no cross-agent standard for AI context files. Every tool invented its own convention
- **No interoperability**: None of these tools read each other's files
- **Exclusions are fragmented**: Some use `.gitignore`, some have their own ignore files, some use admin policies
- **Model Context Protocol (MCP)**: MCP standardizes how agents connect to external tools and data sources, but it does not address project-level rules or coding conventions — that gap remains unfilled

The companion article [Managing Context and Rules Across Multiple AI Coding Assistants](/managing-cross-ai-agent-context/) covers strategies for dealing with this fragmentation.

## Revision History

- **2026-06-29**: Initial reference covering Amazon Q, Claude Code, GitHub Copilot, Cursor, Windsurf, Gemini Code Assist, Cline, Aider, and Kiro
