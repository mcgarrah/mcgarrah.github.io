---
title: "MCP vs CLI vs API: Access Patterns for AI Coding Agents"
layout: post
categories: [technical, devtools]
tags: [mcp, kiro, ai agents, cli, api, developer tools, automation, model context protocol]
excerpt: "AI coding agents can interact with external systems through three patterns: MCP servers, CLI tools, and direct API calls. Each has different tradeoffs around setup effort, approval granularity, agent reliability, and coverage. Here's how to choose."
description: "A comparison of the three access patterns available to AI coding agents — MCP (Model Context Protocol) servers, CLI tools, and direct HTTP API calls — covering setup effort, approval control, agent reliability, coverage breadth, and when to use each pattern."
date: 2026-06-01
last_modified_at: 2026-06-01
published: false
seo:
  type: BlogPosting
  date_published: 2026-06-01
  date_modified: 2026-06-01
---

AI coding agents like Kiro, Cursor, and Claude Code can interact with external systems — issue trackers, cloud providers, observability platforms, source control — through three distinct patterns. Each has different tradeoffs, and most productive setups use a mix of all three.

<!-- excerpt-end -->

## The Three Patterns

### MCP Servers (Model Context Protocol)

An MCP server is a purpose-built integration that exposes a set of structured tools to the agent. The agent calls named functions with typed parameters and gets structured responses back.

**How it works:** A server process (local or remote) registers tools with the IDE. The agent sees a catalog of available actions (e.g., `searchIssues`, `getPage`, `getCostAndUsage`) and invokes them by name with specific parameters.

**Example — querying an issue tracker:**

```
Agent calls: searchIssues(jql="project = OPS AND status = Open", maxResults=10)
Returns: structured JSON with issue keys, summaries, statuses
```

**Example — querying cloud costs:**

```
Agent calls: get_cost_and_usage(start_date="2026-04-01", end_date="2026-05-01", granularity="MONTHLY", metrics=["UnblendedCost"])
Returns: structured cost data by service
```

| Aspect | Detail |
|--------|--------|
| Setup | Configure in settings file — specify command, args, env vars |
| Auth | Varies by server — env vars, cloud profiles, OAuth flows |
| Approval control | Per-tool granularity — can auto-approve reads, block writes |
| Output | Structured (JSON) — agent doesn't need to parse text |
| Coverage | Limited to what the MCP server exposes |

### CLI Tools (Shell Access)

The agent can run shell commands directly through its terminal tool. This gives access to any CLI installed on your machine — AWS CLI, git, kubectl, glab, curl, jq, Python scripts, etc.

**How it works:** The agent constructs a shell command, the IDE prompts for approval (unless in autopilot), executes it, and the agent reads the text output.

**Example — querying cloud costs:**

```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-04-01,End=2026-05-01 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --profile my-profile \
  --region us-east-1
```

**Example — querying issues:**

```bash
glab issue list --project OPS --state opened --per-page 10
```

| Aspect | Detail |
|--------|--------|
| Setup | None beyond having the CLI installed and authenticated |
| Auth | Whatever credentials the CLI is configured with (profiles, tokens, env vars) |
| Approval control | Binary — approve or deny the entire command. No per-flag granularity. |
| Output | Text (often JSON, but the agent must parse it) |
| Coverage | Anything with a CLI — broadest coverage of any pattern |

### Direct API Calls (HTTP/fetch)

The agent can make HTTP requests directly using fetch tools or curl commands. This works for any service with a REST API, even if no MCP or CLI exists for it.

**How it works:** The agent constructs an HTTP request (URL, headers, body), executes it, and parses the response.

**Example — querying a monitoring platform:**

```bash
curl -s -X POST 'https://api.monitoring.example.com/graphql' \
  -H "API-Key: $API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"query":"{account(id:12345){nrql(query:\"SELECT count(*) FROM Transaction SINCE 1 day ago\"){results}}}"}'
```

