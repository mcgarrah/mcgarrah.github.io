---
title: "Jekyll Run Plugin: Patching the Source and Submitting a PR"
layout: post
categories: [web-development, technical, jekyll]
tags: [jekyll, vscode, plugin-bug, open-source, pull-request, typescript, vscode-extension]
excerpt: "The Jekyll Run VS Code extension has two bugs that have gone unfixed for five years: an unscoped getConfiguration() call that breaks multi-root workspaces, and a null rejection in the error handler that swallows real errors. Here's the three-file fix, how to build and test it locally, and the options for getting it published."
description: "A walkthrough of fixing two bugs in the Jekyll Run VS Code extension source code. Covers the getConfiguration() scoping issue, the null error handler crash, building the extension from source, testing the fix, and the decision between submitting a PR to the abandoned upstream or forking and publishing independently."
date: 2026-05-25
last_modified_at: 2026-05-25
published: true
seo:
  type: BlogPosting
  date_published: 2026-05-25
  date_modified: 2026-05-25
---

In the [previous post](/jekyll-run-plugin-multiroot-workspace-bug/), I traced the `TypeError: Cannot read properties of null` crash in the Jekyll Run VS Code extension to its root causes: macOS GUI PATH inheritance and two bugs in the plugin's source code. The workaround — rbenv with Ruby 3.3 and launching VS Code from a terminal — works, but the plugin bugs are still there waiting to bite someone else.

This post covers the actual code fixes, how to build and test the patched extension, and the options for getting the fix published: PR to the original repository, or fork and publish independently.

<!-- excerpt-end -->

## The Three Bugs

### Bug 1: Unscoped getConfiguration() Call

In `src/config/config.ts`, the plugin reads VS Code settings using an unscoped API call:

```typescript
export class Config {
    static get(extension = 'jekyll-run') {
        return vscode.workspace.getConfiguration().get(extension) as any;
    }
}
```

`getConfiguration().get('jekyll-run')` fetches the entire root configuration object and extracts the `jekyll-run` key. In multi-root workspaces, this can return `null` — bypassing all settings sources and the defaults declared in `package.json`.

