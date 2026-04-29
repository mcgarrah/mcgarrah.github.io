---
title: "Run Jekyll: Bug Fixes and Code Review"
layout: post
categories: [web-development, technical]
tags: [jekyll, vscode, vscode-extension, typescript, bug-fix, code-review, security]
excerpt: "A deep code review of the Jekyll Run VS Code extension found 18 issues — 3 fixed in v1.7.1, 15 more waiting. From null rejections that swallow real errors to a boolean default that's secretly a truthy string, here's everything that's wrong and how to fix it."
description: "Comprehensive code review of the Jekyll Run VS Code extension. Documents 18 issues across the codebase: 3 bugs fixed in v1.7.1 (getConfiguration scoping, null error rejection, lsof parsing), plus 15 additional issues found in a deep review including double rejections, Buffer/string confusion, missing error context, and a boolean config default that's actually a truthy string."
date: 2026-06-19
last_modified_at: 2026-06-19
seo:
  type: BlogPosting
  date_published: 2026-06-19
  date_modified: 2026-06-19
---

The [Jekyll Run VS Code extension](https://github.com/Kanna727/jekyll-run) has been abandoned for five years. In the [previous post](/forking-jekyll-run-to-run-jekyll/), I covered forking the repository and modernizing the CI/CD infrastructure. This post covers the actual bugs — three fixed in v1.7.1, plus fifteen more found in a deep code review. This is the same pattern I'd apply when evaluating any third-party dependency for an engineering organization: you're not just fixing bugs, you're assessing technical debt and maintenance risk before deciding whether to adopt, fork, or replace.

<!-- excerpt-end -->

## Bugs Fixed in v1.7.1

These three bugs were the ones I hit personally. They're fixed in the [v1.7.1 release](https://github.com/mcgarrah/jekyll-run/releases/tag/v1.7.1).

### Bug 1: Unscoped getConfiguration() Call

**File:** `src/config/config.ts`
**Symptom:** `TypeError: Cannot read properties of null` in multi-root workspaces

```typescript
// BEFORE (broken)
return vscode.workspace.getConfiguration().get(extension) as any;

// AFTER (fixed)
return vscode.workspace.getConfiguration(extension);
```

`getConfiguration().get('jekyll-run')` fetches the root config and extracts a key. In multi-root workspaces, this returns `null` — bypassing all settings and defaults. The scoped `getConfiguration('jekyll-run')` properly resolves everything.

Also added a defensive null guard in `extension.ts`:

```typescript
const args = (config.commandLineArguments || '').toString();
```

### Bug 2: Null Rejection in Error Handler

**File:** `src/cmds/run.ts`
**Symptom:** TypeError instead of the actual Ruby error message

```typescript
// BEFORE (rejects with null when Errno not found)
reject(error.match(/\B(.+)Errno(.+)/m));

// AFTER (falls back to full error string)
reject(error.match(/\B(.+)Errno(.+)/m) || error);
```

Most Ruby errors don't contain "Errno" — bundler version mismatches, gem not found, syntax errors. The regex returns `null`, the caller does `null.toString()`, crash. The user never sees the real error.

### Bug 3: Port Detection Fails on macOS

**File:** `src/utils/process-on-port.ts`
**Symptom:** Plugin doesn't detect existing Jekyll server, launches a second one that crashes

```typescript
// BEFORE (fails on macOS variable-width lsof columns)
var splittedOutput = output.split('\n')[1].split(' ');

// AFTER (handles any whitespace)
var splittedOutput = output.split('\n')[1].split(/\s+/).filter(Boolean);
```

macOS `lsof` uses multiple spaces between columns. Splitting on single space produces empty strings, so the PID always parses as `0`.

## Deep Code Review: 15 Additional Issues

Beyond the three bugs I hit, a systematic review of the entire codebase found fifteen more issues.

### High Priority — Crashes or Silent Failures

#### 1. Double rejection in stderr handler

**File:** `src/cmds/run.ts` lines 65-74

Both `if(error.includes('Error'))` and `if(error.includes('ruby'))` can match the same stderr data (e.g., "Error loading ruby"). Both call `reject()`, but a Promise can only be rejected once — the second is silently swallowed.

```typescript
// BEFORE: two separate if blocks, both can fire
if (error.includes('Error') || error.includes('argument')) {
    reject(data);
}
if (error.includes('ruby')) {
    reject(error.match(/\B(.+)Errno(.+)/m) || error);
}

// FIX: use else if
if (error.includes('ruby')) {
    reject(error.match(/\B(.+)Errno(.+)/m) || error);
} else if (error.includes('Error') || error.includes('argument')) {
    reject(error);
}
```

#### 2. Raw Buffer passed to reject

**Files:** `src/cmds/run.ts` line 68, `src/cmds/build.ts` line 37

The `Error`/`argument` branch does `reject(data)` where `data` is a raw Buffer from the stream. The caller does `error.toString()` which works on Buffers but produces `[object Object]` on other types.

**Fix:** `reject(error)` — use the already-converted string.

#### 3. lsof crash on header-only output

**File:** `src/utils/process-on-port.ts` line 22

If `lsof` returns output but only the header row (no process line), `output.split('\n')[1]` is `undefined`, and `.split(/\s+/)` on `undefined` throws TypeError.

**Fix:** Check the second line exists before parsing:

```typescript
const lines = output.split('\n');
if (lines.length > 1 && lines[1].trim()) {
    var splittedOutput = lines[1].split(/\s+/).filter(Boolean);
    // ...
}
```

#### 4. install.ts rejects with no error information

**File:** `src/cmds/install.ts` line 31

```typescript
child.stderr.on('data', (data) => {
    console.log('stderr: ' + data);
    reject();  // no error passed — caller gets undefined
});
```

The caller does `error.toString()` on `undefined` — crash. **Fix:** `reject(new Error(data.toString()))`.

#### 5. runBundleInstall not async-aware

**File:** `src/extension.ts` lines 175-188

```typescript
function runBundleInstall(currWorkspace: WorkspaceFolder) {
    runButton?.hide();
    commands.executeCommand('setContext', 'isBuilding', true);
    const install = new Install();
    install.Install(currWorkspace.uri.fsPath, outputChannel).then(/* ... */);
    runButton?.show();  // runs immediately, not after install completes
    commands.executeCommand('setContext', 'isBuilding', false);  // same
}
```

The button state flickers because cleanup runs before the async operation completes. **Fix:** Move cleanup into `.finally()`.

#### 6. deactivate() has no error handling

**File:** `src/extension.ts` line 290

```typescript
export function deactivate() {
    const config = Config.get();  // may fail during teardown
    if (config.stopServerOnExit) {
        commands.executeCommand('jekyll-run.Stop');
    }
}
```

During VS Code shutdown, the workspace may already be torn down. **Fix:** Wrap in try-catch.

### Medium Priority — Robustness

#### 7. exec-cmd.ts swallows all errors

**File:** `src/utils/exec-cmd.ts` line 6

Every command failure returns the string `'error'` with no context. Callers can't distinguish "command not found" from "permission denied" from "timeout".

**Fix:** Return the actual error message: `resolve('error: ' + err.message)` or use a structured result.

#### 8. get-numbers-in-string.ts splits on single space

**File:** `src/utils/get-numbers-in-string.ts` line 3

Same pattern as the lsof bug. Used by `kill-process-children.ts` to parse `ps` output, which also uses variable-width columns.

**Fix:** `.split(/\s+/)` instead of `.split(' ')`.

#### 9. kill-process-children.ts doesn't await the kill

**File:** `src/utils/kill-process-children.ts` line 22

```typescript
var strPidToBeKilled = pidToBeKilled.join(' ');
executeCMD('kill -9 ' + strPidToBeKilled);  // no await
```

The function returns before the kill completes. The caller's `.finally()` may run before processes are dead.

**Fix:** `await executeCMD(...)`.

#### 10. Dead code: VS Code < 1.31 version check

**File:** `src/utils/open-in-browser.ts` line 4

```typescript
if (compareVersions.compare(version, '1.31', '<')) {
    commands.executeCommand('vscode.open', Uri.parse(url));
} else {
    env.openExternal(Uri.parse(url));
}
```

VS Code 1.31 was released in 2019. The extension requires >= 1.18. Any VS Code that can run this extension is past 1.31. The `compare-versions` dependency exists solely for this dead check.

**Fix:** Remove the check and the dependency. Just use `env.openExternal()`.

#### 11. pid-on-port.ts undefined array access

**File:** `src/utils/pid-on-port.ts` line 8

```typescript
resolve(getNumbersInString(output)[0]);  // can be undefined
```

If `netstat` returns output but no numbers are found, `[0]` is `undefined`.

**Fix:** `resolve(getNumbersInString(output)[0] || 0)`.

### Low Priority — Code Quality

#### 12. stopServerOnExit default is wrong type

**File:** `package.json`

```json
"jekyll-run.stopServerOnExit": {
    "type": "boolean",
    "default": "false"  // string, not boolean!
}
```

The string `"false"` is truthy in JavaScript. The server **always** stops on exit regardless of the user's setting. **Fix:** `"default": false`.

#### 13. Inline require

**File:** `src/extension.ts` line 62

```typescript
var read = require('read-yaml');
```

Should be a top-level import for consistency and tree-shaking.

#### 14. Duplicate error handlers

**File:** `src/extension.ts`

The `.then(rejection)` and `.catch()` handlers in the Run and Restart commands are identical copy-paste blocks (~15 lines each, repeated 4 times). **Fix:** Extract to a shared function.

#### 15. Commented-out code

**Files:** `src/utils/process-on-port.ts`, `src/utils/open-in-browser.ts`

Dead commented-out code from previous implementations. Should be removed — it's in git history if needed.

## Summary

| Severity | Fixed in v1.7.1 | Remaining | Total |
|----------|-----------------|-----------|-------|
| Critical (crashes) | 3 | 6 | 9 |
| Medium (robustness) | 0 | 5 | 5 |
| Low (code quality) | 0 | 4 | 4 |
| **Total** | **3** | **15** | **18** |

The `stopServerOnExit` bug (#12) is particularly sneaky — it's been silently broken since the extension was first published. Every user who set it to `false` has been ignored.

## Related Posts

- [Jekyll Run Plugin: Local Development Settings That Actually Work](/jekyll-run-vscode-plugin-local-development/) — Configuration guide
- [Jekyll Run Plugin: Fixing the Multi-Root Workspace Crash](/jekyll-run-plugin-multiroot-workspace-bug/) — macOS debugging story
- [Forking Jekyll Run: From Abandoned Plugin to Run Jekyll](/forking-jekyll-run-to-run-jekyll/) — CI/CD and publishing
- [Testing a VS Code Extension](/vscode-extension-testing-jekyll-run/) — Test harness and CI

## References

- [Run Jekyll Fork](https://github.com/mcgarrah/jekyll-run) — Maintained fork
- [v1.7.1 Release](https://github.com/mcgarrah/jekyll-run/releases/tag/v1.7.1) — Bug fix release with VSIX download
- [Jekyll Run Source Code](https://github.com/Kanna727/jekyll-run) — Original repository
- [VS Code getConfiguration API](https://code.visualstudio.com/api/references/vscode-api#workspace.getConfiguration) — API documentation