**Example — querying a REST API:**

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  'https://api.example.com/v1/resources?limit=10'
```

| Aspect | Detail |
|--------|--------|
| Setup | None — works immediately if you have credentials |
| Auth | Manual — agent must include auth headers, tokens, or query params |
| Approval control | Same as CLI — approve or deny the entire request |
| Output | Raw HTTP response — agent parses JSON/XML/text |
| Coverage | Anything with an HTTP API — universal |

## Comparison

|  | MCP Server | CLI | Direct API |
|--|-----------|-----|------------|
| **Structure** | High — typed tools, named parameters | Medium — flags and args, text output | Low — raw HTTP, manual everything |
| **Setup effort** | Moderate — configure settings, install server | Low — just need the CLI installed | None |
| **Approval granularity** | Per-tool (can auto-approve reads, block writes) | Per-command (all or nothing) | Per-request (all or nothing) |
| **Coverage** | Limited to exposed tools | Broad — anything with a CLI | Universal — anything with an HTTP endpoint |
| **Error handling** | Structured errors from the server | Exit codes + stderr text | HTTP status codes + response body |
| **Agent reliability** | Higher — less room for malformed calls | Medium — can construct bad flags | Lower — must get URL, headers, body all correct |
| **Discoverability** | Agent sees available tools and their schemas | Agent must know (or guess) the right command | Agent must know the API contract |

## Available Integrations by Service

What's typically available for common infrastructure and development services:

| Service | MCP | CLI | API |
|---------|-----|-----|-----|
| **Jira / Confluence** | Atlassian MCP (vendor-native) | — | REST API v3 (Jira), REST API v1 (Confluence) |
| **AWS (general)** | AWS Documentation MCP (read-only) | Full AWS CLI (`aws <service>`) | All AWS service APIs |
| **AWS Cost Explorer** | AWS Billing MCP (vendor-native) | `aws ce` CLI | Cost Explorer API |
| **AWS Athena** | AWS Data Platform MCP (vendor-native) | `aws athena` CLI | Athena API |
| **New Relic** | New Relic MCP (vendor-native) | — | NerdGraph GraphQL API |
| **Wiz** | Wiz MCP (vendor-native) | — | Wiz GraphQL API |
| **Git / GitLab** | GitLab MCP | `git`, `glab` CLI | GitLab REST API |
| **GitHub** | GitHub MCP | `git`, `gh` CLI | GitHub REST/GraphQL API |
| **Kubernetes** | — | `kubectl`, `helm` | Kubernetes API |
| **Terraform** | Terraform MCP (vendor-native) | `terraform` CLI | Terraform Cloud API |

**Legend:**
- *Vendor-native* — published and maintained by the service vendor
- *Remote* — MCP server hosted by vendor, connected via mcp-remote or direct URL
- *Local* — MCP server runs on your machine via uvx/npx, proxies to external APIs
- *—* — no established option in this pattern (though you can always fall back to API)

## Mixing Patterns

These aren't mutually exclusive. A typical workspace might use:

- **Atlassian MCP** for Jira and Confluence (frequent, structured, benefits from tool-level approvals)
- **AWS CLI** for ad-hoc AWS queries (broad coverage, easy to add `--profile` and `--region`)
- **curl/fetch** for a one-off internal API call (not worth setting up an MCP for a single request)

The choice often comes down to: how often will you do this, and how much do you care about approval granularity?

## When to Use Each Pattern

**Use MCP when:**
- You interact with the service multiple times per session
- You want per-tool approval control (auto-approve reads, require approval for writes)
- The service has a vendor-published MCP server
- You want the agent to discover available actions without you specifying them

**Use CLI when:**
- You already have the CLI installed and authenticated
- You need broad coverage across many subcommands
- The interaction is ad-hoc or exploratory
- You're comfortable reviewing full commands before approval

**Use Direct API when:**
- No MCP or CLI exists for the service
- It's a one-off request not worth configuring an integration for
- You need to hit an internal or custom endpoint
- You're prototyping before deciding whether to build an MCP server

## Security Considerations

All three patterns ultimately act through whatever credentials are available. The security model is the same regardless of pattern — the agent can only do what your credentials allow.

That said, the patterns differ in how visible and controllable the access is:

| Concern | MCP | CLI | Direct API |
|---------|-----|-----|------------|
| Can you see what's being accessed? | Yes — tool name and params shown | Yes — full command shown | Yes — full request shown |
| Can you scope approvals? | Per-tool | Per-command | Per-request |
| Can credentials leak into output? | Unlikely — server handles auth | Possible if echoed in command | Possible if included in request |
| Can you audit after the fact? | Tool call logs | Shell history | Shell history or fetch logs |

### Before enabling a new access pattern

A quick checklist regardless of which pattern you're using:

1. Is the source trusted (vendor-published MCP, official CLI, documented API)?
2. Do you understand what actions are available and what data is accessed?
3. Are credentials scoped to minimum required permissions?
4. Have you reviewed any auto-approve settings?
5. Is there a legitimate need for this integration in your workflow?

## Configuration Example: MCP Server

```json
{
  "mcpServers": {
    "aws-billing": {
      "command": "uvx",
      "args": ["awslabs.aws-billing-and-cost-management-mcp-server@latest"],
      "env": {
        "AWS_PROFILE": "my-profile",
        "AWS_REGION": "us-east-1"
      },
      "autoApprove": ["get_cost_and_usage", "get_cost_forecast"]
    }
  }
}
```

The `autoApprove` array is the key differentiator — you can let the agent run read-only cost queries without prompting, while still requiring approval for anything that modifies resources. CLI and API patterns don't offer this granularity.

## Related Posts

- [Managing Cross-AI Agent Context](/managing-cross-ai-agent-context/) — How context files and steering work across AI coding tools
- [AI Coding Agent Context Files Reference](/ai-coding-agent-context-files-reference/) — The configuration layer that sits above these access patterns