The VS Code API documentation [recommends](https://code.visualstudio.com/api/references/vscode-api#workspace.getConfiguration) passing the section name directly: `getConfiguration('jekyll-run')`. This returns a `WorkspaceConfiguration` object that properly resolves defaults, merges settings from all sources, and never returns `null` for declared properties.

### Bug 2: Null Rejection in Error Handler

In `src/cmds/run.ts`, the stderr handler tries to extract an Errno message when the error contains "ruby":

```typescript
child.stderr.on('data', (data) => {
    var error = data.toString();
    if (error.includes('Error') || error.includes('argument')) {
        reject(data);
    }
    if (error.includes('ruby')) {
        reject(error.match(/\B(.+)Errno(.+)/m));
    }
});
```

If the Ruby error doesn't contain "Errno" (which is most Ruby errors — bundler version mismatches, gem not found, syntax errors), `match()` returns `null`. The plugin calls `reject(null)`, and the caller in `extension.ts` does:

```typescript
var strString = error.toString().split('\n')[0];
```

`null.toString()` — TypeError. The real error is swallowed. The user sees a cryptic crash instead of "Could not find bundler 4.0.8" or whatever the actual problem was.

### Bug 3: Port-in-Use Detection Fails on macOS

When a Jekyll server is already running on port 4000 (from a terminal session, for example), clicking Jekyll Run should detect the conflict and show a helpful message. Instead, the plugin launches a second Jekyll process that crashes on the port conflict, and the user sees a thread exception popup from livereload:

```
#<Thread:0x0000000126cc9a58 .../live_reload_reactor.rb:39 run> terminated with exception
```

The plugin has port-checking code that runs `lsof -i tcp:4000` and parses the output. But the parser is broken on macOS. It splits the `lsof` output on single spaces:

```javascript
var splittedOutput = output.split('\n')[1].split(' ');
processOnPort.name = splittedOutput[0];
processOnPort.pid = +splittedOutput[1];
```

The problem is that `lsof` uses variable-width columns with multiple spaces:

```
COMMAND   PID             USER   FD   TYPE ...
ruby    20545 michael.mcgarrah    6u  IPv4 ...
```

Splitting on a single space produces empty strings between fields: `["ruby", "", "", "", "20545", ...]`. So `splittedOutput[1]` is `""`, not `"20545"`. The PID parses as `0`, and the plugin concludes the port is free.

## The Fix

Three files for the configuration and error handling bugs, plus one file for the port detection bug.

### src/config/config.ts

```typescript
import * as vscode from 'vscode';

export class Config {
    static get(extension = 'jekyll-run') {
        return vscode.workspace.getConfiguration(extension);
    }
}
```

Pass the section name directly to `getConfiguration()`. This returns a `WorkspaceConfiguration` proxy that resolves defaults and merges settings correctly in all workspace types.

### src/cmds/run.ts

```diff
     child.stderr.on('data', (data) => {
         var error = data.toString();
         if (error.includes('Error') || error.includes('argument')) {
             console.log('stderr: ' + data);
             this.regenerateStatus.hide();
             reject(data);
         }
         if (error.includes('ruby')) {
             console.log('stderr: ' + data);
             this.regenerateStatus.hide();
-            reject(error.match(/\B(.+)Errno(.+)/m));
+            reject(error.match(/\B(.+)Errno(.+)/m) || error);
         }
     });
```

Fall back to the full error string when the Errno regex doesn't match. The user sees the actual Ruby error instead of a null crash.

### src/extension.ts

```diff
 function getConfigFromArgs() {
     const config = Config.get();
-    const args = config.commandLineArguments.toString();
+    const args = (config.commandLineArguments || '').toString();
     const m_port = args.match(/\B(-P|--port)\s(\d+)\b/);
```

Defensive null guard. Even with the `config.ts` fix, this prevents a crash if `commandLineArguments` is ever undefined.

### src/utils/process-on-port.ts

```diff
-            var splittedOutput = output.split('\n')[1].split(' ');
-            processOnPort.name = splittedOutput[0];
-            processOnPort.pid = +splittedOutput[1];
+            var splittedOutput = output.split('\n')[1].split(/\s+/).filter(Boolean);
+            processOnPort.name = splittedOutput[0];
+            processOnPort.pid = +splittedOutput[1];
```

Split on one-or-more whitespace characters (`/\s+/`) and filter empty strings. Now `splittedOutput[1]` is the actual PID regardless of column spacing.

## Building from Source

The plugin uses TypeScript compiled to JavaScript. The compiled output lives in `out/`.

### Prerequisites

```bash
git clone https://github.com/mcgarrah/jekyll-run.git
cd jekyll-run
npm install
```

### Apply the Fixes

Edit the three files listed above, then compile:

```bash
npm run compile
```

This runs `tsc -p ./` and outputs to `out/`. The compiled JavaScript in `out/config/config.js`, `out/cmds/run.js`, and `out/extension.js` will reflect your changes.

### Test Locally

Copy the compiled output to your VS Code extensions directory:

```bash
# macOS / Linux
cp -r out/ ~/.vscode/extensions/dedsec727.jekyll-run-1.7.0/out/

# WSL2
cp -r out/ ~/.vscode-server/extensions/dedsec727.jekyll-run-1.7.0/out/
```

Reload VS Code (`Cmd+Shift+P` → "Developer: Reload Window") and test the Jekyll Run button in a multi-root workspace.

### Package as VSIX

To create an installable extension package:

```bash
npm install -g @vscode/vsce
vsce package
```

This produces a `.vsix` file you can install with:

```bash
code --install-extension jekyll-run-1.7.1.vsix
```

## Publishing Options

The original repository ([Kanna727/jekyll-run](https://github.com/Kanna727/jekyll-run)) hasn't been updated since 2020. The last commit was five years ago. There are open issues with no responses.

### Option 1: Submit a PR

The respectful first step. Fork the repository, apply the fixes, and submit a pull request.

```bash
# Fork on GitHub, then:
git clone https://github.com/mcgarrah/jekyll-run.git
cd jekyll-run
git checkout -b fix/multiroot-workspace-null-crash

# Apply fixes to the three files
# ...

git add -A
git commit -m "fix: handle null config in multi-root workspaces and fix port detection

- Use getConfiguration(section) instead of getConfiguration().get(section)
  to properly resolve settings and defaults in multi-root workspaces
- Fall back to full error string when Errno regex doesn't match stderr,
  preventing null rejection that crashes the error handler
- Add defensive null guard on commandLineArguments access
- Fix lsof output parsing on macOS by splitting on whitespace regex
  instead of single space, which failed due to variable-width columns"

git push origin fix/multiroot-workspace-null-crash
```

Then open a PR on GitHub. If the maintainer is active, this is the cleanest path.

**Risk:** The repository appears abandoned. The PR may never be reviewed.

### Option 2: Fork and Publish

If the PR sits for a reasonable period (30-60 days), fork and publish under a new name on the VS Code Marketplace.

The extension is licensed under MIT, so forking and republishing is explicitly permitted.

Steps:

1. Fork the repository
2. Apply the fixes
3. Update `package.json`:
   - Change `name` to avoid conflicts (e.g., `jekyll-run-fixed`)
   - Change `publisher` to your VS Code Marketplace publisher ID
   - Bump `version` to `1.8.0`
   - Update `description` to note it's a maintained fork
   - Add a note in `README.md` crediting the original author
4. Create a VS Code Marketplace publisher account if you don't have one
5. Package and publish:

```bash
vsce package
vsce publish
```

### Option 3: Patch in Place

The approach documented in the [Amazon Q rules](/jekyll-run-plugin-multiroot-workspace-bug/) — edit the compiled JavaScript directly in the extension directory. No publishing, no fork, but the patch is overwritten on extension updates.

This is what I'm currently doing. It's the fastest path but the least durable.

## Dependency Concerns

The plugin's `package.json` has outdated dependencies:

```json
{
    "typescript": "^3.8.3",
    "vscode-test": "^1.3.0",
    "@types/vscode": "^1.18.0"
}
```

TypeScript 3.8 is from 2020. The VS Code API types target 1.18 (from 2017). These work but are far behind current versions. A thorough fork would update these, but for a minimal bug fix PR, it's better to keep the dependency changes out of scope.

## What I'm Doing

1. **Immediate:** Using rbenv + terminal launch (no plugin patches needed)
2. **Next:** Submitting a PR to the original repository with the three-file fix
3. **If no response in 60 days:** Forking and publishing as a maintained version

The PR is the right first step. The original author built a useful extension that thousands of people use. If they're still around, they deserve the chance to merge the fix. If not, the MIT license exists for exactly this situation.

## Related Posts

- [Jekyll Run Plugin: Local Development Settings That Actually Work](/jekyll-run-vscode-plugin-local-development/) — Complete configuration guide
- [Jekyll Run Plugin: Fixing the Multi-Root Workspace Crash](/jekyll-run-plugin-multiroot-workspace-bug/) — The macOS debugging story and rbenv solution

## References

- [Jekyll Run Source Code](https://github.com/Kanna727/jekyll-run) — Original GitHub repository
- [Jekyll Run Extension](https://marketplace.visualstudio.com/items?itemName=Dedsec727.jekyll-run) — VS Code Marketplace
- [VS Code Extension Publishing](https://code.visualstudio.com/api/working-with-extensions/publishing-extension) — Official guide
- [vsce CLI](https://github.com/microsoft/vscode-vsce) — VS Code Extension Manager
- [VS Code getConfiguration API](https://code.visualstudio.com/api/references/vscode-api#workspace.getConfiguration) — API documentation
